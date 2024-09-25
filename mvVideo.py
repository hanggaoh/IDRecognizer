import os
from pathlib import Path
import sys

from matcher.matcher import match_and_format
from utils.file import check_file_in_dir
import shutil

from logger_setup import get_logger

logger = get_logger()

# Extended list of video file extensions
video_extensions = {
    '.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', 
    '.3gp', '.webm', '.ogv', '.vob', '.rm', '.rmvb', '.m2ts', '.mts', '.ts', 
    '.mxf', '.divx', '.f4v', '.asf', '.amv', '.svi', '.3g2', '.m2v', '.mpe',
    '.mpv', '.m1v', '.m4p', '.m4b'
}

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

def find_videos(directory):
    # Walk through directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has a video file extension
            if Path(file).suffix.lower() in video_extensions:
                # Yield the directory and file name
                yield (root, file)


def moveVideos(video_files, destination_dir):
    for original_dir, file_name in video_files:
        logger.debug(f"{file_name}")
        formatedName = match_and_format(file_name, patterns)
        extension = file_name.split(".")[-1]
        logger.debug(f"formatedName: {formatedName}, extension: {extension}")
        destination_name = f"{formatedName[0].upper()}.{extension}" if len(formatedName) > 0 else file_name
        destination_name_remove_duplicate = check_file_in_dir(os.path.join(original_dir, file_name), destination_dir, destination_name, True)
        logger.debug(f"Origin file: {os.path.join(original_dir, file_name)}")
        logger.debug(f"Destin file: {os.path.join(destination_dir, destination_name_remove_duplicate)}")
        shutil.move(os.path.join(original_dir, file_name), os.path.join(destination_dir, destination_name_remove_duplicate))
        logger.debug("Moving complete")


def findMoveVideos(source_folder, destination_folder):
    video_files = find_videos(source_folder)
    moveVideos(video_files, destination_folder)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: script.py <source_folder> <destination_folder>")
        sys.exit(1)
    
    source_folder = sys.argv[1]
    destination_folder = sys.argv[2]
    
    findMoveVideos(source_folder, destination_folder)

