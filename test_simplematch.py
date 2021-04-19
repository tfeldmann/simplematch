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
    assert matcher.match("2021-01-abc: Hello") == None
    assert matcher.test("1234-01: 123.123") == True
    assert (
        matcher.regex
        == "^(?P<year>[+-]?[0-9]+)\\-(?P<month>[+-]?[0-9]+):\\ (?P<value>[+-]?(?:[0-9]*[.])?[0-9]+)$"
    )
    assert matcher.converters == {"year": int, "month": int, "value": float}


def test_simple():
    assert sm.test("*.py", "hello.py")
    assert not sm.test("*.zip", "hello.py")
    assert sm.test("{file}.py", "hello.py")
    assert not sm.test("{file}.zip", "hello.py")

    assert sm.test("{folder}/{filename}.js", "foo/bar.js")
    assert sm.test("*.{extension}", "/root/folder/file.exe")
    assert sm.test("{folder}/{filename}.{extension}", "test/123.pdf")
    assert sm.test("{}/{filename}?{}", "www.site.com/home/hello.js?p=1")


def test_return_values():
    # test() behaviour
    assert sm.test("*.py", "hello.py") == True
    assert sm.test("{}.py", "hello.py") == True
    assert sm.test("*.py", "hello.__") == False
    assert sm.test("{}.py", "hello.__") == False

    # match() behaviour
    assert sm.match("*.py", "hello.py") == {}
    assert sm.match("{}.py", "hello.py") == {0: "hello"}
    assert sm.match("*.py", "hello.__") is None
    assert sm.match("{}.py", "hello.__") is None


def test_unnamed_wildcards():
    assert sm.match("{} sees {}", "Tim sees Jacob") == {0: "Tim", 1: "Jacob"}


def test_simple_matching():
    # should return the right match dict
    assert sm.match("{folder}/{filename}.py", "home/hello.py") == {
        "folder": "home",
        "filename": "hello",
    }

    # should return None object if no match
    assert sm.match("{folder}/{filename}?{params}", "hello.js?p=1") == None

    # should match strings with . (dot) and ? (question mart) sights
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


def test_type_int():
    m = sm.Matcher("{num:int}")
    assert m.match("123") == {"num": 123}
    assert m.match("-123") == {"num": -123}
    assert not m.match("-123.0")
    assert m.match("+123") == {"num": 123}
    assert m.match("+000123") == {"num": 123}
    assert m.match("0123") == {"num": 123}


def test_type_float():
    m = sm.Matcher("{num:float}")
    assert m.match("123.4") == {"num": 123.4}
    assert m.match("-123.4") == {"num": -123.4}
    assert m.match("-123.0")
    assert m.match("+123.4") == {"num": 123.4}
    assert m.match("+000123.4") == {"num": 123.4}


def test_type_letter():
    m = sm.Matcher("{chars:letters}*")
    assert m.match("abcf123") == {"chars": "abcf"}
    assert m.match("abcf123#") == {"chars": "abcf"}
    assert m.match("ACBAAC_123") == {"chars": "ACBAAC"}


def test_type_bitcoin():
    m = sm.Matcher("{coin:bitcoin}")
    assert m.match("1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY") == {
        "coin": "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
    }
    assert not m.match("loremipsum")
    assert m.match("16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe") == {
        "coin": "16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe"
    }
    assert m.match("1EBHA1ckUWzNKN7BMfDwGTx6GKEbADUozX") == {
        "coin": "1EBHA1ckUWzNKN7BMfDwGTx6GKEbADUozX"
    }
    assert not m.match("0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae")
    assert m.match("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq") == {
        "coin": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
    }


def test_type_ssn():
    m = sm.Matcher("{n:ssn}")
    assert m.test("123-45-6789")
    assert not m.test("123 45 6789")
    assert m.test("333-22-4444")
    assert not m.test("aaa-bbb-cccc")
    assert not m.test("900-58-4564")
    assert not m.test("999-58-4564")
    assert not m.test("000-45-5454")


def test_type_ipv4():
    m = sm.Matcher("{ip:ipv4}")
    assert m.match("127.0.0.1") == {"ip": "127.0.0.1"}
    assert m.match("192.168.1.1") == {"ip": "192.168.1.1"}
    assert m.match("127.0.0.1") == {"ip": "127.0.0.1"}
    assert m.match("0.0.0.0") == {"ip": "0.0.0.0"}
    assert m.match("255.255.255.255") == {"ip": "255.255.255.255"}
    assert not m.match("256.256.256.256")
    assert not m.match("999.999.999.999")
    assert not m.match("1.2.3")
    assert m.match("1.2.3.4") == {"ip": "1.2.3.4"}


def test_type_ccard():
    m = sm.Matcher("{card:ccard}")
    assert m.match("4569403961014710") == {"card": "4569403961014710"}
    assert m.match("5191914942157165") == {"card": "5191914942157165"}
    assert m.match("370341378581367") == {"card": "370341378581367"}
    assert m.match("38520000023237") == {"card": "38520000023237"}
    assert m.match("6011000000000000") == {"card": "6011000000000000"}
    assert m.match("3566002020360505") == {"card": "3566002020360505"}
    assert not m.match("1234566660000222")


def test_type_url():
    m = sm.Matcher("{url:url}")
    assert not m.match("abcdef")
    assert not m.match("www.whatever.com")
    assert m.match("https://github.com/geongeorge/i-hate-regex") == {
        "url": "https://github.com/geongeorge/i-hate-regex"
    }
    assert m.match("https://www.facebook.com/") == {"url": "https://www.facebook.com/"}
    assert m.match("https://www.google.com/") == {"url": "https://www.google.com/"}
    assert m.match("https://xkcd.com/2293/") == {"url": "https://xkcd.com/2293/"}
    assert not m.match("https://this-shouldn't.match@example.com")
    assert m.match("http://www.example.com/") == {"url": "http://www.example.com/"}


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
