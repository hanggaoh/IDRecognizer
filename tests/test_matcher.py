import unittest
from matcher import matcher
from utils.constants import patterns
class TestMatchAndFormat(unittest.TestCase):
    def setUp(self):
        # Define the pattern dictionary as in your original code
        self.pattern_dict = {
            r"^([a-zA-Z0-9]+)\.(\d{2}\.\d{2}\.\d{2})(\..*)$": lambda m: f"{m.group(2)}.{m.group(1)}{m.group(3)}",
            r"([a-z]{2,5})-(\d{2,3})_(\d{1,2})": lambda m: f"{m.group(1).capitalize()}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
            r"([a-z]{2,5})-(\d{2,3})[-_]?cd([\d]{1,2})": lambda m: f"{m.group(1).capitalize()}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
            r"([a-z]{2,5})-(\d{2,3})([A-E])": lambda m: f"{m.group(1).capitalize()}-{m.group(2).zfill(3)}_{m.group(3)}"
        }
    
    def test_name_formatting_general(self):
        text = "423777_3xplanet_Heyzo_3449.mp4"
        patterns = {r'([a-zA-Z]{2,5})[-_](\d{2,4})': r'\1-\2'}
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result, ["Heyzo-3449"])

    def test_name_formatting_specific(self):
        text = "423777_3xplanet_Heyzo_3449.mp4"
        patterns = {r'(?i)(heyzo).*(\d{4})': r'\1-\2'}
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result, ["Heyzo-3449"])
    
    def test_name_formatting_all(self):
        text = "423777_3xplanet_Heyzo_3449.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "Heyzo-3449")

    def test_name_formatting_with_white(self):
        text = "legalporno.16.04.23.arwen.gold.and.crystal.greenvelle.gio151.mp4"
        results = matcher.match_and_format(text, patterns)
        self.assertEqual(results[0], "16.04.23.legalporno.arwen.gold.and.crystal.greenvelle.gio151.mp4")

    def test_name_milti_CD_formatting(self):
        # Test cases
        test_cases = {
            "giro-92_01.wmv": ['Giro-092_01'],
            "race-45_cd1.mp4": ['Race-045_01'],
            "event-03D.mkv": ['Event-003_D'],
            "tour-129cd1.MP4": ['Tour-129_01', 'Tour-129_c']
        }
        
        for original, expected in test_cases.items():
            # Apply matching and formatting
            result = matcher.match_and_format(original, self.pattern_dict)
            self.assertEqual(result, expected, f"Failed for {original}")
    
# To run the tests
if __name__ == '__main__':
    unittest.main()
