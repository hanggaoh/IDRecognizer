import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from matcher.matcher import match_and_format
from utils.constants import patterns
from logger_setup import get_logger
from utils.checker import RuleChainChecker, ZeroSizeRule, MediaInfoDurationRule

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
    def get_available_destination(dest_path):
        """
        Returns a unique, valid destination file path for copying.
        - If dest_path does not exist, returns dest_path.
        - If dest_path exists and is broken (zero size or invalid media), returns dest_path.
        - If dest_path exists and is valid, appends _i until a non-existing path is found.
        """
        if not os.path.exists(dest_path):
            return dest_path

        checker = RuleChainChecker([ZeroSizeRule(), MediaInfoDurationRule()])
        if checker.apply_rules(dest_path):
            return dest_path

        base, ext = os.path.splitext(dest_path)
        for i in range(1, 10000):  # Arbitrary upper limit to avoid infinite loop
            candidate = f"{base}_{i}{ext}"
            if not os.path.exists(candidate):
                return candidate
        raise RuntimeError("Could not find available destination path.")

    @classmethod
    def get_corrected_path(cls, destination_folder, origin_path):
        """
        Returns a corrected, available destination path based on matching rules.
        """
        parent_folder, basename, extension = cls.split_path(origin_path.strip())
        matches_folder = match_and_format(parent_folder, patterns)
        matches_basename = match_and_format(basename, patterns)

        logger.debug(f"Matches for folder: {matches_folder}")
        logger.debug(f"Matches for basename: {matches_basename}")
        chosen_basename = cls.choose_basename_for_destination_file(
            matches_folder, matches_basename, basename
        )
        corrected_path = cls.join_path_base_ext(destination_folder, chosen_basename, extension)
        return cls.get_available_destination(corrected_path)
