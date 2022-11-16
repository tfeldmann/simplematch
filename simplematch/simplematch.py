"""
simplematch
"""
import re


class Environment:
    def __init__(self, block_start_string: str, block_end_string: str):
        # https://regex101.com/r/xS2B04/3
        safe_chars = r"[^:\[\]{}{}]".format(block_start_string, block_end_string)
        self.block_regex = re.compile(
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

    def parse(self, pattern: str):
        for x in self.block_regex.finditer(pattern):
            yield x.span(), x.group(), x.groups()


DEFAULT_ENV = Environment(block_start_string="<", block_end_string=">")


txt = """
    \{test}
    {test:test[123]}
    <temp:float> °C
    <  year :   int[max=4]>-<month: int[len=2]>-<day:int[max=2]>
    <:float>*<:float><:float[ len = 2, case_sensitive]>
    <:float>\*<name>*\<str>
    <planet><test:end>
    """

for x in DEFAULT_ENV.parse(txt):
    print(x)
