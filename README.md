# simplematch

> Minimal, super readable string pattern matching for python.

[![PyPI Version][pypi-image]][pypi-url]

## Syntax

`simplematch` has only two syntax elements:

- wildcard `*`
- capture group `{capture_name}`

Capture groups can be named (`{name}`), unnamed (`{*}`) and typed (`{value:float}`).

The following types are available:

- `ìnt`
- `float`
- `email`
- `url`
- `ipv4`
- `ipv6`
- `bitcoin`
- `ssn` (Social security number)
- `ccard` (matches Visa, MasterCard, American Express, Diners Club, Discover, JCB)

## Basic usage

```python
import simplematch as sm

# extracting data
sm.match(
    pattern="Invoice_*_{year}_{month}_{day}.pdf",
    string="Invoice_RE2321_2021_01_15.pdf")
>>> {"year": "2021", "month": "01", "day": "15"}

# test match only
sm.test("ABC-{value:int}", "ABC-13")
>>> True
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

# show generated regular expression
matcher.regex
>>> '^(?P<year>[+-]?[0-9]+)\\-(?P<month>[+-]?[0-9]+):\\ (?P<value>[+-]?(?:[0-9]*[.])?[0-9]+)$'
```

## Background

`simplematch` aims to fill a gap between parsing with `str.split()` and regular
expressions. It should be as simple as possible, fast and stable.

The `simplematch` syntax is transpiled to regular expressions under the hood, so
matching performance should be just as good.

I hope you get some good use out of this!

## License

[MIT](https://choosealicense.com/licenses/mit/)

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/simplematch
[pypi-url]: https://pypi.org/project/simplematch/
