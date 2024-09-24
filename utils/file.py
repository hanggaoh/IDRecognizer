import os
import filecmp

# Mocking os and filecmp functionalities for testing without actual files
from unittest.mock import patch
from logger_setup import get_logger

logger = get_logger()

def check_file_in_dir(originalFile, destinationDir, filename, compare_identical=True):
    """
    Check if a file with the given filename exists in the destinationDir.
    If it exists, adds a numeric suffix before the extension, then checks again.
    If compare_identical is True, and the original file is identical to the existing one, 
    do not add a suffix and return the original filename.
    """
    base_name, extension = os.path.splitext(filename)
    destination_file_path = os.path.join(destinationDir, filename)
    
    if os.path.isfile(destination_file_path):
        # If compare_identical is True, check if the files are identical
        if compare_identical:
            for file in os.listdir(destinationDir):
                if file.startswith(base_name) and os.path.isfile(os.path.join(destinationDir, file)):
                    logger.debug(f"Find file same name: {destination_file_path}")
                    if filecmp.cmp(destination_file_path, originalFile, shallow=False):
                        logger.debug("Same file, replace it")
                        return filename
        
        # Append a numeric suffix if the file exists
        i = 1
        while os.path.isfile(destination_file_path):
            new_filename = f"{base_name}_{i}{extension}"
            destination_file_path = os.path.join(destinationDir, new_filename)
            i += 1
        return new_filename

    return filename


# Unit tests for the function
@patch('os.path.isfile')
@patch('os.listdir')
@patch('filecmp.cmp')
def test_check_file_in_dir(mock_cmp, mock_listdir, mock_isfile):
    # Test case 1: File does not exist in destinationDir
    mock_isfile.return_value = False
    assert check_file_in_dir('test_dir', 'file.txt', False) == 'file.txt'

    # Test case 2: File exists in destinationDir, add suffix
    mock_isfile.side_effect = lambda path: path.endswith("existing_file.txt")
    mock_listdir.return_value = ['existing_file.txt']
    assert check_file_in_dir('test_dir', 'existing_file.txt', False) == 'existing_file_1.txt'

    # Test case 3: File exists, but identical, no suffix added
    mock_cmp.return_value = True
    mock_isfile.side_effect = lambda path: path.endswith("identical_file.txt")
    mock_listdir.return_value = ['identical_file.txt']
    assert check_file_in_dir('test_dir', 'identical_file.txt', True) == 'identical_file.txt'

    # Test case 4: File exists, different content, add suffix
    mock_cmp.return_value = False
    mock_isfile.side_effect = lambda path: path.endswith("diff_content_file.txt")
    mock_listdir.return_value = ['diff_content_file.txt']
    assert check_file_in_dir('test_dir', 'diff_content_file.txt', True) == 'diff_content_file_1.txt'

    print("All tests passed.")
