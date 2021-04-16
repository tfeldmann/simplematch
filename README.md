<img width="500" src="https://raw.githubusercontent.com/tfeldmann/simplematch/main/docs/simplematch.svg" alt="logo">

# simplematch

> Minimal, super readable string pattern matching for python.

[![PyPI Version][pypi-image]][pypi-url]
[![tests](https://github.com/tfeldmann/simplematch/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/tfeldmann/simplematch/actions/workflows/tests.yml)

```python
import simplematch

simplematch.match("He* {planet}!", "Hello World!")
>>> {"planet": "World"}

simplematch.match("It* {temp:float}°C *", "It's -10.2°C outside!")
>>> {"temp": -10.2}
```

## Installation

`pip install simplematch`

## Syntax

`simplematch` has only two syntax elements:

- wildcard `*`
- capture group `{name}`

Capture groups can be named (`{name}`), unnamed (`{}`) and typed (`{name:float}`).

The following types are available:

- `int`
- `float`
- `email`
- `url`
- `ipv4`
- `ipv6`
- `bitcoin`
- `ssn` (social security number)
- `ccard` (matches Visa, MasterCard, American Express, Diners Club, Discover, JCB)

For now, only named capture groups can be typed.

Then use one of these functions:

```python
import simplematch

simplematch.match(pattern, string) # -> returns a dict
simplematch.test(pattern, string)  # -> return True / False
```

Or use a `Matcher` object:

```python
import simplematch as sm

matcher = sm.Matcher(pattern)

matcher.match(string) # -> returns a dict
matcher.test(string)  # -> returns True / False
matcher.regex         # -> shows the generated regex
```

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

## Contributions

Contributions are welcome! Just submit a PR and maybe get in touch with me via email
before big changes.

## License

[MIT](https://choosealicense.com/licenses/mit/)

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/simplematch
[pypi-url]: https://pypi.org/project/simplematch/
