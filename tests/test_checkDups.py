import os
import shutil
import tempfile
import unittest

from checkDups import find_duplicate_names

class TestFindDuplicateNames(unittest.TestCase):
    def setUp(self):
        # create an empty temp dir before each test
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # remove it (and all its contents) after each test
        shutil.rmtree(self.temp_dir)

    def create_files(self, files):
        # helper to touch each filename in the temp dir
        for name in files:
            path = os.path.join(self.temp_dir, name)
            # ensure any subdirs exist (here you don’t have subdirs, but just in case)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w'):
                pass

    def test_duplicate_with_uppercase_extension(self):
        files = ['film.MP4', 'film_1.MP4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('film.MP4', result)
        self.assertIn('film_1.MP4', result['film.MP4'])
        
    def test_duplicate_with_multiple_originals(self):
        files = ['a.mp4', 'a_1.mp4', 'b.avi', 'b_1.avi', 'b_2.avi']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('a.mp4', result)
        self.assertIn('a_1.mp4', result['a.mp4'])
        self.assertIn('b.avi', result)
        self.assertEqual(set(result['b.avi']), {'b_1.avi', 'b_2.avi'})

    def test_duplicate_with_non_sequential_suffix(self):
        files = ['x.mp4', 'x_2.mp4', 'x_5.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('x.mp4', result)
        self.assertEqual(set(result['x.mp4']), {'x_2.mp4', 'x_5.mp4'})

    def test_duplicate_with_large_number_suffix(self):
        files = ['y.mp4', 'y_9.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('y.mp4', result)
        self.assertIn('y_9.mp4', result['y.mp4'])

    def test_duplicate_with_irrelevant_files(self):
        files = ['z.mp4', 'z_1.mp4', 'notes.txt', 'z_1.txt', 'z_2.doc']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('z.mp4', result)
        self.assertIn('z_1.mp4', result['z.mp4'])
        # txt/doc should be ignored
        self.assertNotIn('notes.txt', result)
        self.assertEqual(len(result['z.mp4']), 1)

    def test_duplicate_with_hidden_files(self):
        files = ['.hidden.mp4', '.hidden_1.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('.hidden.mp4', result)
        self.assertIn('.hidden_1.mp4', result['.hidden.mp4'])

    def test_duplicate_with_spaces_in_name(self):
        files = ['my video.mp4', 'my video_1.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('my video.mp4', result)
        self.assertIn('my video_1.mp4', result['my video.mp4'])

    def test_duplicate_with_multiple_dots(self):
        files = ['archive.v1.mp4', 'archive.v1_1.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('archive.v1.mp4', result)
        self.assertIn('archive.v1_1.mp4', result['archive.v1.mp4'])

    def test_duplicate_with_no_extension(self):
        files = ['noext', 'noext_1']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        # nothing should be flagged (no recognized video extension)
        self.assertEqual(result, {})
    def test_no_duplicates(self):
        files = ['unique1.mp4', 'unique2.avi', 'unique3.mkv']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertEqual(result, {})

    def test_duplicate_with_mixed_case_extensions(self):
        files = ['movie.Mp4', 'movie_1.mP4', 'movie_2.MP4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('movie.Mp4', result)
        self.assertEqual(set(result['movie.Mp4']), {'movie_1.mP4', 'movie_2.MP4'})

    def test_duplicate_with_multiple_groups(self):
        files = ['alpha.mp4', 'alpha_1.mp4', 'beta.avi', 'beta_1.avi', 'gamma.mkv']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('alpha.mp4', result)
        self.assertIn('alpha_1.mp4', result['alpha.mp4'])
        self.assertIn('beta.avi', result)
        self.assertIn('beta_1.avi', result['beta.avi'])
        self.assertNotIn('gamma.mkv', result)

    def test_duplicate_with_no_original(self):
        files = ['orphan_1.mp4', 'orphan_2.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        # One of the orphans is picked as original
        self.assertEqual(len(result), 1)
        orig = list(result.keys())[0]
        dups = result[orig]
        self.assertEqual(set([orig] + dups), {'orphan_1.mp4', 'orphan_2.mp4'})

    def test_duplicate_with_subdirectories(self):
        os.makedirs(os.path.join(self.temp_dir, 'subdir'))
        files = ['main.mp4', 'main_1.mp4', os.path.join('subdir', 'main_2.mp4')]
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('main.mp4', result)
        self.assertIn('main_1.mp4', result['main.mp4'])
        self.assertIn('main_2.mp4', result['main.mp4'])
        
    def test_duplicate_with_leading_zeros_in_suffix(self):
        files = ['clip.mp4', 'clip_01.mp4', 'clip_002.mp4']
        self.create_files(files)
        result = find_duplicate_names(self.temp_dir)
        self.assertIn('clip.mp4', result)
        self.assertEqual(set(result['clip.mp4']), {'clip_01.mp4', 'clip_002.mp4'})
if __name__ == '__main__':
    unittest.main(verbosity=2)
