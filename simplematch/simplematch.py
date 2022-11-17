"""
simplematch
"""
import re
from typing import NamedTuple, Optional
from collections import defaultdict

from . import converters as cv


class Block(NamedTuple):
    name: Optional[str]
    converter: Optional[str]
    args: Optional[str]


def block_parser_regex(block_start_string: str = "<", block_end_string: str = ">"):
    """
    Assembles a regular expression which matches wildcards (`*`) and blocks
    in the form of

        `<name:converter[args]>`

    Block delimiters (`<` and `>`) can be changed via the `block_start_string` and
    `block_end_string` arguments.

    Matches have three captures: (`name`, `converter`, `args`).
    """
    # https://regex101.com/r/xS2B04/3
    safe_chars = r"[^:\[\]%s%s]" % (block_start_string, block_end_string)
    regex = re.compile(
        r"""
        (?<!\\)\*                 # match either an unescaped wildcard `*`
        |                         # or
        (?:                       # a converter definition
            (?<!\\)               # allow escaping the block start string
            {start}               # start block
            ({safe}+?)?           # the optional identifier name.
            (?:                   # make the converter part optional
                :                 # converter definition starts with `:`
                ({safe}+?)             # converter name
                (?:\[({safe}+?)\])?    # converter arguments
            )?                    # end of converter part
            {end}                 # end of block
        )
        """.format(
            start=block_start_string,
            end=block_end_string,
            safe=safe_chars,
        ),
        re.VERBOSE,
    )
    return regex


class Environment:
    converters = {
        "str": cv.Str,
        "int": cv.Int,
        "float": cv.Float,
        "decimal": cv.Decimal,
        "yyyy": cv.FourDigitYear,
        "letters": cv.Letters,
        "roman": cv.RomanNumeral,
        "bitcoin": cv.Bitcoin,
        "email": cv.Email,
        "url": cv.Url,
        "ipv4": cv.IpV4,
        "ipv6": cv.IpV6,
        "port": cv.Port,
        "mac": cv.MacAddress,
        "ssn": cv.SocialSecurityNumber,
        "cc": cv.CreditCard,
        "latlon": cv.LatLon,
        "semver": cv.SemanticVersion,
        "jira": cv.JiraIssueTicket,
        "hashtag": cv.Hashtag,
    }

    def __init__(
        self,
        block_start_string: str,
        block_end_string: str,
        unnamed_key: str,
    ):
        self.block_parser_regex = block_parser_regex(
            block_start_string=block_start_string,
            block_end_string=block_end_string,
        )
        self.unnamed_key = unnamed_key
        self._tmp_converters = defaultdict(list)

    def _replacer(self, match: re.Match) -> str:
        """
        This does two things:
        1. replaces a sm-syntax block with the regular expression given by the converter
        2. Adds the converter in the temporary list of converters
        """
        # strip whitespace from within the block
        name, _converter, _args = (
            x.strip() if x is not None else None for x in match.groups()
        )
        # handle wildcard (*)
        if name is _converter is _args is None:
            return r".*"
        converter = self.converters.get(_converter, cv.Str)()
        self._tmp_converters[name or self.unnamed_key].append(converter)
        return converter.regex

    def parse_pattern(self, pattern: str):
        self._tmp_converters.clear()
        result = self.block_parser_regex.sub(self._replacer, pattern)
        return result, dict(self._tmp_converters)


DEFAULT_ENV = Environment(
    block_start_string="<",
    block_end_string=">",
    unnamed_key="unnamed",
)


class Matcher:
    def __init__(
        self,
        pattern: str = "*",
        case_sensitive: bool = True,
        environment=DEFAULT_ENV,
    ):
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.environment = environment
        self.regex, self.converters = self.environment.parse_pattern(pattern)
        print("Regex: ", self.regex)
        print("Conve: ", self.converters)


Matcher("<temp : str><temp:float><temp:cc>*Test")
Matcher("<temp:float[something]> °C wheather <planet>")
Matcher("<:url><:url>")

# txt = """
#     \{test}
#     {test:test[123]}
#     <temp:float> °C
#     <  year :   int[max=4]>-<month: int[len=4]>-<day:int[max=2]>
#     <:float>*<:float><:float[ len = 2, case_sensitive]>
#     <:float>\*<name>*\<str>
#     <planet><test:end>
#     """

# for x in DEFAULT_ENV.parse(txt):
#     print(x)
