"""
Inspired by https://www.npmjs.com/package/easypattern

Basic testings

var easyPattern = require("easyPattern");

var pattern = easyPattern("{file}.js");
pattern.test("archive.zip"); // false
pattern.test("index.js"); // true
Basic matching

var pattern = easyPattern("{folder}/{filename}.js");
var result = pattern.match("foo/bar.js");

//result = {folder: "foo", filename: "bar"}
Wildcard matching

var pattern = easyPattern("*.{extension}");
var result = pattern.match("/root/folder/file.exe");

//result = {extension:"exe"}
Advance matching

var pattern = easyPattern("{*}/{filename}?{*}");
var result = pattern.match("www.site.com/home/hello.js?p=1");

//result = {1:"www.site.com/home", 2:"p=1", filename:"hello.js"}


"""
import re


def create_regex(pattern):

    # .replace(\., "\\.")
    # .replace(\-, "\\-")
    # .replace(\[, "\\[")
    # .replace(\], "\\]")
    # .replace(\*\{, "*/{")
    # .replace(\*, ".*")
    # .replace(\?, "\\?")
    # .replace(\(, "{")
    # .replace(\), "}")
    # .replace(\{\.\*\}/g,"(.*)")
    # .replace(\{[^\}]*\}/g,"([^\/]+)");

    result = (
        pattern.replace(".", r"\.")
        .replace("-", r"\-")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("*{", r"*/{")
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
        self.source = pattern
        self.pattern = convert_to_regex(pattern)

    def __str__(self):
        return "Matcher(%s)" % self.source


def test(pattern, string):
    pass


def match(pattern, string):
    regex = create_regex(pattern)
    print(pattern + " -> " + regex)
    print(string)
    match = re.search(regex, string)
    if match:
        result = match.groupdict()
        for i, x in enumerate(grouplist(match)):
            result[i] = x
        print(result)
    print()


if __name__ == "__main__":
    pass
