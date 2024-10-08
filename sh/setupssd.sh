#!/bin/bash

# Default mount point
DEFAULT_MOUNT_POINT="/media/pi/ssd"

# Use command-line arguments for device; if not provided, use default sda1
DEVICE=${1:-/dev/sda1}
MOUNT_POINT=${2:-$DEFAULT_MOUNT_POINT}

# Check if the device exists
if [ ! -b "$DEVICE" ]; then
    echo "Device $DEVICE not found!"
    exit 1
fi

# Get the UUID of the device
UUID=$(blkid -o value -s UUID "$DEVICE")
if [ -z "$UUID" ]; then
    echo "Could not determine UUID for $DEVICE."
    exit 1
fi
echo "UUID of $DEVICE: $UUID"

# Check if the mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Mount point $MOUNT_POINT does not exist. Creating it."
    sudo mkdir -p "$MOUNT_POINT"
fi

# Mount the device using UUID
sudo mount UUID="$UUID" "$MOUNT_POINT"

# Check if the mount was successful
if mountpoint -q "$MOUNT_POINT"; then
    echo "Successfully mounted $DEVICE (UUID: $UUID) to $MOUNT_POINT."
else
    echo "Failed to mount $DEVICE."
    exit 1
fi

# Add to /etc/fstab for automatic mounting at startup using UUID
FSTAB_ENTRY="UUID=$UUID $MOUNT_POINT auto defaults 0 2"
if ! grep -qF "$FSTAB_ENTRY" /etc/fstab; then
    echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab > /dev/null
    echo "Added entry to /etc/fstab for automatic mounting."
else
    echo "Entry already exists in /etc/fstab."
fi

# Final check to ensure the device is mounted
if ! mountpoint -q "$MOUNT_POINT"; then
    echo "Error: $DEVICE (UUID: $UUID) is not mounted at $MOUNT_POINT."
    exit 1
fi
