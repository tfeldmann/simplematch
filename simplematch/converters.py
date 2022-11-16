from decimal import Decimal


class Str:
    regex = r".*"

    def to_python(self, value: str) -> str:
        return value


class Int:
    regex = r"[+-]?[0-9]"

    def __init__(self, len=None, *, min=None, max=None):
        pass

    def to_python(self, value: str) -> int:
        return int(value)


class Float:
    regex = r"[+-]?([0-9]*[.])?[0-9]+"

    def to_python(self, value: str) -> float:
        return float(value)


class Decimal(Float):
    def to_python(self, value: str) -> Decimal:
        return Decimal(value)


class FourDigitYear(Int):
    regex = "[0-9]{4}"

    def to_python(self, value: str) -> int:
        return int(value)


class Letters(Str):
    regex = r"[a-zA-Z]+"


class RomanNumeral(Int):
    pass


class Bitcoin(Str):
    regex = r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}"


class Email(Str):
    regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


class Url(Str):
    regex = (
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b"
        r"([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)"
    )


class IpV4(Str):
    regex = (
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        r"(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
    )


class SocialSecurityNumber(Str):
    regex = r"(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}"
