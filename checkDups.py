import os
import argparse
from logger_setup import get_logger
from utils.constants import video_extensions
import subprocess
import shutil
import json
import re
from abc import ABC, abstractmethod

logger = get_logger()

def find_duplicate_names(folder_path):
    from collections import defaultdict

    base_name_map = defaultdict(list)
    for _, _, files in os.walk(folder_path):
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext.lower() in video_extensions:
                # Remove _N suffix if present for grouping
                match = re.match(r"^(.*?)(?:_(\d+))?$", name)
                if match:
                    base_name = match.group(1)
                    base_name_map[base_name].append(file_name)

    # Only keep groups with more than one file (potential duplicates)
    duplicate_files = {}
    for base, files in base_name_map.items():
        if len(files) > 1:
            # Find the original (without _N) and dups (with _N)
            orig = None
            dups = []
            for f in files:
                name, ext = os.path.splitext(f)
                if re.match(rf"^{re.escape(base)}$", name):
                    orig = f
                else:
                    dups.append(f)
            if orig:
                duplicate_files[orig] = dups
            else:
                # If no original, pick one as original and rest as dups
                duplicate_files[files[0]] = files[1:]

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

class DuplicateRule(ABC):
    @abstractmethod
    def apply(self, original, dups, folder_path, alternative_folder_path):
        pass

class ReplaceBrokenOriginalRule(DuplicateRule):
    def apply(self, original, dups, folder_path, alternative_folder_path):
        original_path = os.path.join(folder_path, original)
        orig_info = get_media_info(original_path)
        if is_broken(original_path) or not orig_info:
            logger.info(f"Original file {original} is broken, searching for a valid duplicate to replace it.")
            for dup in dups:
                dup_path = os.path.join(folder_path, dup)
                if not is_broken(dup_path):
                    logger.info(f"Replacing broken original {original} with duplicate {dup}.")
                    shutil.move(dup_path, original_path)
                    return True  # Rule handled this case
                else:
                    os.remove(dup_path)
            logger.info(f"No valid duplicate found to replace broken original {original}.")
            return True  # Rule handled this case
        return False  # Pass to next rule

class RemoveBrokenDuplicateRule(DuplicateRule):
    def apply(self, original, dups, folder_path, alternative_folder_path):
        handled = False
        for dup in dups[:]:
            dup_path = os.path.join(folder_path, dup)
            if not get_media_info(dup_path):
                logger.info(f"Duplicate file {dup} is broken or unreadable, remove it")
                os.remove(dup_path)
                dups.remove(dup)
                handled = True
        return handled  # Continue to next rule

class KeepHigherResolutionRule(DuplicateRule):
    def apply(self, original, dups, folder_path, alternative_folder_path):
        original_path = os.path.join(folder_path, original)
        orig_info = get_media_info(original_path)
        if not orig_info:
            return False
        for dup in dups:
            dup_path = os.path.join(folder_path, dup)
            dup_info = get_media_info(dup_path)
            if not dup_info or dup_info['duration'] == 0:
                continue
            if abs(orig_info['duration'] / dup_info['duration'] - 1) < 0.05:
                orig_res = orig_info['width'] * orig_info['height']
                dup_res = dup_info['width'] * dup_info['height']
                if dup_res > orig_res:
                    to_keep_path, to_remove_path = dup_path, original_path
                    to_keep_name, to_remove_name = dup, original
                else:
                    to_keep_path, to_remove_path = original_path, dup_path
                    to_keep_name, to_remove_name = original, dup

                if alternative_folder_path:
                    logger.info(f"Moving lower resolution file {to_remove_name} to {alternative_folder_path}")
                    shutil.move(to_remove_path, os.path.join(alternative_folder_path, to_remove_name))
                    if to_keep_path != original_path:
                        shutil.move(to_keep_path, original_path)
                else:
                    if to_keep_path != original_path:
                        shutil.move(to_keep_path, original_path)
                    os.remove(to_remove_path)
                    logger.info(f"Removed lower resolution file {to_remove_name}, kept {to_keep_name} at {original_path}")
                return True
            else:
                logger.info(f"Duplicate {dup} duration does not match original {original}, skipping.")
        return False

def check_duplicate_videos(folder_path, alternative_folder_path):
    duplicate_map = find_duplicate_names(folder_path)
    rules = [
        ReplaceBrokenOriginalRule(),
        RemoveBrokenDuplicateRule(),
        KeepHigherResolutionRule(),
    ]
    for original, dups in duplicate_map.items():
        for rule in rules:
            handled = rule.apply(original, dups, folder_path, alternative_folder_path)
            if handled:
                break

def main():
    parser = argparse.ArgumentParser(description="Check duplicate videos.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing video files")
    parser.add_argument(
        "--alternative_folder_path",
        type=str,
        default=None,
        help="Optional path to move duplicates or originals. If not provided, files will not be moved."
    )

    args = parser.parse_args()

    check_duplicate_videos(args.folder_path, args.alternative_folder_path)


if __name__ == "__main__":
    main()
