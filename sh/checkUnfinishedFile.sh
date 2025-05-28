#!/bin/bash

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

ssd_path="$SSD_PATH"
hdd_path="$HDD_PATH"
echo "Checking for unfinished files in $ssd_path..."

sudo find "$ssd_path" -type f \( -empty -o ! -writable \) -print -delete

echo "Checking for unfinished files in $hdd_path..."
sudo find "$hdd_path" -type f \( -empty -o ! -writable \) -print -delete