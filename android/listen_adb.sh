#!/bin/bash
workingDir="$(dirname "$(dirname "$0")")"
exec >> $workingDir/logs/listen_adb.log 2>&1
echo "Script started at $(date)"

cd "$workingDir"
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi
script_to_run="$workingDir/android/adbPullVideo.sh"

while true; do
  # Get the list of connected devices
  connected_devices=$(adb devices | grep -w "device" | awk '{print $1}')

  # Check if any device is connected
  if [ -n "$connected_devices" ]; then
    echo "Device detected: $connected_devices"
    # Run your script
    bash "$script_to_run" -f
  fi

  # Wait for a short time before checking again
  sleep 30
done
