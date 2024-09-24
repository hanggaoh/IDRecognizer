
# Unit tests
import unittest
import tempfile
import shutil
from utils.file import check_and_rename_file
import os

class TestFileRename(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_file_exists_rename(self):
        # Create a file
        filename = "test.txt"
        open(os.path.join(self.test_dir, filename), 'w').close()
        new_filename = check_and_rename_file(self.test_dir, filename)
        self.assertEqual(new_filename, "test_1.txt")

    def test_identical_file(self):
        # Create two identical files
        filename = "test.txt"
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write("Sample text")
        
        # Call the function
        new_filename = check_and_rename_file(self.test_dir, filename)
        self.assertEqual(new_filename, "test.txt")  # Should return the original name