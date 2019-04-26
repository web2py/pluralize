import os
import re
import json
import threading
import ast

__version__ = "0.1.0"

re_language = re.compile('^\w\w(-\w+)*.json$')


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

    def xml(self):
        """same as str but for interoperability with yatl helpers"""
        return self.translator(self.text, **self.kwargs)


class Translator(object):

    def __init__(self, folder=None):
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
        if folder:
            self.load(folder)

    def load(self, folder):
        """loads languages and pluralizations from folder/en-US.json files"""
        self.languages = {}
        for filename in os.listdir(folder):
            if re_language.match(filename):
                with open(os.path.join(folder, filename)) as fp:
                    self.languages[filename[:-5].lower()] = json.load(fp)

    def dump(self, folder):
        """save the loaded translation files"""
        for tag in self.languages:
            filename = tag + '.json'
            with open(os.path.join(folder, filename), 'w') as fp:
                json.dump(self.languages[tag], fp, sort_keys=True, indent=4)

    def select(self, accepted_languages='fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5'):
        """given appected_langauges string from HTTP header, picks the best match"""
        if isinstance(accepted_languages, str):
            accepted_languages = [tag.split(
                ';')[0].strip() for tag in accepted_languages.split(',')]
            for tag in accepted_languages:
                for k in range(tag.count('-'), 0, -1):
                    subtag = '-'.join(tag.split('-')[:k])
                    if not subtag in accepted_languages:
                        accepted_languages.append(subtag)
        self.local.tag = None
        self.local.language = None
        for tag in accepted_languages:
            if tag.lower() in self.languages:
                self.local.tag = tag
                self.local.language = self.languages[tag]
                break

    def __call__(self, text):
        """retuns a lazyT object"""
        return lazyT(self._translator, text)

    def _translator(self, text, **kwargs):
        """translates/pluralizes"""
        if self.local.language:
            n = kwargs.get('n', 1)
            translations = self.local.language.get(text)
            if translations is None:
                self.missing.add(text)
            elif isinstance(translations, dict) and translations:
                k = max(i for i in translations.keys() if i <= n)
                text = translations[k].format(**kwargs)
        return text.format(**kwargs)

    def find_matches(self, folder, name='T', extensions=['py', 'js', 'html']):
        """finds all strings in files in folder needing translations"""
        matches_found = set()
        string_t_finder = r'(?<=[^\w]' + name + r'\()(?P<name>'\
            + r"[uU]?[rR]?(?:'''(?:[^']|'{1,2}(?!'))*''')|"\
            + r"(?:'(?:[^'\\]|\\.)*')|" + r'(?:"""(?:[^"]|"{1,2}(?!"))*""")|'\
            + r'(?:"(?:[^"\\]|\\.)*"))'
        regex_t = re.compile(string_t_finder)
        for root, dirs, files in os.walk(folder):
            for name in files:
                if name.split('.')[-1] in extensions:
                    path = os.path.join(root, name)
                    with open(path) as fp:
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
