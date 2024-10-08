#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <disk_identifier> <mount_point>"
    exit 1
fi

# Arguments
disk_identifier=$1
mount_point=$2

# Detect filesystem type using blkid
fs_type=$(blkid -o value -s TYPE /dev/$disk_identifier)

# Check if blkid was able to find the filesystem type
if [ -z "$fs_type" ]; then
    echo "Could not detect filesystem type for /dev/$disk_identifier."
    exit 1
fi

echo "Detected filesystem type: $fs_type"

# Check if disk identifier and mount point exist in fstab
if grep -q "$disk_identifier" /etc/fstab; then
    echo "Disk identifier $disk_identifier is already in /etc/fstab."
    exit 0
fi

# Add the mount point if it doesn't exist
if ! grep -q "$mount_point" /etc/fstab; then
    echo "Adding $disk_identifier to /etc/fstab with filesystem type $fs_type..."

    # Create the entry in /etc/fstab based on detected filesystem type
    echo "/dev/$disk_identifier  $mount_point  $fs_type  defaults  0  0" | sudo tee -a /etc/fstab > /dev/null

    echo "Entry added to /etc/fstab:"
    echo "/dev/$disk_identifier  $mount_point  $fs_type  defaults  0  0"

    # Optionally, create the mount point directory if it doesn't exist
    if [ ! -d "$mount_point" ]; then
        sudo mkdir -p "$mount_point"
        echo "Mount point directory $mount_point created."
    fi

    # Reload systemd to recognize changes to fstab
    sudo systemctl daemon-reload

    # Mount the drive
    sudo mount -a

    echo "Disk $disk_identifier mounted at $mount_point."
else
    echo "Mount point $mount_point is already in /etc/fstab."
fi
