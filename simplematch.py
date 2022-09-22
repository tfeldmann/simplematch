#!/usr/bin/env python3
"""
simplematch
"""
import datetime
import decimal
import re
import uuid
from collections import namedtuple

# taken from the standard re module - minus "*+?{}", because that's our own syntax
SPECIAL_CHARS = {i: "\\" + chr(i) for i in b"(){}-^$\\.&~# \t\n\r\v\f"}

# a regex that ensures all groups to be non-capturing. Otherwise they would appear in
# the matches
TYPE_CLEANUP_REGEX = re.compile(r"(?<!\\)\((?!\?)")

# `types` is the dict of known types that is filled with register_type
Type = namedtuple("Type", "regex converter")
types = {}


def register_type(name, regex, converter=str):
    """ register a type to be available for the {value:type} matching syntax """
    cleaned = TYPE_CLEANUP_REGEX.sub("(?:", regex)
    types[name] = Type(regex=cleaned, converter=converter)


# include some useful basic types
register_type("int", r"[+-]?[0-9]+", int)
register_type("float", r"[+-]?([0-9]*[.])?[0-9]+", float)
register_type("decimal", r"[+-]?([0-9]*[.])?[0-9]+", decimal.Decimal)
register_type("uuid", r"[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}", uuid.UUID)
register_type("date", r"\d{4}-\d{1,2}-\d{1,2}", datetime.date.fromisoformat)
register_type(
    "datetime",
    r"\d{4}-\d{1,2}-\d{1,2}"
    r"[T ]\d{1,2}:\d{1,2}"
    r"(?::\d{1,2}(?:[\.,]\d{1,6}\d{0,6})?)?"
    r"(Z|[+-]\d{2}(?::?\d{2})?)?",
    datetime.datetime.fromisoformat
)
register_type("letters", r"[^\d_\W]+")
register_type("identifier", r"\w+")

# found on https://ihateregex.io/
register_type("email", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
register_type(
    "ipv4",
    (
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]"
        r"?)){3}"
    ),
)
register_type(
    "url",
    (
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA"
        r"-Z0-9()!@:%_\+.~#?&\/\/=]*)"
    ),
)

register_type(
    # Visa, MasterCard, American Express, Diners Club, Discover, JCB
    "ccard",
    (
        r"(^4[0-9]{12}(?:[0-9]{3})?$)|(^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6]["
        r"0-9]{2}|27[01][0-9]|2720)[0-9]{12}$)|(3[47][0-9]{13})|(^3(?:0[0-5]|[68][0-9])"
        r"[0-9]{11}$)|(^6(?:011|5[0-9]{2})[0-9]{12}$)|(^(?:2131|1800|35\d{3})\d{11}$)"
    ),
)
register_type(
    "ipv6",
    (
        r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA"
        r"-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){"
        r"1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3"
        r"}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0"
        r"-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:"
        r"(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5"
        r"]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0"
        r"-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,"
        r"3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
    ),
)


class Matcher:
    def __init__(self, pattern="*", case_sensitive=True):
        self.converters = {}
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.regex = self._create_regex(pattern)

    def test(self, string):
        match = self._regex_compiled.match(string)
        return match is not None

    def match(self, string):
        match = self._regex_compiled.match(string)
        if match:
            # assemble result dict
            result = match.groupdict()
            for i, x in enumerate(self._grouplist(match)):
                result[i] = x

            # run converters
            for key, converter in self.converters.items():
                result[key] = converter(result[key])
            return result
        return None

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, value):
        self._regex = value
        flags = 0 if self.case_sensitive else re.IGNORECASE
        # cache the compiled regex
        self._regex_compiled = re.compile(value, flags=flags)

    def _create_regex(self, pattern):
        self.converters.clear()  # empty converters
        self._unnamed_group_index = 0
        wildcards = {
            "*": r".*",
            "+": r".",
            "?": r".?",
            "|": r"|",  # Not converted but can be escaped
        }

        result = pattern.translate(SPECIAL_CHARS)  # escape special chars

        for wildcard, actual in wildcards.items():
            not_escaped_pattern = fr"(?<!\[)\{wildcard}"
            escaped_pattern = fr"\[\{wildcard}]"
            result = re.sub(not_escaped_pattern, actual, result)
            result = re.sub(escaped_pattern, fr"\{wildcard}", result)
        result = re.sub(r"\[([^]]*)]", self._field_repl, result)  # handle groups
        return f"^{result}$"

    def _field_repl(self, match_obj):
        group_string = match_obj.group(0).replace("\ ", "")
        name_regex = r"(\w[\w\d_]*)"

        # unnamed field, just increase the index
        match = re.search(r"\[]", group_string)
        if match:
            self._unnamed_group_index += 1
            return r"(.*)"

        # unnamed field with only the type annotation
        match = re.search(fr"\[:{name_regex}]", group_string)
        if match:
            type_ = match.groups()[0]
            # register this field with the name of the type to convert it later
            self.converters[self._unnamed_group_index] = types[type_].converter
            self._unnamed_group_index += 1
            return fr"({types[type_].regex})"

        # field without type annotation
        match = re.search(fr"\[{name_regex}]", group_string)
        if match:
            name = match.group(1)
            return fr"(?P<{name}>.*)"

        # field with type annotation
        match = re.search(fr"\[{name_regex}:{name_regex}]", group_string)
        if match:
            name, type_ = match.groups()
            # register this field to convert it later
            self.converters[name] = types[type_].converter
            return fr"(?P<{name}>{types[type_].regex})"

    @staticmethod
    def _grouplist(match):
        """ Add unnamed match groups to the groupdict """
        # https://stackoverflow.com/a/53385788/300783
        named = match.groupdict()
        ignored_groups = set()
        for name, index in match.re.groupindex.items():
            if name in named:  # check twice if it is really the named attribute
                ignored_groups.add(index)
        return [
            group
            for i, group in enumerate(match.groups())
            if i + 1 not in ignored_groups
        ]

    def __repr__(self):
        return f'<Matcher("{self.pattern}")>'


def test(pattern, string, case_sensitive=True):
    return Matcher(pattern, case_sensitive=case_sensitive).test(string)


def match(pattern, string, case_sensitive=True):
    return Matcher(pattern, case_sensitive=case_sensitive).match(string)


def to_regex(pattern):
    return Matcher(pattern).regex


if __name__ == "__main__":
    import json
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("pattern", help="A matching pattern")
    parser.add_argument("string", help="The string to match")
    parser.add_argument(
        "--regex", action="store_true", help="Show the generated regular expression"
    )
    args = parser.parse_args()
    matcher = Matcher(args.pattern)
    print(json.dumps(matcher.match(args.string)))
    if args.regex:
        print("Regex:", matcher.regex)
