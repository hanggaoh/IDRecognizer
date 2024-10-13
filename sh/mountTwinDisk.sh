#!/bin/bash

# Ensure the script is run as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "Error: Please run as root"
        exit 1
    fi
}

# Install mergerfs if it is not installed
install_mergerfs() {
    if ! command -v mergerfs &> /dev/null; then
        echo "mergerfs not found. Installing mergerfs..."
        apt-get update && apt-get install -y mergerfs
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install mergerfs"
            exit 1
        fi
    fi
}

# Unmount any existing mounts
clean_previous_mounts() {
    # Loop through the provided devices
    for device in "$@"; do
        if mount | grep -q "/dev/$device"; then
            echo "Attempting to unmount /dev/$device..."
            umount -f "/dev/$device" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "/dev/$device unmounted successfully."
            else
                echo "Warning: Failed to unmount /dev/$device. It may be busy."
            fi
        fi
        if mount | grep -q "/media/pi/$device"; then
            echo "Attempting to unmount /media/pi/$device..."
            umount -f "/media/pi/$device" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "/media/pi/$device unmounted successfully."
            else
                echo "Warning: Failed to unmount /media/pi/$device. It may be busy."
            fi
        fi
    done
    
    # Check if smbshare is mounted
    if mount | grep -q "/home/pi/smbshare"; then
        echo "Attempting to unmount /home/pi/smbshare..."
        umount -f /home/pi/smbshare 2>/dev/null
        
        # Check for errors during unmount
        if [ $? -eq 0 ]; then
            echo "/home/pi/smbshare unmounted successfully."
        else
            echo "Warning: Failed to unmount /home/pi/smbshare. It may be busy."
        fi
    fi

    # Final check for remaining mounts specific to devices
    remaining_mounts=$(mount | grep -E "/dev/(${*// /|})|/media/pi/(${*// /|})|/home/pi/smbshare")
    if [ -n "$remaining_mounts" ]; then
        echo "Error: Some mounts could not be cleaned."
        echo "Remaining mounts:"
        echo "$remaining_mounts"
        exit 1
    else
        echo "All specified mounts have been cleaned successfully."
    fi
}

# Mount each device and add to fstab using UUID
mount_device() {
    local device="$1"
    local mount_point="/media/pi/$device"
    
    mkdir -p "$mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create mount point for $device"
        exit 1
    fi
    
    # Check filesystem type and select appropriate mount command
    local fs_type=$(lsblk -no FSTYPE "/dev/$device")
    local mount_command="mount"
    if [ "$fs_type" == "ntfs" ]; then
        mount_command="ntfs-3g"
    fi
    
    $mount_command "/dev/$device" "$mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to mount $device"
        exit 1
    fi

    # Use UUID in /etc/fstab to avoid issues on startup
    local uuid=$(blkid -s UUID -o value "/dev/$device")
    if ! grep -qs "UUID=$uuid" /etc/fstab; then
        echo "UUID=$uuid $mount_point $fs_type defaults,auto,users,rw,nofail 0 2" >> /etc/fstab
        if [ $? -ne 0 ]; then
            echo "Error: Failed to add $device to /etc/fstab"
            exit 1
        fi
        echo "Added $device to /etc/fstab using UUID"
    else
        echo "$device is already present in /etc/fstab"
    fi
    
    echo "$device mounted successfully to $mount_point"
    mount_points+=("$mount_point")
}

# Combine mount points using mergerfs with the preferred drive logic
combine_mount_points() {
    local preferred_mount="${mount_points[0]}"
    local secondary_mount="${mount_points[1]}"
    local combined_mount_point="/home/pi/smbshare"
    
    mkdir -p "$combined_mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create combined mount point"
        exit 1
    fi

    # Use preferred drive for most frequently used files, secondary drive for less frequent
    mergerfs "$preferred_mount:$secondary_mount" "$combined_mount_point" -o defaults,allow_other,category.create=ff,moveonenospc=true,nonempty
    if [ $? -ne 0 ]; then
        echo "Error: Failed to mount mergerfs"
        exit 1
    fi

    # Add mergerfs entry to fstab using the UUID of the preferred and secondary disks
    local preferred_uuid=$(blkid -s UUID -o value "/dev/$(basename "$preferred_mount")")
    local secondary_uuid=$(blkid -s UUID -o value "/dev/$(basename "$secondary_mount")")
    if ! grep -qs "mergerfs#$preferred_uuid:$secondary_uuid" /etc/fstab; then
        echo "mergerfs#UUID=$preferred_uuid:UUID=$secondary_uuid $combined_mount_point fuse.mergerfs defaults,allow_other,category.create=ff,moveonenospc=true,nonempty 0 0" >> /etc/fstab
        if [ $? -ne 0 ]; then
            echo "Error: Failed to add mergerfs entry to /etc/fstab"
            exit 1
        fi
        echo "Added mergerfs entry to /etc/fstab using UUID"
    else
        echo "Mergerfs entry is already present in /etc/fstab"
    fi

    echo "Mergerfs mounted successfully with preferred drive at $preferred_mount"
}

# Function to manage files based on access time using arguments for identifiers
manage_files() {
    local preferred_mount="/media/pi/$1"  # First argument as the preferred drive
    local secondary_mount="/media/pi/$2"  # Second argument as the secondary drive
    local combined_mount="/home/pi/smbshare"

    # Move frequently used files (accessed within last 7 days) to preferred drive
    find "$combined_mount" -type f -atime -7 -exec cp -u --preserve=all {} "$preferred_mount" \;

    # Move infrequently used files (not accessed in 30+ days) to secondary drive
    find "$combined_mount" -type f -atime +30 -exec mv -n {} "$secondary_mount" \;
}

create_cron_job() {
    local preferred_drive="$1"
    local secondary_drive="$2"

    local script_path="$(realpath "$0")"
    local parent_folder="$(dirname "$script_path")"
    local log_folder="$parent_folder/../logs"
    local log_file="$log_folder/cronjob.log"
    # Ensure the logs directory exists
    mkdir -p "$log_folder"

    local cron_job="0 2 * * * /bin/bash -c 'find /home/pi/smbshare -type f -atime -7 -exec cp -u --preserve=all {} /media/pi/$preferred_drive \; && find /home/pi/smbshare -type f -atime +30 -exec mv -n {} /media/pi/$secondary_drive \;' >> $log_file 2>&1"

    # Remove any existing cron job that includes 'find /home/pi/smbshare'
    crontab -l | grep -v -F "find /home/pi/smbshare" | crontab -

    # Check if the cron job already exists and add a new one if not
    if ! crontab -l | grep -q -F "$cron_job"; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        echo "Cron job created to manage file frequency"
    else
        echo "Cron job already exists"
    fi
}

# Main function to orchestrate mounting and cron job setup
main() {
    check_root
    install_mergerfs
    
    # Clean previous mounts
    clean_previous_mounts "$@"
    
    mount_points=()
    for device in "$@"; do
        mount_device "$device"
    done
    
    sleep 2  # Wait to ensure mounts are stable
    
    if [ ${#mount_points[@]} -ge 2 ]; then
        combine_mount_points
        create_cron_job "$1" "$2"  # Pass preferred and secondary drive identifiers to cron job
    else
        echo "Error: Not enough mount points for mergerfs. At least two are required."
        exit 1
    fi
}

# Run the main function with all passed arguments (e.g., sdb
