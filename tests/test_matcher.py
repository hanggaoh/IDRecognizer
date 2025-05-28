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

    def test_name_unconsore(self):
        text = '無碼、無修正、UNCENSORED SKYHD-001 Sky Angel Blue Vol.1 宮澤ケイト, 桜井梨花  .mp4'
        results = matcher.match_and_format(text, patterns)
        self.assertEqual(results[0], 'SKYHD-001')

    def test_name_unconsore_k(self):
        text = '[thz.la]k1463_yuki_okamoto_bo.wmv'
        results = matcher.match_and_format(text, patterns)
        self.assertEqual(results[0], 'k1463')

    def test_name_milti_CD_formatting(self):
        # Test cases
        test_cases = {
            "giro-92_01.wmv": ['Giro-092_01'],
            "race-45_cd1.mp4": ['Race-045_01'],
            "event-03D.mkv": ['Event-003_D'],
            "tour-129cd1.MP4": ['Tour-129_01', 'Tour-129_c'],
            "event-003/event-003_cd2.mp4": ['Event-003_02'],
        }
        
        for original, expected in test_cases.items():
            # Apply matching and formatting
            result = matcher.match_and_format(original, self.pattern_dict)
            self.assertEqual(result[0], expected[0], f"Failed for {original}")
    def test_path(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/[javtorrent.biz]_KMI062/KMI-062.avi"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "KMI-062")
    
    def test_file_seperate_cds(self):
        text = "KMI-062/KMI-062_01.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "KMI-062_01")

    def test_file_seperate_cds_with_just_cd_number(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/miad-548/[456k.me]miad-548-2.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "miad-548_02")

    def test_prefix_website(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/MMPB-026/hhd800.com@MMPB-026.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "MMPB-026")
    def test_no_seperator(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/140212[22ID-007]辻さき BEST SELECTION 4時間/22ID007.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "22ID-007")

    def test_series_formatting(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/GIRO-81/GIRO81_03.wmv"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "GIRO-081_03")

    def test_weird_AB_formatting(self):
        text = "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/SSPD-081/3xplanet_SSPD-081HDB.wmv"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "SSPD-081_B")
    
    def test_match_no_dash_but_space(self):
        text = "MIGD 028 (Mosaic Removed)W真性中出し 早川瀬里奈 原千尋 (Chihiro Hara & Serina Hayakawa)/MIGD 028 uncensored.mp4"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "MIGD-028")

    def test_match_no_dash(self):
        text = "zuko025.avi"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "zuko-025")
        
    def test_letter_space_digits(self):
        text = "IDBD-304   A.avi"
        result = matcher.match_and_format(text, patterns)
        self.assertEqual(result[0], "IDBD-304_A")

# To run the tests
if __name__ == '__main__':
    unittest.main()
