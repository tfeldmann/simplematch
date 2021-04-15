"""
easymatch
"""
import re

TYPES = {
    "int": (r"[+-]?0|[1-9][0-9]*", int),
    "float": (r"[+-]?([0-9]*[.])?[0-9]+", float),
}


def create_regex(pattern):
    result = (
        pattern.replace(".", r"\.")
        .replace("-", r"\-")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("*", r".*")
        .replace("?", r"\?")
        .replace("(", r"{")
        .replace(")", r"}")
    )
    result = re.sub(r"\{\.\*\}", r"(.*)", result)
    result = re.sub(r"\{([^\}]*)\}", r"(?P<\1>.*)", result)
    return result


def grouplist(match):
    # Used to extract only unnamed group matches.
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
        self.pattern = pattern
        self.regex = create_regex(pattern)
        self._regex = re.compile(self.regex)

    def test(self, string):
        match = self._regex.search(string)
        return match is not None

    def match(self, string):
        match = self._regex.search(string)
        if match:
            result = match.groupdict()
            for i, x in enumerate(grouplist(match)):
                result[i] = x
            return result
        return {}

    def __repr__(self):
        return '<Matcher("%s")>' % self.pattern


def test(pattern, string):
    return Matcher(pattern).test(string)


def match(pattern, string):
    return Matcher(pattern).match(string)


if __name__ == "__main__":
    m = Matcher("{year__int}")
    print(m.regex)
    print(m.match("2012"))
