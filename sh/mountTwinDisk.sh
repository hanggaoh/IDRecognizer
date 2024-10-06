#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Install mergerfs if it is not installed
if ! command -v mergerfs &> /dev/null; then
    echo "mergerfs not found. Installing mergerfs..."
    apt-get update && apt-get install -y mergerfs
    if [ $? -ne 0 ]; then
        echo "Failed to install mergerfs"
        exit 1
    fi
fi

# Unmount previous mounts to ensure a clean state
umount -l /media/pi/sdb1 2>/dev/null
umount -l /media/pi/sdc1 2>/dev/null
umount -l /home/pi/smbshare 2>/dev/null

# Iterate over all provided arguments and mount each one
mount_points=()
for device in "$@"; do
    mount_point="/media/pi/$device"

    mkdir -p "$mount_point"

    # Mount using appropriate method (ntfs-3g for NTFS)
    mount_command="mount"
    fs_type=$(lsblk -no FSTYPE "/dev/$device")

    if [ "$fs_type" == "ntfs" ]; then
        mount_command="ntfs-3g"
    fi

    $mount_command "/dev/$device" "$mount_point"

    if [ $? -eq 0 ]; then
        echo "$device mounted successfully to $mount_point"
    else
        echo "Failed to mount $device"
        continue
    fi

    # Get UUID of the device
    uuid=$(blkid -s UUID -o value "/dev/$device")

    # Add entry to /etc/fstab if it doesn't already exist
    if ! grep -qs "$uuid" /etc/fstab; then
        echo "UUID=$uuid $mount_point $fs_type defaults,auto,users,rw,nofail 0 2" >> /etc/fstab
        echo "Added $device to /etc/fstab"
    else
        echo "$device is already present in /etc/fstab"
    fi

    mount_points+=("$mount_point")
done

# Wait to ensure all drives are mounted properly
sleep 2

# Combine mount points using mergerfs
if [ ${#mount_points[@]} -ge 2 ]; then
    combined_mount_point="/home/pi/smbshare"
    mkdir -p "$combined_mount_point"

    merged_paths=$(IFS=:; echo "${mount_points[*]}")

    # Confirm that all drives are mounted
    if mount | grep -qs "/media/pi/sdb1" && mount | grep -qs "/media/pi/sdc1"; then
        echo "Both drives are mounted, proceeding with mergerfs..."

        mergerfs "$merged_paths" "$combined_mount_point" -o defaults,allow_other,category.create=mfs,nonempty
        if [ $? -eq 0 ]; then
            echo "Mergerfs mounted successfully to $combined_mount_point"

            # Add mergerfs entry to /etc/fstab if it doesn't already exist
            if ! grep -qs "mergerfs#$merged_paths" /etc/fstab; then
                echo "mergerfs#$merged_paths $combined_mount_point fuse.mergerfs defaults,allow_other,category.create=mfs,nonempty 0 0" >> /etc/fstab
                echo "Added mergerfs entry to /etc/fstab"
            else
                echo "Mergerfs entry is already present in /etc/fstab"
            fi
        else
            echo "Failed to mount mergerfs"
        fi
    else
        echo "One or both drives are not mounted properly. Exiting..."
        exit 1
    fi
else
    echo "Not enough mount points for mergerfs. At least two are required."
fi
