import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from revoregex import RegexMatcher, RevoRegex

class TestRegexMatcher(unittest.TestCase):
    def test_revo_regex_api(self):
        revo = RevoRegex(lang="tr")
        self.assertTrue(revo.validate("email", "test@example.com"))
        self.assertFalse(revo.validate("email", "test.com"))
        revo_en = RevoRegex(lang="en")
        self.assertTrue(revo_en.validate("email", "test@example.com"))
        self.assertFalse(revo_en.validate("email", "test.com"))
    def test_email_validation(self):
        matcher_tr = RegexMatcher(language='tr')
        matcher_en = RegexMatcher(language='en')
        self.assertTrue(matcher_tr.validate('email', 'test@example.com'))
        self.assertFalse(matcher_tr.validate('email', 'test@.com'))
        self.assertTrue(matcher_en.validate('email', 'user@mail.co.uk'))
        self.assertFalse(matcher_en.validate('email', 'user@mail'))

    def test_phone_validation(self):
        matcher_tr = RegexMatcher(language='tr')
        matcher_en = RegexMatcher(language='en')
        self.assertTrue(matcher_tr.validate('telefon', '05551234567'))
        self.assertTrue(matcher_tr.validate('telefon', '+905551234567'))
        self.assertFalse(matcher_tr.validate('telefon', '12345'))
        self.assertTrue(matcher_en.validate('phone', '+11234567890'))
        self.assertTrue(matcher_en.validate('phone', '1234567890'))
        self.assertFalse(matcher_en.validate('phone', '555-1234'))

    def test_tc_validation(self):
        matcher_tr = RegexMatcher(language='tr')
        self.assertTrue(matcher_tr.validate('tc', '12345678901'))
        self.assertFalse(matcher_tr.validate('tc', '02345678901'))
        self.assertFalse(matcher_tr.validate('tc', 'abcdefghijk'))

    def test_iban_validation(self):
        matcher_tr = RegexMatcher(language='tr')
        matcher_en = RegexMatcher(language='en')
        self.assertTrue(matcher_tr.validate('iban', 'TR330006100519786457841326'))
        self.assertFalse(matcher_tr.validate('iban', 'TR006100519786457841326'))
        self.assertTrue(matcher_en.validate('iban', 'GB29 NWBK 6016 1331 9268 19'))
        self.assertFalse(matcher_en.validate('iban', '1234567890'))

    def test_english_number(self):
        matcher = RegexMatcher(language='en')
        self.assertIsNotNone(matcher.match('number', '1234'))
        self.assertIsNone(matcher.match('number', 'abcd'))

    def test_turkish_sayi(self):
        matcher = RegexMatcher(language='tr')
        self.assertIsNotNone(matcher.match('sayı', '5678'))
        self.assertIsNone(matcher.match('sayı', 'abcd'))

    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            RegexMatcher(language='de')

    def test_invalid_pattern_key(self):
        matcher = RegexMatcher(language='en')
        with self.assertRaises(ValueError):
            matcher.match('not_a_key', 'test')

if __name__ == '__main__':
    unittest.main()
