#!/usr/bin/env python3
"""
easymatch
"""
import json
import re
from argparse import ArgumentParser
from collections import namedtuple

Type = namedtuple("Type", "regex converter")

types = {
    "int": Type(regex=r"[+-]?0|[1-9][0-9]*", converter=int),
    "float": Type(regex=r"[+-]?(?:[0-9]*[.])?[0-9]+", converter=float),
    "email": Type(
        regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", converter=str
    ),
    "phone": Type(
        regex=r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}", converter=str
    ),
    "ssn": Type(
        regex=r"(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}", converter=str
    ),
    "ipv4": Type(
        regex=r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}",
        converter=str,
    ),
    "ipv6": Type(
        regex=r"(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))",
        converter=str,
    ),
}


def register_type(name, regex, converter=str):
    types[name] = Type(regex=regex, converter=converter)


_special_chars_map = {i: "\\" + chr(i) for i in b"()[]?*+-|^$\\.&~# \t\n\r\v\f"}


def grouplist(match):
    """ extract unnamed match groups """
    # https://stackoverflow.com/a/53385788/300783
    named = match.groupdict()
    ignored_groups = set()
    for name, index in match.re.groupindex.items():
        if name in named:  # check twice, if it is really the named attribute.
            ignored_groups.add(index)
    return [
        group for i, group in enumerate(match.groups()) if i + 1 not in ignored_groups
    ]


class Matcher:
    def __init__(self, pattern):
        self._converters = {}
        self.pattern = pattern

        # cache the compiled regex
        self.regex = self.create_regex(pattern)
        self._regex = re.compile(self.regex)

    def test(self, string):
        match = self._regex.match(string)
        return match is not None

    def match(self, string):
        match = self._regex.match(string)
        if match:
            # assemble result dict
            result = match.groupdict()
            for i, x in enumerate(grouplist(match)):
                result[i] = x

            # run converters
            for key, converter in self._converters.items():
                result[key] = converter(result[key])
            return result
        return {}

    def _field_repl(self, matchobj):
        # field with type annotation
        match = re.search(r"\{(\w+):(\w+)\}", matchobj.group(0))
        if match:
            name, type_ = match.groups()
            self._converters[name] = types[type_].converter
            return "(?P<%s>%s)" % (name, types[type_].regex)

        # field without type annotation
        match = re.search(r"\{(\w+)\}", matchobj.group(0))
        if match:
            name = match.group(1)
            return r"(?P<%s>.*)" % name

    def create_regex(self, pattern):
        # empty converters
        self._converters.clear()
        # escape some common characters
        result = (
            pattern.replace(".", r"\.")
            .replace("-", r"\-")
            .replace("[", r"\[")
            .replace("]", r"\]")
            .replace("*", r".*")
            .replace("?", r"\?")
            .replace("(", r"\(")
            .replace(")", r"\)")
            .replace("/", r"\/")
        )
        # handle named and wildcard matches
        result = re.sub(r"\{\.\*\}", r"(.*)", result)
        # result = re.sub(r"\{([^\}]*)\}", r"(?P<\1>.*)", result)
        result = re.sub(r"\{([^\}]*)\}", self._field_repl, result)
        return "^%s$" % result

        re.escape

    def __repr__(self):
        return '<Matcher("%s")>' % self.pattern


def test(pattern, string):
    return Matcher(pattern).test(string)


def match(pattern, string):
    return Matcher(pattern).match(string)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("string")
    args = parser.parse_args()
    print(json.dumps(Matcher(args.pattern).match(args.string)))
