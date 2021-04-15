import easymatch as em


def test_readme_example():
    result = em.match(
        pattern="Invoice*_{year}_{month}_{day}.pdf",
        string="Invoice_RE2321_2021_01_15.pdf",
    )
    assert result == {"year": "2021", "month": "01", "day": "15"}


def test_extended_readme_example():
    result = em.match(
        pattern="{path}/Invoice*_{year}_{month}_{day}.pdf",
        string="~/Documents/Invoices/Invoice_RE2321_2021_01_15.pdf",
    )
    assert result == {
        "path": "~/Documents/Invoices",
        "year": "2021",
        "month": "01",
        "day": "15",
    }


def test_regex():
    em.test("{file}.js", "archive.zip")
    em.test("{file}.js", "index.js")
    em.test("{folder}/{filename}.js", "foo/bar.js")
    em.test("*.{extension}", "/root/folder/file.exe")
    em.test("{folder}/{filename}.{extension}", "test/123.pdf")
    em.test("{*}/{filename}?{*}", "www.site.com/home/hello.js?p=1")


def test_simple():
    assert em.test("*.py", "hello.py")
    assert not em.test("*.zip", "hello.py")

    assert em.test("{file}.py", "hello.py")
    assert not em.test("{file}.zip", "hello.py")


def test_simple_matching():
    # should return the right match dict
    assert em.match("{folder}/{filename}.py", "home/hello.py") == {
        "folder": "home",
        "filename": "hello",
    }

    # should return empty object if no match
    assert em.match("{folder}/{filename}?{params}", "hello.js?p=1") == dict()

    # should match strings with . (dot) and ? (question mart) sights
    assert em.match("{folder}/{filename}?{params}", "home/hello.js?p=1") == dict(
        folder="home", filename="hello.js", params="p=1"
    )

    # should match wild cards
    assert em.match("*/{filename}", "home/hello.js") == dict(filename="hello.js")

    # NOT: should tolerate *{param} syntax - it acts as */{param}
    # this is different from the easypattern library!
    assert not em.match("*{filename}", "home/hello.js") == dict(filename="hello.js")

    # should save wild cards
    assert em.match("{*}/{filename}?{*}", "www.site.com/home/hello.js?p=1") == {
        0: "www.site.com/home",
        1: "p=1",
        "filename": "hello.js",
    }


def test_type_int():
    m = em.Matcher("{num:int}")
    assert m.match("123") == {"num": 123}
    assert m.match("-123") == {"num": -123}
    assert not m.match("-123.0")
    assert m.match("+123") == {"num": 123}
    assert m.match("+000123") == {"num": 123}
    assert m.match("0123") == {"num": 123}


def test_type_float():
    m = em.Matcher("{num:float}")
    assert m.match("123.4") == {"num": 123.4}
    assert m.match("-123.4") == {"num": -123.4}
    assert m.match("-123.0")
    assert m.match("+123.4") == {"num": 123.4}
    assert m.match("+000123.4") == {"num": 123.4}


def test_type_ipv4():
    m = em.Matcher("{ip:ipv4}")
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
    m = em.Matcher("{card:ccard}")
    assert m.match("4569403961014710") == {"card": "4569403961014710"}
    assert m.match("5191914942157165") == {"card": "5191914942157165"}
    assert m.match("370341378581367") == {"card": "370341378581367"}
    assert m.match("38520000023237") == {"card": "38520000023237"}
    assert m.match("6011000000000000") == {"card": "6011000000000000"}
    assert m.match("3566002020360505") == {"card": "3566002020360505"}
    assert not m.match("1234566660000222")


def test_type_bitcoin():
    m = em.Matcher("{coin:bitcoin}")
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


def test_type_url():
    m = em.Matcher("{url:url}")
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
