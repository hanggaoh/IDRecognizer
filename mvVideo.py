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
import cv2
import ffmpeg

logger = get_logger()

def is_same_file(src, dst):
    def get_video_duration(path):
        try:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return None
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            if fps > 0:
                return frame_count / fps
            return None
        except Exception:
            return None

    dur_src = get_video_duration(src)
    dur_dst = get_video_duration(dst)
    if dur_src is None or dur_dst is None:
        return False
    threshold = 0.02  # 2% difference allowed
    return abs(dur_src - dur_dst) / max(dur_src, dur_dst) < threshold

def compare_video_resolutions(src, dst):
    # Use OpenCV to compare video resolutions (width x height)
    def get_resolution(path):
        try:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return (0, 0)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return (width, height)
        except Exception:
            return (0, 0)

    res_src = get_resolution(src)
    res_dst = get_resolution(dst)

    if (res_src[0] * res_src[1]) > (res_dst[0] * res_dst[1]):
        return 1  # Source is higher resolution
    elif (res_src[0] * res_src[1]) < (res_dst[0] * res_dst[1]):
        return -1  # Destination is higher resolution
    else:
        return 0  # Resolutions are the same

def is_better_codec(src_path, dst_path):
    def get_codec(path):
        try:
            probe = ffmpeg.probe(path)
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    return stream.get('codec_name', '')
        except Exception:
            return ''
        return ''

    # Define codec efficiency order (higher index = more efficient)
    codec_efficiency = [
        'mpeg2video',  # Legacy, very low efficiency
        'vp8',         # WebM baseline, similar to H.264
        'h263',        # Older mobile codec, slightly better than MPEG-2
        'h264',        # Widely used, good balance
        'theora',      # Open-source, similar to VP8
        'hevc',        # High efficiency, ~50% better than H.264
        'vp9',         # Comparable to HEVC, royalty-free
        'av1',         # Most efficient mainstream codec
        'vvc',         # Versatile Video Coding (H.266), ~30% better than HEVC/AV1
        'evc',         # Essential Video Coding, designed for licensing simplicity
        'lc-evc',      # Low Complexity EVC, trade-off between speed and efficiency
    ]

    def codec_rank(codec):
        try:
            return codec_efficiency.index(codec)
        except ValueError:
            return -1  # Unknown codec, treat as least efficient

    src_codec = get_codec(src_path)
    dst_codec = get_codec(dst_path)
    return codec_rank(src_codec) > codec_rank(dst_codec)


def resolve_destination_name(original_path, destination_dir, base_name, ext, attempt=0):
    if attempt == 0:
        candidate_name = f"{base_name}.{ext}"
    else:
        candidate_name = f"{base_name}_{attempt}.{ext}"
    candidate_path = os.path.join(destination_dir, candidate_name)

    if not os.path.exists(candidate_path):
        return candidate_name  # No conflict

    if is_broken(candidate_path):
        logger.info(f"Destination file {candidate_path} is broken. Will replace.")
        return candidate_name  # Replace broken file

    if is_same_file(original_path, candidate_path):
        resolution_status = compare_video_resolutions(original_path, candidate_path)
        if resolution_status == 1:
            logger.info(f"Replacing {candidate_path} with higher resolution {original_path}")
            return candidate_name  # Replace with higher res
        elif resolution_status == -1:
            logger.info(f"Keeping existing {candidate_path} (higher resolution)")
            return None  # Skip moving
        elif is_better_codec(original_path, candidate_path):
            logger.info(f"Replacing {candidate_path} with more efficient codec from {original_path}")
            return candidate_name  # Replace with better codec
        else:
            logger.info(f"Keeping existing {candidate_path} (higher resolution)")
            return None
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
        _, _, free = shutil.disk_usage(destination_dir)
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

def moveVideos(video_files, destination_dir, remove=True):
    for original_dir, file_name in video_files:
        logger.debug(f"{file_name}")
        formatedName = match_and_format(file_name, patterns)
        extension = file_name.split(".")[-1]
        logger.debug(f"formatedName: {formatedName}, extension: {extension}")
        if formatedName and isinstance(formatedName, (list, tuple)) and len(formatedName) > 0:
            base_name = str(formatedName[0]).upper()
        else:
            base_name = os.path.splitext(file_name)[0]
        original_path = os.path.join(original_dir, file_name)
        destination_name = resolve_destination_name(original_path, destination_dir, base_name, extension)

        if destination_name is None:
            logger.info(f"Skipping {file_name} as a higher resolution file already exists.")
            os.remove(original_path)
            continue

        logger.debug(f"Origin file: {original_path}")
        logger.debug(f"Destin file: {os.path.join(destination_dir, destination_name)}")

        # Call the copy function
        copy_file_with_logging(original_path, destination_dir, destination_name, logger)
        
        # Remove the original file after successful copy
        if remove:
            try:
                if os.path.exists(destination_name):
                    os.remove(original_path)
            except Exception as e:
                logger.error(f"Failed to remove original file {original_path}: {e}")
        logger.debug("Moving complete")

def findMoveVideos(source_folder, destination_folder, remove=True):
    video_files = find_videos(source_folder)
    moveVideos(video_files, destination_folder, remove)

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
    remove = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
       
    if check_disk_usage(source_folder, threshold):
        findMoveVideos(source_folder, destination_folder, remove)
    else:
        logger.info(f"Disk usage of {source_folder} is below the threshold of {threshold}%. Skipping operation.")
