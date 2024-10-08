#!/bin/bash

# Default device and mount point
DEFAULT_DEVICE="/dev/sda1"
DEFAULT_MOUNT_POINT="/media/pi/ssd"

# Use command-line arguments if provided
DEVICE=${1:-$DEFAULT_DEVICE}
MOUNT_POINT=${2:-$DEFAULT_MOUNT_POINT}

# Check if the device exists
if [ ! -b "$DEVICE" ]; then
    echo "Device $DEVICE not found!"
    exit 1
fi

# Check the filesystem type
FS_TYPE=$(blkid -o value -s TYPE "$DEVICE")
if [ -z "$FS_TYPE" ]; then
    echo "Could not determine filesystem type for $DEVICE."
    exit 1
fi
echo "Filesystem type of $DEVICE: $FS_TYPE"

# Check if the mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Mount point $MOUNT_POINT does not exist. Creating it."
    sudo mkdir -p "$MOUNT_POINT"
fi

# Mount the device
sudo mount "$DEVICE" "$MOUNT_POINT"

# Check if the mount was successful
if mountpoint -q "$MOUNT_POINT"; then
    echo "Successfully mounted $DEVICE to $MOUNT_POINT."
else
    echo "Failed to mount $DEVICE."
    exit 1
fi

# Add to /etc/fstab for automatic mounting at startup
FSTAB_ENTRY="$DEVICE $MOUNT_POINT $FS_TYPE defaults 0 2"
if ! grep -qF "$FSTAB_ENTRY" /etc/fstab; then
    echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab > /dev/null
    echo "Added entry to /etc/fstab for automatic mounting."
else
    echo "Entry already exists in /etc/fstab."
fi
