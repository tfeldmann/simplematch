import datetime
from decimal import Decimal
from uuid import UUID

import pytest  # type: ignore

import simplematch as sm


def test_readme_example_opener():
    assert sm.match("He* [planet]!", "Hello World!") == {"planet": "World"}
    assert sm.match("It* [temp:float]?°C *", "It's -10.2 °C outside!") == {"temp": -10.2}


def test_readme_example_basic_usage():
    result = sm.match(
        pattern="Invoice*_[year]_[month]_[day].pdf",
        string="Invoice_RE2321_2021_01_15.pdf",
    )
    assert result == {"year": "2021", "month": "01", "day": "15"}
    assert sm.test("ABC-[value:int]", "ABC-13")


def test_readme_example_typehints():
    matcher = sm.Matcher("[year:int]-[month:int]: [value:float]")
    assert matcher.match("2021-01: -12.786") == {
        "year": 2021,
        "month": 1,
        "value": -12.786,
    }
    assert matcher.match("2021-01-abc: Hello") is None
    assert matcher.test("1234-01: 123.123") is True
    assert (
        matcher.regex
        == "^(?P<year>[+-]?[0-9]+)\\-(?P<month>[+-]?[0-9]+):\\ (?P<value>[+-]?(?:[0-9]*[.])?[0-9]+)$"
    )
    assert matcher.converters == {"year": int, "month": int, "value": float}


@pytest.mark.parametrize(
    "fmt, inp, result",
    (
        # Wildcards
        ("*.py", "hello.py", True),
        ("*.zip", "hello.py", False),
        ("++.py", "yo.py", True),
        ("+++.py", "yo.py", False),
        ("yo???.py", "yo12.py", True),
        ("yo???.py", "yo1234.py", False),
        ("a|b", "a", True),
        ("a|b", "c", False),
        ("[:int]|[:float]", "1", True),
        ("[:int]|[:float]", "1.0", True),
        # Wildcards escaped
        (r"real[*]times", "real*times", True),
        (r"real[*]times", "real+times", False),
        (r"real[+]plus", "real+plus", True),
        (r"real[+]plus", "real-plus", False),
        (r"real[?]question mark", "real?question mark", True),
        (r"real[?]question mark", "real!question mark", False),
        (r"real[|]pipe", "real|pipe", True),
        (r"real[|]pipe", "real!pipe", False),
        # Groups
        ("[file].py", "hello.py", True),
        ("[file].zip", "hello.py", False),
        ("[folder]/[filename].js", "foo/bar.js", True),
        ("*.[extension]", "/root/folder/file.exe", True),
        ("[folder]/[filename].[extension]", "test/123.pdf", True),
        ("[]/[filename][?][]", "www.site.com/home/hello.js?p=1", True),
        # Unicode
        ("*.p?", "whatevör.pü", True),
        ("*.[:letters]", "whatevör.pü", True),
        ("*.[:letters]", "whatevör.p¥", False),
    ),
)
def test_test(fmt, inp, result):
    assert sm.test(fmt, inp) == result


@pytest.mark.parametrize(
    "fmt, inp, test_result, match_result",
    (
        ("*.py", "hello.py", True, {}),
        ("[].py", "hello.py", True, {0: "hello"}),
        ("*.py", "hello.__", False, None),
        ("[].py", "hello.__", False, None),
    ),
)
def test_result(fmt, inp, test_result, match_result):
    assert sm.test(fmt, inp) == test_result
    assert sm.match(fmt, inp) == match_result


def test_unnamed_wildcards():
    assert sm.match("[] sees []", "Tim sees Jacob") == {0: "Tim", 1: "Jacob"}


def test_match_dict_with_named_groups_and_hints():
    assert sm.match("[folder1]/[file_name][file_ID: int].py", "home/hello1.py") == {
        "folder1": "home",
        "file_name": "hello",
        "file_ID": 1,
    }


def test_return_none_if_no_match():
    assert sm.match("[folder]/[filename][?][params]", "hello.js?p=1") is None


def test_match_when_regex_values():
    assert sm.match("[folder]/[filename][?][params]", "home/hello.js?p=1") == dict(
        folder="home", filename="hello.js", params="p=1"
    )


def test_match_wildcards():
    assert sm.match("*/[filename]+js", "home/hello.js") == dict(filename="hello")


def test_save_unnamed_groups():
    assert sm.match("[]/[filename][?][]", "www.site.com/home/hello.js?p=1") == {
        0: "www.site.com/home",
        1: "p=1",
        "filename": "hello.js",
    }


def test_unnamed_groups_with_hints():
    assert sm.match("[:int] [:float] [:int]", "1 2.3 4") == {0: 1, 1: 2.3, 2: 4}


def test_mixed_groups_with_hints():
    assert sm.match("[one:int] [:int]", "1 2") == {0: 2, "one": 1}


@pytest.mark.parametrize(
    "inp, result",
    (
        ("123", {"num": 123}),
        ("-123", {"num": -123}),
        ("+123", {"num": 123}),
        ("+000123", {"num": 123}),
        ("0123", {"num": 123}),
        ("-123.0", None),
    ),
)
def test_type_int(inp, result):
    m = sm.Matcher("[num:int]")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("123.4", {"num": 123.4}),
        ("-123.4", {"num": -123.4}),
        ("+123.4", {"num": 123.4}),
        ("+000123.4", {"num": 123.4}),
        ("-123.0", {"num": -123.0}),
    ),
)
def test_type_float(inp, result):
    m = sm.Matcher("[num:float]")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("123.4", {"num": Decimal("123.4")}),
        ("-123.4", {"num": Decimal("-123.4")}),
        ("+123.4", {"num": Decimal("123.4")}),
        ("+000123.4", {"num": Decimal("123.4")}),
        ("-123.0", {"num": Decimal("-123")}),
        ("-.1", {"num": Decimal("-0.1")}),
    ),
)
def test_type_decimal(inp, result):
    m = sm.Matcher("[num:decimal]")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("d4d42dd9-68de-463d-b43e-b1a12a7623d3", {"uuid": UUID("d4d42dd968de463db43eb1a12a7623d3")}),
        ("d4d42dd968de463db43eb1a12a7623d3", {"uuid": UUID("d4d42dd968de463db43eb1a12a7623d3")}),
        ("d4d42dd968de463db43eb1a12a7623", None),
    ),
)
def test_type_uuid(inp, result):
    m = sm.Matcher("[uuid:uuid]")
    assert m.match(inp) == result


def test_type_date():
    m = sm.Matcher("[date:date]")
    assert m.match("2022-09-16") == {"date": datetime.date(2022, 9, 16)}


def test_type_datetime__naive():
    now = datetime.datetime.utcnow()
    as_str = now.isoformat()

    m = sm.Matcher("[datetime:datetime]")
    assert m.match(as_str) == {"datetime": now}


def test_type_datetime__with_timezone():
    m = sm.Matcher("[datetime:datetime]")
    as_datetime = m.match("2007-11-20 22:19:17+02:00")["datetime"]

    assert as_datetime.year == 2007
    assert as_datetime.second == 17
    assert as_datetime.tzinfo == datetime.timezone(datetime.timedelta(seconds=7200))


@pytest.mark.parametrize(
    "inp, result",
    (
        ("abcf123", {"chars": "abcf"}),
        ("abcf123#", {"chars": "abcf"}),
        ("ACBAAC_123", {"chars": "ACBAAC"}),
    ),
)
def test_type_letter(inp, result):
    m = sm.Matcher("[chars:letters]*")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("abcf123", {"chars": "abcf123"}),
        ("abcf123#", {"chars": "abcf123"}),
        ("ACBAAC_123", {"chars": "ACBAAC_123"}),
    ),
)
def test_type_identifier(inp, result):
    m = sm.Matcher("[chars:identifier]*")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "string",
    (
        "john@doe.com",
        "dotted.name@dotted.domain.org",
        "ug.ly-name_1@ug-ly.domain0.co.uk",
    ),
)
def test_type_email(string):
    matcher = sm.Matcher("[email:email]")
    assert matcher.test(string) is True
    assert matcher.match(string) == {"email": string}


@pytest.mark.parametrize(
    "inp, result",
    (
        ("127.0.0.1", {"ip": "127.0.0.1"}),
        ("192.168.1.1", {"ip": "192.168.1.1"}),
        ("127.0.0.1", {"ip": "127.0.0.1"}),
        ("0.0.0.0", {"ip": "0.0.0.0"}),
        ("255.255.255.255", {"ip": "255.255.255.255"}),
        ("256.256.256.256", None),
        ("999.999.999.999", None),
        ("1.2.3", None),
        ("1.2.3.4", {"ip": "1.2.3.4"}),
    ),
)
def test_type_ipv4(inp, result):
    m = sm.Matcher("[ip:ipv4]")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("4569403961014710", {"card": "4569403961014710"}),
        ("5191914942157165", {"card": "5191914942157165"}),
        ("370341378581367", {"card": "370341378581367"}),
        ("38520000023237", {"card": "38520000023237"}),
        ("6011000000000000", {"card": "6011000000000000"}),
        ("3566002020360505", {"card": "3566002020360505"}),
        ("1234566660000222", None),
    ),
)
def test_type_ccard(inp, result):
    m = sm.Matcher("[card:ccard]")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, is_url",
    (
        ("abcdef", False),
        ("www.whatever.com", False),
        ("https://github.com/geongeorge/i-hate-regex", True),
        ("https://www.facebook.com/", True),
        ("https://www.google.com/", True),
        ("https://xkcd.com/2293/", True),
        ("https://this-shouldn't.match@example.com", False),
        ("http://www.example.com/", True),
    ),
)
def test_type_url(inp, is_url):
    m = sm.Matcher("[url:url]")
    result = m.match(inp)
    if is_url:
        assert result == {"url": inp}
    else:
        assert result is None


def test_register_type():
    def mood_detect(smiley):
        moods = {
            "😀": "good",
            "☹️": "bad",
            "🫤": "sceptic",
        }
        return moods.get(smiley, "unknown")

    sm.register_type("smiley", r"[😀☹🫤]", mood_detect)

    assert sm.match("I'm feeling [mood:smiley] *", "I'm feeling 😀 today!") == {
        "mood": "good",
    }


def test_case_sensitive():
    assert sm.test("Hello []", "Hello World")
    assert not sm.test("hello []", "Hello World")

    assert sm.test("Hello []", "Hello World", case_sensitive=False)
    assert sm.test("hello []", "Hello World", case_sensitive=False)

    # keep capture group names
    assert sm.match("HELLO [PlAnEt]", "Hello Earth", case_sensitive=False) == {
        "PlAnEt": "Earth"
    }


def test_manual_specification():
    m = sm.Matcher()
    m.regex = r"^(?P<test>\w+) \d+$"
    m.converters = {"test": str.upper}
    assert m.match("hello 123") == {"test": "HELLO"}
