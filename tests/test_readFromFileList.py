#PYTHONPATH=$(pwd) python3 tests/test_readFromFileList.py

from formatFile import formatName
from logger_setup import get_logger

logger = get_logger()

if __name__ == "__main__":
    with open("cat", "r") as f:
        for line in f:
            filename = line.rstrip().split("/")[-1]
            logger.debug(f"Original file: {filename}")
            logger.debug(f"Formated: {formatName("~/Movies/.a", filename)}")