#!/bin/bash

# Navigate to the directory where mvVideo.py is located
# Change this to the actual directory
# Run the Python script with the first destination
workingDir="$(dirname "$(dirname "$0")")"

cd "$workingDir"
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

ssd_path="$SSD_PATH"
hdd_path="$HDD_PATH"

sudo python3 ./mvVideo.py $ssd_path $hdd_path 60