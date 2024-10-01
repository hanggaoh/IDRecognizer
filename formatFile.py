# sanitize_filename.py
import sys
import os
from matcher.matcher import match_and_format
from utils.file import check_file_in_dir

patterns = {
    r'(heyzo).*(\d{4})': r'\1-\2',
    r'(?i)(fc2).*(ppv).*(\d{7}|\b\d{6}\b)': r'\1-\2-\3',
    r'(?i)(\d{6})[-_](\d{3}).*(carib|1pon)': r'\3-\1-\2',
    r'(?i)(carib|1pon).*(\d{6})[-_](\d{3}).*': r'\1-\2-\3',
    r'(\d{6})[-_](\d{3})': r'\1-\2',
    r'([a-zA-Z]{4})[0]*(\d{3,4})': r'\1-\2',
    r'([nN]\d{4})': r'\1',
   r'([a-zA-Z]{4,6})[-_0](\d{2,4})': r'\1-\2',
    r'([a-zA-Z0-9]{2,8})[-_0](\d{2,4})': r'\1-\2',
    r'([a-zA-Z]{3,4})(\d{2,4})': r'\1-\2',
    }


if __name__ == "__main__":
    # The input file path will be passed as the first argument
    destination_Folder = sys.argv[1]
    file_name = sys.argv[2]

    formatedName = match_and_format(file_name, patterns)
    extension = file_name.split(".")[-1]
    destination_name = f"{formatedName[0].upper()}.{extension}" if len(formatedName) > 0 else file_name
    destination_name_remove_duplicate = check_file_in_dir("", destination_Folder, destination_name, False)

    # Join the base directory with the sanitized filename
    corrected_path = os.path.join(destination_Folder, destination_name_remove_duplicate)

    # Print the corrected path, which will be used by the shell script
    print(corrected_path)
