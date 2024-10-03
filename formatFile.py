# sanitize_filename.py
import sys
import os
from matcher.matcher import match_and_format
from utils.file import check_file_in_dir
from utils.constants import patterns

def formatName(destination_Folder, file_name):
    formatedName = match_and_format(file_name, patterns)
    extension = file_name.split(".")[-1]
    destination_name = f"{formatedName[0].upper()}.{extension}" if len(formatedName) > 0 else file_name
    destination_name_remove_duplicate = check_file_in_dir("", destination_Folder, destination_name, False)

    # Join the base directory with the sanitized filename
    corrected_path = os.path.join(destination_Folder, destination_name_remove_duplicate)
    return corrected_path

if __name__ == "__main__":
    # The input file path will be passed as the first argument
    destination_Folder = sys.argv[1]
    file_name = sys.argv[2]

    corrected_path=formatName(destination_Folder, file_name)
    # Print the corrected path, which will be used by the shell script
    print(corrected_path)
