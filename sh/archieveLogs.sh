#!/bin/sh

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

script_path="$(realpath "$0")"
parent_folder="$(dirname "$script_path")"
workingDirectory="$(dirname "$(dirname "$(realpath "$0")")")"
log_folder="$workingDirectory/logs"

echo "Archiving logs in $log_folder..."

# Get cut date: default is first day of this month, or use argument if provided
if [ -n "$1" ]; then
    cut_date="$1"
else
    cut_date="$(date +%Y-%m-01)"
fi

# Get last month in YYYY-MM format for archive name
archive_month="$(date -d "$cut_date -1 day" +%Y-%m)"

# Find .log files older than cut_date, zip them
files_to_archive=$(find "$log_folder" -maxdepth 1 -type f -name "*.log" ! -newermt "$cut_date")

if [ -n "$files_to_archive" ]; then
    zip_file="$log_folder/${archive_month}.zip"
    zip -j "$zip_file" $files_to_archive
    # Remove archived files
    rm $files_to_archive
    echo "Archived logs to $zip_file"
else
    echo "No logs to archive before $cut_date"
fi