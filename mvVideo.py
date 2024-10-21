import os
from pathlib import Path
import sys
import time
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


def copy_file_with_logging(original_path, destination_dir, logger):
    """Copy a file to the destination directory with logging of the copy speed."""
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage(destination_dir)
        file_size = os.path.getsize(original_path)

        # Check for sufficient disk space
        if file_size > free:
            raise OSError("Not enough disk space to move the file.")

        # Start the timer
        start_time = time.time()
        
        # Prepare destination path
        destination_name = os.path.basename(original_path)
        destination_path = os.path.join(destination_dir, destination_name)

        # Copy the file with metadata preservation
        shutil.copy2(original_path, destination_path)

        # End the timer
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate speed in MB/s
        speed = file_size / (duration * 1024 * 1024) if duration > 0 else 0

        # Log the copy speed
        logger.info(f"Copied {original_path} to {destination_dir} at {speed:.2f} MB/s in {duration:.2f} seconds.")

    except (KeyboardInterrupt, Exception) as e:
        if os.path.exists(destination_path):
            os.remove(destination_path)  # Clean up on error
        logger.error(f"An error occurred while copying {original_path}: {e}")
        raise

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

        original_path = os.path.join(original_dir, file_name)
        destination_path = os.path.join(destination_dir, destination_name_remove_duplicate)
        
        # Call the copy function
        copy_file_with_logging(original_path, destination_dir, logger)
        
        # Remove the original file after successful copy
        os.remove(original_path)
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

