#!/bin/bash

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

ssd_path="$SSD_PATH"
hdd_path="$HDD_PATH"

# Function to add cron job if it doesn't already exist
add_cron_job_if_not_exists() {
    local cron_job="$1"    # Cron job to add
    local log_file="$2"    # Path to the log file
    local temp_cron=$(mktemp)  # Temporary file for crontab

    # Ensure cron is installed
    if ! command -v cron &> /dev/null; then
        echo "Cron is not installed. Installing..."
        sudo apt update
        sudo apt install -y cron
        sudo systemctl enable cron
        sudo systemctl start cron
    fi

    # Fetch current crontab and check if the cron job already exists
    sudo crontab -l 2>/dev/null > "$temp_cron"

    # If the cron job doesn't exist, append it and install the new crontab
    if ! grep -q "$cron_job" "$temp_cron"; then
        echo "$cron_job" >> "$temp_cron"
        sudo crontab "$temp_cron"
        echo "Cron job added: $cron_job"
    else
        echo "Cron job already exists."
    fi

    # Clean up
    rm -f "$temp_cron"
}

# Function to create a new cron job for managing file transfer
create_cron_job() {
    local preferred_drive="$1"
    local secondary_drive="$2"

    # Get paths and log files
    local script_path="$(realpath "$0")"
    local parent_folder="$(dirname "$script_path")"
    local log_folder="$parent_folder/../logs"
    local log_file="$log_folder/cronjob.log"

    # Ensure the logs directory exists
    mkdir -p "$log_folder"

    # Define the cron job
    local cron_job="0 2 * * * /bin/bash -c 'sudo find /media/pi/smbshare -type f -atime -3 -print -exec cp -u --preserve=all {} /media/pi/$preferred_drive \; && sudo find /media/pi/smbshare -type f \( -atime +3 -o ! -atime -7 \) -print -exec mv -n {} /media/pi/$secondary_drive \;' >> $log_file 2>&1"

    # Add the cron job if it doesn't already exist
    add_cron_job_if_not_exists "$cron_job" "$log_file"
}

# Main script
create_cron_job "$1" "$2"
