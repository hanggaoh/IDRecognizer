#!/bin/bash
# filepath: /home/gh/IDRecognizer/sh/formatNewDisk.sh

if [[ "$1" == "-u" ]]; then
    if [[ $# -ne 2 ]]; then
        echo "Usage: $0 -u <disk>"
        exit 1
    fi
    DISK="$2"
    PART="${DISK}1"
    UUID=$(sudo blkid -s UUID -o value "$PART")
    if mountpoint -q "/mnt/"*; then
        sudo umount "$PART" || true
    fi
    if [[ -n "$UUID" ]]; then
        sudo sed -i "/$UUID/d" /etc/fstab
        echo "Removed $PART from /etc/fstab and unmounted."
    else
        echo "UUID for $PART not found."
    fi
    exit 0
fi

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <disk> <label>"
    echo "Example: $0 /dev/sdh mountedDisk"
    exit 1
fi

DISK="$1"
LABEL="$2"
MOUNT_POINT="/mnt/$LABEL"

echo "Formatting $DISK with label $LABEL and mounting to $MOUNT_POINT..."


echo "WARNING: This will erase ALL data on $DISK!"
read -p "Type YES to continue: " confirm
if [[ "$confirm" != "YES" ]]; then
    echo "Aborted."
    exit 1
fi

# Unmount any mounted partitions
sudo umount ${DISK}?* || true

# Wipe old partition table
sudo wipefs -a "$DISK"

# Create new GPT and one big partition
sudo parted -s "$DISK" mklabel gpt
sudo parted -s "$DISK" mkpart primary ext4 0% 100%

# Wait for kernel to recognize new partition
sleep 2

# Format the new partition
sudo mkfs.ext4 -L "$LABEL" "${DISK}1"

# Create mount point
sudo mkdir -p "$MOUNT_POINT"

# Get UUID
UUID=$(sudo blkid -s UUID -o value "${DISK}1")

# Add to /etc/fstab if not already present
if ! grep -q "$UUID" /etc/fstab; then
    echo "UUID=$UUID $MOUNT_POINT ext4 defaults 0 2" | sudo tee -a /etc/fstab
fi

# Mount the partition
sudo mount "$MOUNT_POINT"

echo "Done! $DISK is now formatted, mounted at $MOUNT_POINT, and set to auto-mount."

