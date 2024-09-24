import filecmp

def test_file_comparison_identical_files():
    # Paths to the two identical video files
    file1 = 'D:\迅雷下载\RVG-039\A\RVG-039.mp4'
    file2 = 'D:\迅雷下载\RVG-039\B\RVG-039.mp4'

    # Compare the files (set shallow=False to ensure content comparison)
    are_files_identical = filecmp.cmp(file1, file2, shallow=False)

    # Check if the files are identical
    print(f"File equal: {are_files_identical}")
    assert not are_files_identical, "Test failed: The files should not be identical."

if __name__ == "__main__":
    test_file_comparison_identical_files()
