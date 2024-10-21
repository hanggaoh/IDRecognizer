#!/bin/bash

# Get the current working directory
CURRENT_DIR=$(pwd)
HOME_DIR="/home/pi"

# Define paths
PYTHON_SCRIPT="$CURRENT_DIR/checkVideo.py"
LOG_FILE="$CURRENT_DIR/logs/broken.txt"
SMBSHARE_DIR="$HOME_DIR/smbshare"

# Create logs directory if it doesn't exist
mkdir -p "$CURRENT_DIR/logs"

# Command to add to cron
CRON_JOB="0 4 * * * /usr/bin/python3 $PYTHON_SCRIPT $SMBSHARE_DIR $LOG_FILE"

# Check if the cron job already exists
if sudo crontab -l | grep -q "$PYTHON_SCRIPT"; then
    echo "Cron job already exists."
else
    # Add the cron job
    (sudo crontab -l; echo "$CRON_JOB") | sudo crontab -
    echo "Cron job added: $CRON_JOB"
fi
