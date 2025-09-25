
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.formatter import PathFormatter

class TestPathFormatter(unittest.TestCase):
    def test_split_path(self):
        parent, base, ext = PathFormatter.split_path("/foo/bar/baz.mp4")
        self.assertEqual(parent, "/foo/bar")
        self.assertEqual(base, "baz")
        self.assertEqual(ext, "mp4")

    def test_split_path_no_extension(self):
        parent, base, ext = PathFormatter.split_path("/foo/bar/baz")
        self.assertEqual(parent, "/foo/bar")
        self.assertEqual(base, "baz")
        self.assertEqual(ext, "")

    def test_join_path_base_ext(self):
        path = PathFormatter.join_path_base_ext("/dest", "baz", "mp4")
        self.assertEqual(path, "/dest/BAZ.mp4")

    def test_choose_basename_for_destination_file_only_basename(self):
        result = PathFormatter.choose_basename_for_destination_file(
            [], ["basename"], "orig"
        )
        self.assertEqual(result, "basename")

    def test_choose_basename_for_destination_file_none(self):
        result = PathFormatter.choose_basename_for_destination_file(
            [], [], "orig"
        )
        self.assertEqual(result, "orig")

    def test_get_corrected_path(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/881800362/ABCDE123.avi"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCDE-123.avi"
        )

    def test_get_corrected_path_folder_underscore_file_not(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/ABCD_123_1/ABCD_123.avi"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCD-123.avi"
        )

    def test_get_corrected_path_folder_not_underscore_file(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/ABCD123/ABCD123_1.avi"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCD-123_01.avi"
        )
    
    def test_get_corrected_path_file_not_match_choose_folder(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/ABCD123/something.not.match.avi"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCD-123.avi"
        )
    def test_get_corrected_path_file_has_cds(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/abcd-123/abcd-123cd2.mp4"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCD-123_02.mp4"
        )
    def test_get_corrected_path_file_has_url(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/【somthing.com】ABCD-123.1080p/【something.com】ABCD-123.1080p.mkv"
        )
        self.assertEqual(
            corrected_path,
            "/dest/ABCD-123.mkv"
        )

    def test_get_corrected_path_cds_has_space(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/IDBD-304/IDBD-304   A.avi"
        )
        self.assertEqual(
            corrected_path,
            "/dest/IDBD-304_A.avi"
        )
    
    def test_get_corrected_path_cds_has_other_letters(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "[bbs.yzkof.com]JUC-970.1080P/[bbs.yzkof.com]JUC-970.1080P B.mp4"
        )

        self.assertEqual(
            corrected_path,
            "/dest/JUC-970_B.mp4"
        )
    
    def test_get_corrected_path_cds_has_other_letters(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/mnt/2T/Archive/蒼井空/02-08-23 [AV] Sora Aoi - Let's Go Blue in the Sky!.avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/02-08-23.avi"
        )
    def test_get_corrected_path_letter_with_digit(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/[3D-1080P]MCB3DBD-04/MCB3DBD-04.mkv"
        )

        self.assertEqual(
            corrected_path,
            "/dest/MCB3DBD-04.mkv"
        )
    
    def test_get_corrected_path_letter_with_digi_1(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload/[3D-1080P]CW3D2BD-05/3D Catwalk Poison 05 - Megumi Shino.mkv"
        )

        self.assertEqual(
            corrected_path,
            "/dest/CW3D2BD-05.mkv"
        )

    def test_should_not_find_pattern_in_base(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "PT-142-DVD/dioguitar23.net_PT-142.ISO"
        )

        self.assertEqual(
            corrected_path,
            "/dest/PT-142.ISO"
        )
    def test_disk_in_name(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "Fairy FMX-003/[FAIRY] FMX-003-diskC-1.avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/FMX-003_C.avi"
        )
    def test_disk_in_name_d(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "Sky.High.Premium.7.SKY179.DiSC2.DVDRip.XviD.JAV.Uncensored-JapanX/japanx-sky179d2-cd1.avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/SKY-179_2.avi"
        )
    def test_3_letter_4_digit(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "FDD2050(AVI)/FDD2050.XviD.avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/FDD-2050.avi"
        )

    def test_base_name_should_not_be_matched(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "080108-819/whole2048.XviD.avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/080108-819.avi"
        )

    def test_base_name_five_digits(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "kiwvr-675/4k2.com@kiwvr00675_1_8k.mp4"
        )

        self.assertEqual(
            corrected_path,
            "/dest/KIWVR-00675.mp4"
        )

    def test_base_name_contains_letter(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "MKD-S29-DVD/hotavxxx.com_MKD-S29.ISO"
        )

        self.assertEqual(
            corrected_path,
            "/dest/MKD-S29.ISO"
        )
        
    def test_base_name_contains_open(self):
        corrected_path = PathFormatter.get_corrected_path(
            "/dest", "(OPEN0705).avi"
        )

        self.assertEqual(
            corrected_path,
            "/dest/OPEN-0705.avi"
        )

if __name__ == '__main__':
    unittest.main()
