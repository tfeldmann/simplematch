# simplematch

Minimal, super readable string pattern matching for python.

## Basic example:

```python
import simplematch as sm

sm.match(
    pattern="Invoice*_{year}_{month}_{day}.pdf",
    string="Invoice_RE2321_2021_01_15.pdf")
>>> {"year": "2021", "month": "01", "day": "15"}
```

## Type hints

```python
import simplematch as sm

matcher = sm.Matcher("{year:int}-{month:int}: {value:float}")

# extracting data
matcher.match("2021-01: -12.786")
>>> {"year": 2021, "month": 1, "value": -12.786}

# month is no integer, no match
matcher.match("2021-AB: Hello")
>>> {}

# no extraction, only test for match
matcher.test("1234-01: 123.123")
>>> True
```

I use it in some applications to provide pattern matching functionality to endusers.

This library started as a python fork of https://github.com/nadav-dav/EasyPattern.
So kudos to you for the nice syntax!
