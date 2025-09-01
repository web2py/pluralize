import unittest

from pluralize import Translator


class TestPluralization(unittest.TestCase):
    def setUp(self):
        T = Translator(comment_marker="##")
        T.update_languages(T.find_matches("./"))
        T.languages = {
            "it": {
                "dog": {
                    "0": "no cane",
                    "1": "un cane",
                    "2": "due cani",
                    "3": "alcuni cani",
                    "10": "tanti cani",
                },
                "dog named {name}": {"0": "cane chiamato {name}"},
                "dog##dialect": {
                    "0": "nisciuno cane",
                },
            }
        }
        T.select("en;q=0.9,it-IT;q=0.1")
        self.T = T

    def test_simple(self):
        T = self.T
        dog = T("dog")
        self.assertEqual(str(dog.format(n=0)), "no cane")
        self.assertEqual(str(dog.format(n=1)), "un cane")
        self.assertEqual(str(dog.format(n=2)), "due cani")
        self.assertEqual(str(dog.format(n=3)), "alcuni cani")
        self.assertEqual(str(dog.format(n=5)), "alcuni cani")
        self.assertEqual(str(dog.format(n=100)), "tanti cani")

        self.assertEqual(str(dog % dict(n=0)), "no cane")
        self.assertEqual(str(dog % dict(n=1)), "un cane")

        plus = T("plus")
        T.languages["it"]["plus"] = {"0": "piu'"}
        self.assertEqual(
            dog + " " + plus + " " + dog.format(n=2), "un cane piu' due cani"
        )

    def test_interpolation(self):
        T = self.T
        dog = T("dog named {name}")
        self.assertEqual(str(dog.format(name="Snoopy")), "cane chiamato Snoopy")
        self.assertEqual(str(dog % dict(name="Snoopy")), "cane chiamato Snoopy")

    def test_comments(self):
        T = self.T
        dog = T("dog")
        self.assertEqual(str(dog.format(n=0)), "no cane")
        dog = T("dog##dialect")
        self.assertEqual(str(dog.format(n=0)), "nisciuno cane")

    def test_idempotency(self):
        T = self.T
        text = "dog"
        a = T(text)
        b = T(a)
        c = T(b)
        self.assertEqual(str(c.format(n=1)), "un cane")
