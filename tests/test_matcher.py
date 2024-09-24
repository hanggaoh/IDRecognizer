import unittest
from matcher import matcher
class TestMatchAndFormat(unittest.TestCase):
    def test_name_formatting(self):
        text = "423777_3xplanet_Heyzo_3449.mp4"
        patterns = {r'([a-zA-Z]{2,5})[-_](\d{2,4})': r'\1-\2'}
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result, ["Heyzo-3449"])

# To run the tests
if __name__ == '__main__':
    unittest.main()
