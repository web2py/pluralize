import unittest
from pluralize import Translator


class TestPluralization(unittest.TestCase):
    def test_simple(self):
        T = Translator()
        T.update_languages(T.find_matches('./'))
        dog = T('dog')
        T.languages = {'it': {'dog': {'0': 'no cane', '1': 'un cane',
                                      '2': 'due cani', '3': 'alcuni cani', '10': 'tanti cani'}}}
        T.select('en;q=0.9,it-IT;q=0.1')
        self.assertEqual(str(dog.format(n=0)), 'no cane')
        self.assertEqual(str(dog.format(n=1)), 'un cane')
        self.assertEqual(str(dog.format(n=2)), 'due cani')
        self.assertEqual(str(dog.format(n=3)), 'alcuni cani')
        self.assertEqual(str(dog.format(n=5)), 'alcuni cani')
        self.assertEqual(str(dog.format(n=100)), 'tanti cani')

        plus = T('plus')
        T.languages['it']['plus'] = {'0': "piu'"}
        self.assertEqual(
            dog + ' ' + plus + ' ' + dog.format(n=2), "un cane piu' due cani")
