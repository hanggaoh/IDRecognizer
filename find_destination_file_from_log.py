# %%
import re
import os
from utils.formatter import PathFormatter
from logger_setup import get_logger
import argparse

logger = get_logger()
log_file_path = "logs/problem_log.log"

# pattern = re.compile(r'Copied\s+(.*?)\s+to\s+(.*)\sat')
pattern = re.compile(r"Destin file:\s+\/.*\/(.*)\.")


with open(log_file_path, "r") as log_file:
    for line in log_file:
        match = pattern.search(line)
        if match:
            print(match.group(1))

# %%
