#!/bin/bash

# Navigate to the directory where mvVideo.py is located
# Change this to the actual directory
# Run the Python script with the first destination
python3 ./mvVideo.py /media/pi/ssd /media/pi/hdd1/

# Check if the script was successful
if [ $? -ne 0 ]; then
    echo "Primary destination failed, attempting alternative destination..."
    # Run the Python script with an alternative destination
    python3 ./mvVideo.py /media/pi/ssd /media/pi/HDD/
fi