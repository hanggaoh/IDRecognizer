import os
from pathlib import Path
import sys

from matcher.matcher import match_and_format
from utils.file import check_file_in_dir
from utils.constants import video_extensions
from utils.constants import patterns
import shutil

from logger_setup import get_logger

logger = get_logger()

# Extended list of video file extensions


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
        try:
            original_path = os.path.join(original_dir, file_name)
            destination_path = os.path.join(destination_dir, destination_name_remove_duplicate)

            total, used, free = shutil.disk_usage(destination_dir)
            file_size = os.path.getsize(original_path)

            if file_size > free:
                raise OSError("Not enough disk space to move the file.")

            # Copy the file with metadata preservation
            shutil.copy2(original_path, destination_path)
            
            # Remove the original file after successful copy
            os.remove(original_path)
            logger.debug("Moving complete")
        except (KeyboardInterrupt, Exception) as e:
            if os.path.exists(destination_path):
                os.remove(destination_path)
            logger.error(f"An error occurred: {e}")
            raise

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

