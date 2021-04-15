import easymatch as em

def test_readme_example():
    result = em.match(
        pattern="Invoice*_{year}_{month}_{day}.pdf",
        string="Invoice_RE2321_2021_01_15.pdf")
    assert result == {"year": "2021", "month": "01", "day": "15"}

def test_regex():
    em.test("{file}.js", "archive.zip")
    em.test("{file}.js", "index.js")
    em.test("{folder}/{filename}.js", "foo/bar.js")
    em.test("*.{extension}", "/root/folder/file.exe")
    em.test("{folder}/{filename}.{extension}", "test/123.pdf")
    em.test("{*}/{filename}?{*}", "www.site.com/home/hello.js?p=1")
