#!/bin/bash
workingDir="$(dirname "$(dirname "$0")")"
# Let Docker handle logging by writing to stdout/stderr
echo "ADB listener script started at $(date)"

cd "$workingDir"
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi
script_to_run="$workingDir/android/adbPullVideo.sh"

# Give the container a moment to connect to the host's ADB server
sleep 5

while true; do
  echo "Checking for ADB server and devices..."

  # First, check if the server is even reachable and a device is connected
  server_state=$(adb get-state 2>/dev/null)
  if [ "$server_state" != "device" ]; then
      echo "ADB server not found or no device connected. State: '$server_state'. Retrying in 60s..."
      sleep 60
      continue
  fi

  # Get the list of connected and authorized devices
  # The 'device' state ensures we don't act on 'unauthorized' or 'offline' devices.
  connected_devices=$(adb devices | grep -w "device" | awk '{print $1}')

  # Check if any device is connected
  if [ -n "$connected_devices" ]; then
    for device in $connected_devices; do
        echo "Device detected: $device. Running pull script."
        bash "$script_to_run" -f
        # If the script should only run once per cycle, even with multiple devices, break here.
        break
    done
  else
    echo "No authorized devices found."
  fi

  # Wait for a short time before checking again
  echo "Check complete. Waiting 60 seconds."
  sleep 60
done
