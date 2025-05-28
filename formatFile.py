# sanitize_filename.py
import sys
from utils.formatter import PathFormatter

if __name__ == "__main__":
    destination_Folder = sys.argv[1]
    origin_path = sys.argv[2]
    print(PathFormatter.get_corrected_path(destination_Folder, origin_path))

