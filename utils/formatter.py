import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from matcher.matcher import match_and_format
from utils.constants import patterns
from logger_setup import get_logger

logger = get_logger()


class PathFormatter:
    @staticmethod
    def join_path_base_ext(destination_folder, file_name, extension):
        destination_name = f"{file_name.upper()}.{extension}"
        destination_path = os.path.join(destination_folder, destination_name)
        return destination_path

    @staticmethod
    def split_path(origin_path):
        parent_folder = os.path.dirname(origin_path)
        filename_with_ext = os.path.basename(origin_path)
        basename, extension = os.path.splitext(filename_with_ext)
        extension = extension.lstrip('.')
        return parent_folder, basename, extension

    @staticmethod
    def choose_basename_for_destination_file(matches_folder, matches_basename, original_name):
        corrected_basename = original_name
        if len(matches_basename) > 0:
            logger.debug("Matches found in basename, using the first match.")
            corrected_basename = matches_basename[0]
        elif len(matches_folder) > 0:
            logger.debug("No matches in basename, using matches from folder.")
            corrected_basename = matches_folder[0]
        else:
            logger.debug("No matches found, using original basename.")
            corrected_basename = original_name
        return corrected_basename

    @staticmethod
    def get_corrected_path(destination_folder, origin_path):
        parent_folder, basename, extension = PathFormatter.split_path(origin_path.strip())
        matches_folder = match_and_format(parent_folder, patterns)
        matches_basename = match_and_format(basename, patterns)

        logger.debug(f"Matches for folder: {matches_folder}")
        logger.debug(f"Matches for basename: {matches_basename}")
        chosen_basename = PathFormatter.choose_basename_for_destination_file(
            matches_folder, matches_basename, basename
        )
        corrected_path = PathFormatter.join_path_base_ext(destination_folder, chosen_basename, extension)
        return corrected_path

