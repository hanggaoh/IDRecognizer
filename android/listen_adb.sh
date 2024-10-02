#!/bin/bash
exec >> /home/pi/IDRecognizer/logs/listen_adb.log 2>&1
echo "Script started at $(date)"
# Path to the script you want to run when a device is detected
script_to_run="/home/pi/IDRecognizer/android/adbPullVideo.sh"

while true; do
  # Get the list of connected devices
  connected_devices=$(adb devices | grep -w "device" | awk '{print $1}')

  # Check if any device is connected
  if [ -n "$connected_devices" ]; then
    echo "Device detected: $connected_devices"
    # Run your script
    bash "$script_to_run"
  fi

  # Wait for a short time before checking again
  sleep 30
done
