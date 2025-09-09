#%%
import re
import os
from utils.formatter import PathFormatter
from logger_setup import get_logger

logger = get_logger()
log_file_path = "logs/problem_rename.log"

pattern = re.compile(r'Copied\s+(.*?)\s+to\s+(.*)\sat')

with open(log_file_path, 'r') as log_file:
    for line in log_file:
        match = pattern.search(line)
        if match:
            original_path = match.group(1)
            moved_path = match.group(2)
            dest_dir = os.path.dirname(moved_path)
            reformated_name = PathFormatter.get_corrected_path(dest_dir, original_path)
            logger.debug(f"Original: {original_path}, Moved: {moved_path}, Dest Dir: {dest_dir}")
            logger.debug(f"Reformatted Name: {reformated_name}")
            logger.debug(f"Renaming {moved_path} to {reformated_name}")
            os.rename(moved_path, reformated_name)
            