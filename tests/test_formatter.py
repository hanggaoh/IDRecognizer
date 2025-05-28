
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

if __name__ == '__main__':
    unittest.main()
