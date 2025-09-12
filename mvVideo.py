import os
from pathlib import Path
import sys
import time
from matcher.matcher import match_and_format
from utils.constants import video_extensions
from utils.constants import patterns
import shutil

from checkDups import is_broken
from logger_setup import get_logger

logger = get_logger()

def is_same_file(src, dst):
    try:
        return os.path.getsize(src) == os.path.getsize(dst)
    except Exception:
        return False

def get_high_res_file(src, dst):
    # Placeholder: you can implement a better logic (e.g., by resolution, bitrate, etc.)
    # For now, keep the larger file
    return src if os.path.getsize(src) >= os.path.getsize(dst) else dst

def resolve_destination_name(original_path, destination_dir, base_name, ext, attempt=0):
    # Compose candidate name
    if attempt == 0:
        candidate_name = f"{base_name}.{ext}"
    else:
        candidate_name = f"{base_name}_{attempt}.{ext}"
    candidate_path = os.path.join(destination_dir, candidate_name)

    if not os.path.exists(candidate_path):
        return candidate_name  # No conflict

    # If file exists, check if it's broken
    if is_broken(candidate_path):
        logger.info(f"Destination file {candidate_path} is broken. Will replace.")
        return candidate_name  # Replace broken file

    # If not broken, check if they are the same file
    if is_same_file(original_path, candidate_path):
        # Keep the higher resolution (larger) file
        high_res = get_high_res_file(original_path, candidate_path)
        if high_res == original_path:
            logger.info(f"Replacing {candidate_path} with higher resolution {original_path}")
            return candidate_name  # Replace with higher res
        else:
            logger.info(f"Keeping existing {candidate_path} (higher resolution)")
            return None  # Skip moving

    # Otherwise, try next candidate with incremented suffix
    return resolve_destination_name(original_path, destination_dir, base_name, ext, attempt + 1)

def find_videos(directory):
    # Walk through directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has a video file extension
            if Path(file).suffix.lower() in video_extensions:
                # Yield the directory and file name
                yield (root, file)

def copy_file_with_logging(original_path, destination_dir, destination_name, logger):
    """Copy a file to the destination directory with logging of the copy speed."""
    destination_path = os.path.join(destination_dir, destination_name)
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage(destination_dir)
        file_size = os.path.getsize(original_path)

        # Check for sufficient disk space
        if file_size > free:
            raise OSError("Not enough disk space to move the file.")

        # Start the timer
        start_time = time.time()
        
        # Copy the file with metadata preservation
        shutil.copy2(original_path, destination_path)

        # End the timer
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate speed in MB/s
        speed = file_size / (duration * 1024 * 1024) if duration > 0 else 0

        # Log the copy speed
        logger.info(f"Copied {original_path} to {destination_path} at {speed:.2f} MB/s in {duration:.2f} seconds.")

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
        base_name = formatedName[0].upper() if len(formatedName) > 0 else os.path.splitext(file_name)[0]
        original_path = os.path.join(original_dir, file_name)
        destination_name = resolve_destination_name(original_path, destination_dir, base_name, extension)
        if is_broken(original_path):
            logger.info(f"Skipping {file_name} as it is detected as broken.")
            os.remove(original_path)
            continue
        if destination_name is None:
            logger.info(f"Skipping {file_name} as a higher resolution file already exists.")
            os.remove(original_path)
            continue

        logger.debug(f"Origin file: {original_path}")
        logger.debug(f"Destin file: {os.path.join(destination_dir, destination_name)}")

        # Call the copy function
        copy_file_with_logging(original_path, destination_dir, destination_name, logger)
        
        # Remove the original file after successful copy
        os.remove(original_path)
        logger.debug("Moving complete")

def findMoveVideos(source_folder, destination_folder):
    video_files = find_videos(source_folder)
    moveVideos(video_files, destination_folder)

def check_disk_usage(directory, threshold):
    """Check if the disk usage of the given directory is above the threshold percentage."""
    total, used, free = shutil.disk_usage(directory)
    used_percentage = (used / total) * 100
    logger.info(f"Disk usage of {directory}: {used_percentage:.2f}%")
    return used_percentage >= threshold

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: script.py <source_folder> <destination_folder>")
        sys.exit(1)
    
    source_folder = sys.argv[1]
    destination_folder = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0
       
    if check_disk_usage(source_folder, threshold):
        findMoveVideos(source_folder, destination_folder)
    else:
        logger.info(f"Disk usage of {source_folder} is below the threshold of {threshold}%. Skipping operation.")
