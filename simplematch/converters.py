import decimal
from ipaddress import IPv4Address


class Str:
    regex = r".*"

    @staticmethod
    def to_python(value: str) -> str:
        return value


class Int:
    regex = r"[+-]?[0-9]"

    @staticmethod
    def to_python(value: str) -> int:
        return int(value)


class Float:
    regex = r"[+-]?([0-9]*[.])?[0-9]+"

    @staticmethod
    def to_python(value: str) -> float:
        return float(value)


class Decimal(Float):
    @staticmethod
    def to_python(value: str) -> decimal.Decimal:
        return decimal.Decimal(value)


class FourDigitYear(Int):
    regex = "[0-9]{4}"

    @staticmethod
    def to_python(value: str) -> int:
        return int(value)


class Letters(Str):
    regex = r"[a-zA-Z]+"


class RomanNumeral(Int):
    regex = r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"


class Bitcoin(Str):
    regex = r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}"


class Email(Str):
    regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


class Url(Str):
    regex = (
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b"
        r"([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)"
    )


class IpV4:
    regex = (
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        r"(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
    )

    def to_python(self, value) -> IPv4Address:
        return IPv4Address(value)


class IpV6:
    regex = (
        r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA"
        r"-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){"
        r"1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3"
        r"}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0"
        r"-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:"
        r"(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5"
        r"]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0"
        r"-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,"
        r"3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
    )


class Port:
    regex = (
        r"((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|"
        r"([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))"
    )


class MacAddress:
    regex = r"[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}"


class SocialSecurityNumber(Str):
    regex = r"(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}"


class CreditCard:
    regex = (
        r"(^4[0-9]{12}(?:[0-9]{3})?$)|(^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6]["
        r"0-9]{2}|27[01][0-9]|2720)[0-9]{12}$)|(3[47][0-9]{13})|(^3(?:0[0-5]|[68][0-9])"
        r"[0-9]{11}$)|(^6(?:011|5[0-9]{2})[0-9]{12}$)|(^(?:2131|1800|35\d{3})\d{11}$)"
    )


class LatLon:
    regex = r"((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)"


class SemanticVersion:
    regex = (
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    )


class JiraIssueTicket:
    regex = r"[A-Z]{2,}-\d+"


class Hashtag:
    regex = r"#[^ !@#$%^&*(),.?\":{}|<>]*"
