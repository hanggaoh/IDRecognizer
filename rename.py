#%%
import re
import os
from utils.formatter import PathFormatter
from logger_setup import get_logger
import argparse

logger = get_logger()
log_file_path = "logs/problem_rename.log"

# pattern = re.compile(r'Copied\s+(.*?)\s+to\s+(.*)\sat')
pattern = re.compile(r'Pulling\s+(.*?)\s+to\s+(.*)')

def build_parser():
    p = argparse.ArgumentParser(description="Demo")
    p.add_argument("--dest_dir", default="./data", help="Path to data dir")
    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = pattern.search(line)
            if match:
                original_path = match.group(1)
                moved_path = match.group(2)
                moved_base = os.path.basename(moved_path)
                if args.dest_dir is not None:
                    dest_dir = args.dest_dir
                    moved_path = os.path.join(dest_dir, moved_base)
                else:
                    dest_dir = os.path.dirname(moved_path)
                reformated_name = PathFormatter.get_corrected_path(dest_dir, original_path)
                print(f"Original: {original_path}, Moved: {moved_path}, Dest Dir: {dest_dir}")
                print(f"Reformatted Name: {reformated_name}")
                if os.path.isfile(moved_path):
                    print(f"Renaming {moved_path} to {reformated_name}")
                    os.rename(moved_path, reformated_name)

#%%

if __name__ == "__main__":
    main()
# %%
