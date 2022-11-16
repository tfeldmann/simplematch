# Changelog

## WIP

- Literal `*` can now be matched by escaping them: `\*`

## v1.3 (2021-04-19)

- Adds a `case_sensitive` option to `test()` and `match()` function. (`True` by default)
- Allows editing and manual specification of `Matcher.regex` and `Matcher.converters`.

## v1.2 (2021-04-19)

- `match()` now returns an empty dict on matches with capture groups, `None` otherwise.
  In lower versions, `match()` always returned a dict.

## v1.1 (2021-04-16)

- The syntax for unnamed capture groups is now `{}`.
- add `letters` type

## v1.0 (2021-04-16)

- inital release
