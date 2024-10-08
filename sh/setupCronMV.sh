#!/bin/bash

# Get the current working directory
currentPWD=$(pwd)

# Define the log file path
logFile="$currentPWD/logs/mv_cron.log"

# Create the logs directory if it doesn't exist
mkdir -p "$currentPWD/logs"

# Check if cron is installed, and install if not
if ! command -v cron &> /dev/null; then
    echo "Cron is not installed. Installing..."
    sudo apt update
    sudo apt install -y cron
    sudo systemctl enable cron
    sudo systemctl start cron
fi

# Check if there is a crontab for the pi user
if ! crontab -u pi -l &>/dev/null; then
    # Create an empty crontab for pi
    crontab -u pi -l > temp_cron
else
    crontab -u pi -l > temp_cron
fi

# Check if the cron job already exists
if ! grep -q "$currentPWD/sh/mvFileCron.sh" temp_cron; then
    # Add the cron job for pi
    echo "0 */12 * * * $currentPWD/sh/mvFileCron.sh >> $logFile 2>&1" >> temp_cron
    crontab -u pi temp_cron
    echo "Cron job added for user pi: $currentPWD/sh/mvFileCron.sh every 12 hours"
else
    echo "Cron job already exists for user pi."
fi

# Clean up
rm temp_cron