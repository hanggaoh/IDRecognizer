import logging
import datetime
import os

LOGS_FOLDER = "logs"

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

# Create and configure logger
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create and configure logger with dynamic filename based on timestamp
log_filename = f"{LOGS_FOLDER}/logfile_{timestamp}.log"

logging.basicConfig(filename=log_filename,
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object for the logger
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


def get_logger():
    return logger
