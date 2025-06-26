import os
import argparse
from logger_setup import get_logger
from utils.constants import video_extensions
import subprocess
import shutil
import json

logger = get_logger()

def find_duplicate_names(folder_path):
    duplicate_files = {}
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext.lower() in video_extensions:
                # Check for name.extension and name_N.extension patterns
                if name.endswith(('_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9')):
                    base_name = name[:-2]
                    original_file = f"{base_name}{ext}"
                    if original_file in files:
                        if original_file not in duplicate_files:
                            duplicate_files[original_file] = []
                        duplicate_files[original_file].append(file_name)
                    else:
                        logger.info(f"No original file for dup {file_name}, rename it")
                        shutil.move(os.path.join(folder_path, file_name), os.path.join(folder_path, original_file))
                elif f"{name}_1{ext}" in files or f"{name}_2{ext}" in files or f"{name}_3{ext}" in files or \
                     f"{name}_4{ext}" in files or f"{name}_5{ext}" in files or f"{name}_6{ext}" in files or \
                     f"{name}_7{ext}" in files or f"{name}_8{ext}" in files or f"{name}_9{ext}" in files:
                    if file_name not in duplicate_files:
                        duplicate_files[file_name] = []
    
    if duplicate_files:
        logger.info(f"Found potential duplicate video files: {duplicate_files}")
    else:
        logger.info("No potential duplicate video files found.")
    return duplicate_files

def get_media_info(file_path):
        try:
            result = subprocess.run(
                ['mediainfo', '--Output=JSON', file_path],
                capture_output=True, text=True, check=True
            )
            info = json.loads(result.stdout)
            track = info['media']['track']
            video_track = next((t for t in track if t['@type'] == 'Video'), None)
            if not video_track:
                return None
            duration = float(video_track.get('Duration', 0))
            width = int(video_track.get('Width', 0))
            height = int(video_track.get('Height', 0))
            return {'duration': duration, 'width': width, 'height': height}
        except Exception as e:
            logger.error(f"Failed to get media info for {file_path}: {e}")
            return None

def is_broken(file_path):
    info = get_media_info(file_path)
    return info is None or info['duration'] == 0

def check_duplicate_videos(folder_path, alternative_folder_path):
    # find if folder_path files has some files that has name.extension and name_\d.extension and collect those files
    duplicate_map = find_duplicate_names(folder_path)
    for original, dups in duplicate_map.items():
        original_path = os.path.join(folder_path, original)
        orig_info = get_media_info(original_path)
        if is_broken(original_path) or not orig_info:
            logger.info(f"Original file {original} is broken, searching for a valid duplicate to replace it.")
            replaced = False
            for dup in dups:
                dup_path = os.path.join(folder_path, dup)
                if not is_broken(dup_path):
                    logger.info(f"Replacing broken original {original} with duplicate {dup}.")
                    shutil.move(dup_path, original_path)
                    replaced = True
                    break
                else:
                    os.remove(dup_path)
            if not replaced:
                logger.info(f"No valid duplicate found to replace broken original {original}.")
            continue
        for dup in dups:
            dup_path = os.path.join(folder_path, dup)
            dup_info = get_media_info(dup_path)
            if not dup_info:
                logger.info(f"Duplicate file {dup} is broken or unreadable, moving to {alternative_folder_path}")
                os.remove(dup_path)
                continue
            # Compare durations (allow small difference, e.g., 1 second)
            if abs(orig_info['duration'] / dup_info['duration'] - 1) < 0.01:
                # Keep higher resolution
                orig_res = orig_info['width'] * orig_info['height']
                dup_res = dup_info['width'] * dup_info['height']
                if dup_res > orig_res:
                    logger.info(f"Duplicate {dup} has higher resolution than {original}, moving {original} to {alternative_folder_path}")
                    shutil.move(original_path, os.path.join(alternative_folder_path, original))
                    shutil.move(dup_path, original_path)
                else:
                    logger.info(f"Moving duplicate {dup} to {alternative_folder_path}")
                    shutil.move(dup_path, os.path.join(alternative_folder_path, original))
            else:
                logger.info(f"Duplicate {dup} duration does not match original {original}, skipping.")

def main():
    # Argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Check duplicate videos.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing video files")
    parser.add_argument("alternative_folder_path", type=str, help="Path to the output file for storing results")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the arguments
    check_duplicate_videos(args.folder_path, args.alternative_folder_path)


if __name__ == "__main__":
    main()
