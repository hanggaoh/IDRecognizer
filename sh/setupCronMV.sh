#!/bin/bash

# Get the current working directory
script_path="$(realpath "$0")"
parent_folder="$(dirname "$script_path")"
workingDirectory="$(dirname "$(dirname "$(realpath "$0")")")"
log_folder="$workingDirectory/logs"

# Define the log file path
logFile="$log_folder/mv_cron.log"

# Create the logs directory if it doesn't exist
mkdir -p "$log_folder"

# Check if cron is installed, and install if not
if ! command -v cron &> /dev/null; then
    echo "Cron is not installed. Installing..."
    sudo apt update
    sudo apt install -y cron
    sudo systemctl enable cron
    sudo systemctl start cron
fi

# Check if the cron job already exists for root
sudo crontab -l -u root 2>/dev/null > temp_cron || true
if ! grep -q "$workingDirectory/sh/mvFileCron.sh" temp_cron; then
    # Add the cron job for root
    echo "0 */4 * * * $workingDirectory/sh/mvFileCron.sh >> $logFile 2>&1" >> temp_cron
    sudo crontab -u root temp_cron
    echo "Cron job added for root: $workingDirectory/sh/mvFileCron.sh every 4 hours"
else
    echo "Cron job already exists for root."
fi

# Clean up
rm temp_cron