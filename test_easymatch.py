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
