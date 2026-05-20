# Pluralize

Pluralize is a Python library for Internationalization (i18n) and Pluralization.

The library assumes a folder (for exaple "translations") that contains files like:

```sh
it.json
it-IT.json
fr.json
fr-FR.json
(etc)
```

Each file has the following structure, for example for Italian (it.json):

```json
{"dog": {"0": "no cane", "1": "un cane", "2": "{n} cani", "10": "tantissimi cani"}}
```

The top level keys are the expressions to be translated and the associated value/dictionary maps a number to a translation.
Different translations correspond to different plural forms of the expression,

Here is another example for the word "bed" in Czech

```json
{"bed": {"0": "no postel", "1": "postel", "2": "postele", "5": "postelí"}}
```

A translation value may also be a plain string when no pluralization is needed:

```json
{"hello": "ciao"}
```

When loaded, plain-string values are normalized in memory to `{"0": "..."}` and a warning is logged so the file can be cleaned up. The dict form is preferred, but the string form is accepted so that translation files written by other i18n tools work without modification.

To translate and pluralize a string "dog" one simply wraps the string in the T operator as follows:

```python
>>> from pluralize import Translator
>>> T = Translator('translations')
>>> dog = T("dog")
>>> print(dog)
dog
>>> T.select('it')
>>> print(dog)
un cane
>>> print(dog.format(n=0))
no cane
>>> print(dog.format(n=1))
un cane
>>> print(dog.format(n=5))
5 cani
>>> print(dog.format(n=20))
tantissimi cani
```

The string can contain multiple placeholders but the `{n}` placeholder is special because the variable called `n` is used to determine the pluralization by best match (max dict key `<= n`).

`T(...)` returns a `lazyT` object: the actual translation lookup is deferred until the value is rendered to a string. This means a `lazyT` can be created at import time and resolved later, after `T.select(...)` has chosen a language.

`lazyT` objects support:

- Concatenation with each other and with regular strings: `T("hello") + " " + T("world")`.
- `.format(**kwargs)` to bind placeholder values, including the special `n` for pluralization: `T("dog").format(n=5)`.
- The `%` operator with a dict, equivalent to `.format(**d)`: `T("route {num}") % {"num": 66}`. With a non-dict argument, `%` falls back to standard string `%` formatting on the translated text (for backward compatibility).
- `.xml()`, which returns the translated string. It is provided for interoperability with `yatl` HTML helpers, which call `xml()` on embedded values.

`T.select(s)` can parse a string `s` following the HTTP `Accept-Language` header format (e.g. `"fr-CH, fr;q=0.9, en;q=0.8, *;q=0.5"`) and picks the best available match from the loaded languages. Sub-tags are tried as fallbacks (e.g. `fr-CH` falls back to `fr`).

## Constructor options

```python
Translator(folder=None, encoding="utf-8", comment_marker=None)
```

- `folder`: directory of `xx.json` / `xx-YY.json` files to load. If omitted, no files are loaded and `T.languages` starts empty.
- `encoding`: text encoding used to read and write translation files. Defaults to `utf-8`.
- `comment_marker`: when set (e.g. `"##"`), any text after this marker is stripped from the *original* (untranslated) string before it is returned. This lets you disambiguate identical source strings that need different translations, e.g. `T("Open ##verb")` and `T("Open ##adjective")` — when no translation is selected, the user sees `"Open"`.

## Missing translations

Every source string that is looked up but has no entry in the currently selected language is added to `T.missing` (a `set`). This is useful for finding gaps after running your app against a real workload.

## Update the translation files

Find all strings wrapped in T(...) in .py, .html, and .js files:
```python
matches = T.find_matches('path/to/app/folder')
```

Add newly discovered entries in all supported languages
```python
T.update_languages(matches)
```

Add a new supported language (for example german, "de")

```python
T.languages['de'] = {}
```

Make sure all languages contain the same origin expressions
```python
known_expressions = set()
for language in T.languages.values():
    for expression in language:
        known_expressions.add(expression)
T.update_languages(known_expressions))
```

Finally save the changes:

```python
T.save('translations')
```

`save()` writes one JSON file per loaded language, sorted by key and indented. Pass `ensure_ascii=False` to keep non-ASCII characters as-is in the output.
