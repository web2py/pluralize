import ast
import json
import os
import re
import threading

__version__ = "20240519.1"

re_language = re.compile(r"^\w\w(-\w+)*.json$")


class lazyT(object):

    """accesssory object used to represent a T("string")"""

    def __init__(self, translator, text, **kwargs):
        self.translator = translator
        self.text = text
        self.kwargs = kwargs

    def format(self, **other):
        """T('hello {n}').format(n=2)"""
        kwargs = dict(self.kwargs)
        kwargs.update(**other)
        return lazyT(self.translator, self.text, **kwargs)

    def __add__(self, other):
        """T('hello') + ' ' + T('world')"""
        return str(self) + str(other)

    def __radd__(self, other):
        """T('hello') + ' ' + T('world')"""
        return str(other) + str(self)

    def __str__(self):
        """str(T('dog')) -> 'cane'"""
        return self.xml()

    def __mod__(self, obj):
        """T('route %d') % 66 -> 'route 66'"""
        return self.xml() % obj

    def xml(self):
        """same as str but for interoperability with yatl helpers"""
        return self.translator(self.text, **self.kwargs)


class Translator(object):
    def __init__(self, folder=None, encoding="utf-8", comment_marker=None):
        """
        creates a translator object loading languages and pluralizations from translations/en-US.py files
        usage:

            T =  Translator('translations')
            print(T('dog'))
        """
        self.local = threading.local()
        self.languages = {}
        self.local.tag = None
        self.local.language = None
        self.missing = set()
        self.folder = folder
        self.encoding = encoding
        self.comment_marker = comment_marker
        if folder:
            self.load(folder)

    def load(self, folder):
        """loads languages and pluralizations from folder/en-US.json files"""
        self.languages = {}
        for filename in os.listdir(folder):
            if re_language.match(filename):
                with open(
                    os.path.join(folder, filename), "r", encoding=self.encoding
                ) as fp:
                    self.languages[filename[:-5].lower()] = json.load(fp)

    def save(self, folder=None, ensure_ascii=True):
        """save the loaded translation files"""
        folder = folder or self.folder
        for key in self.languages:
            filename = "%s.json" % key
            with open(
                os.path.join(folder, filename), "w", encoding=self.encoding
            ) as fp:
                json.dump(
                    self.languages[key],
                    fp,
                    sort_keys=True,
                    indent=4,
                    ensure_ascii=ensure_ascii,
                )

    def select(self, accepted_languages="fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5"):
        """given appected_langauges string from HTTP header, picks the best match"""
        if isinstance(accepted_languages, str):
            accepted_languages = [
                tag.split(";")[0].replace("_", "-").strip()
                for tag in accepted_languages.split(",")
            ]
            for tag in accepted_languages:
                for k in range(tag.count("-"), 0, -1):
                    subtag = "-".join(tag.split("-")[:k])
                    if not subtag in accepted_languages:
                        accepted_languages.append(subtag)
        self.local.tag = None
        self.local.language = None
        for tag in accepted_languages:
            if tag.lower() in self.languages:
                self.local.tag = tag.lower()
                self.local.language = self.languages[tag.lower()]
                break

    def __call__(self, text):
        """retuns a lazyT object"""
        if isinstance(text, lazyT):
            return text
        return lazyT(self._translator, text)

    def _translator(self, text, **kwargs):
        """translates/pluralizes"""
        if not isinstance(text, str):
            text = str(text)
        if getattr(self.local, "language", None):
            n = kwargs.get("n", 1)
            translations = self.local.language.get(text)
            if translations is None:
                self.missing.add(text)
            elif isinstance(translations, dict) and translations:
                k = max(int(i) for i in translations.keys() if int(i) <= n)
                text = translations[str(k)].format(**kwargs)
        if text and self.comment_marker:
            text = text.split(self.comment_marker)[0]
        return text.format(**kwargs)

    @staticmethod
    def find_matches(
        folder, name="T", extensions=["py", "js", "html"], encoding="utf-8"
    ):
        """finds all strings in files in folder needing translations"""
        matches_found = set()
        re_string_t = (
            r"(?<=[^\w]%s\()(?P<name>"
            r"[uU]?[rR]?(?:'''(?:[^']|'{1,2}(?!'))*''')"
            r"|(?:'(?:[^'\\]|\\.)*')"
            r'|(?:"""(?:[^"]|"{1,2}(?!"))*""")'
            r'|(?:"(?:[^"\\]|\\.)*"))'
        ) % name
        regex_t = re.compile(re_string_t)
        for root, dirs, files in os.walk(folder):
            for name in files:
                if name.split(".")[-1] in extensions:
                    path = os.path.join(root, name)
                    with open(path, encoding=encoding) as fp:
                        data = fp.read()
                    items = regex_t.findall(data)
                    matches_found |= set(map(ast.literal_eval, items))
        return list(matches_found)

    def update_languages(self, items):
        """updates all loaded language files with the items, typically items returned by find_matches
        example of workflow:
            T = Translator()
            T.load(laguage_folder)
            T.update_languages(T.find_matches(app_folder))
            T.save(languages_folder)
        """
        for tag in self.languages:
            language = self.languages[tag]
            for item in items:
                if not item in language:
                    language[item] = {}
