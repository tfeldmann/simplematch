import pytest  # type: ignore

import simplematch as sm


def test_readme_example_opener():
    assert sm.match("He* {planet}!", "Hello World!") == {"planet": "World"}
    assert sm.match("It* {temp:float}°C *", "It's -10.2°C outside!") == {"temp": -10.2}


def test_readme_example_basic_usage():
    result = sm.match(
        pattern="Invoice*_{year}_{month}_{day}.pdf",
        string="Invoice_RE2321_2021_01_15.pdf",
    )
    assert result == {"year": "2021", "month": "01", "day": "15"}
    assert sm.test("ABC-{value:int}", "ABC-13")


def test_readme_example_typehints():
    matcher = sm.Matcher("{year:int}-{month:int}: {value:float}")
    assert matcher.match("2021-01: -12.786") == {
        "year": 2021,
        "month": 1,
        "value": -12.786,
    }
    assert matcher.match("2021-01-abc: Hello") is None
    assert matcher.test("1234-01: 123.123") is True
    assert matcher.regex == (
        "^(?P<year>[+-]?[0-9]+)\\-(?P<month>[+-]?[0-9]+):\\ (?P<value>[+-]?"
        "(?:[0-9]*[.])?[0-9]+)$"
    )
    assert matcher.converters == {"year": int, "month": int, "value": float}


@pytest.mark.parametrize(
    "fmt, inp, result",
    (
        ("*.py", "hello.py", True),
        ("*.zip", "hello.py", False),
        ("{file}.py", "hello.py", True),
        ("{file}.zip", "hello.py", False),
        ("{folder}/{filename}.js", "foo/bar.js", True),
        ("*.{extension}", "/root/folder/file.exe", True),
        ("{folder}/{filename}.{extension}", "test/123.pdf", True),
        ("{}/{filename}?{}", "www.site.com/home/hello.js?p=1", True),
    ),
)
def test_simple(fmt, inp, result):
    assert sm.test(fmt, inp) == result


@pytest.mark.parametrize(
    "fmt, inp, test_result, match_result",
    (
        ("*.py", "hello.py", True, {}),
        ("{}.py", "hello.py", True, {0: "hello"}),
        ("*.py", "hello.__", False, None),
        ("{}.py", "hello.__", False, None),
    ),
)
def test_result(fmt, inp, test_result, match_result):
    assert sm.test(fmt, inp) == test_result
    assert sm.match(fmt, inp) == match_result


def test_unnamed_wildcards():
    assert sm.match("{} sees {}", "Tim sees Jacob") == {0: "Tim", 1: "Jacob"}


def test_simple_matching():
    # should return the right match dict
    assert sm.match("{folder}/{filename}.py", "home/hello.py") == {
        "folder": "home",
        "filename": "hello",
    }

    # should return None object if no match
    assert sm.match("{folder}/{filename}?{params}", "hello.js?p=1") is None

    # should match strings with . (dot) and ? (question mark) signs
    assert sm.match("{folder}/{filename}?{params}", "home/hello.js?p=1") == dict(
        folder="home", filename="hello.js", params="p=1"
    )

    # should match wild cards
    assert sm.match("*/{filename}", "home/hello.js") == dict(filename="hello.js")

    # NOT: should tolerate *{param} syntax - it acts as */{param}
    # this is different from the easypattern library!
    assert not sm.match("*{filename}", "home/hello.js") == dict(filename="hello.js")

    # should save wild cards
    assert sm.match("{}/{filename}?{}", "www.site.com/home/hello.js?p=1") == {
        0: "www.site.com/home",
        1: "p=1",
        "filename": "hello.js",
    }


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
    m = sm.Matcher("{num:int}")
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
    m = sm.Matcher("{num:float}")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, result",
    (
        ("abcf123", {"chars": "abcf"}),
        ("abcf123#", {"chars": "abcf"}),
        ("ACBAAC_123", {"chars": "ACBAAC"}),
    ),
)
def test_type_letter(inp, result):
    m = sm.Matcher("{chars:letters}*")
    assert m.match(inp) == result


@pytest.mark.parametrize(
    "inp, is_bitcoin",
    (
        ("1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY", True),
        ("loremipsum", False),
        ("16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe", True),
        ("1EBHA1ckUWzNKN7BMfDwGTx6GKEbADUozX", True),
        ("0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae", False),
        ("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", True),
    ),
)
def test_type_bitcoin(inp, is_bitcoin):
    m = sm.Matcher("{coin:bitcoin}")
    result = m.match(inp)
    if is_bitcoin:
        assert result == {"coin": inp}
    else:
        assert result is None


@pytest.mark.parametrize(
    "string",
    (
        "john@doe.com",
        "dotted.name@dotted.domain.org",
        "ug.ly-name_1@ug-ly.domain0.co.uk",
    ),
)
def test_type_email(string):
    matcher = sm.Matcher("{email:email}")
    assert matcher.test(string) is True
    assert matcher.match(string) == {"email": string}


@pytest.mark.parametrize(
    "inp, is_ssn",
    (
        ("123-45-6789", True),
        ("123 45 6789", False),
        ("333-22-4444", True),
        ("aaa-bbb-cccc", False),
        ("900-58-4564", False),
        ("999-58-4564", False),
        ("000-45-5454", False),
    ),
)
def test_type_ssn(inp, is_ssn):
    m = sm.Matcher("{n:ssn}")
    assert m.test(inp) == is_ssn


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
    m = sm.Matcher("{ip:ipv4}")
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
    m = sm.Matcher("{card:ccard}")
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
        ("http:/ww.example.com/", False),
    ),
)
def test_type_url(inp, is_url):
    m = sm.Matcher("{url:url}")
    result = m.match(inp)
    if is_url:
        assert result == {"url": inp}
    else:
        assert result is None


def test_register_type():
    def mood_detect(smiley):
        moods = {
            ":)": "good",
            ":(": "bad",
            ":/": "sceptic",
        }
        return moods.get(smiley, "unknown")

    sm.register_type("smiley", r":[\(\)\/]", mood_detect)

    assert sm.match("I'm feeling {mood:smiley} *", "I'm feeling :) today!") == {
        "mood": "good"
    }


def test_case_sensitive():
    assert sm.test("Hello {}", "Hello World")
    assert not sm.test("hello {}", "Hello World")

    assert sm.test("Hello {}", "Hello World", case_sensitive=False)
    assert sm.test("hello {}", "Hello World", case_sensitive=False)

    # keep capture group names
    assert sm.match("HELLO {PlAnEt}", "Hello Earth", case_sensitive=False) == {
        "PlAnEt": "Earth"
    }


def test_manual_specification():
    m = sm.Matcher()
    m.regex = r"^(?P<test>\w+) \d+$"
    m.converters = {"test": str.upper}
    assert m.match("hello 123") == {"test": "HELLO"}
