#!/bin/bash

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

pi_user="$PI_USER"
hdd_path="${MOUNT_POINT:-/mnt/merged}"

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
        if mount | grep -q "/media/${pi_user}/$device"; then
            echo "Attempting to unmount /media/${pi_user}/$device..."
            umount -f "/media/${pi_user}/$device" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "/media/${pi_user}/$device unmounted successfully."
            else
                echo "Warning: Failed to unmount /media/${pi_user}/$device. It may be busy."
            fi
        fi
        # Check if the device is in /etc/fstab and remove the line if it exists
        if grep -q "/media/${pi_user}/$device" /etc/fstab; then
            echo "Removing /media/${pi_user}/$device from /etc/fstab..."
            sed -i "\|/media/${pi_user}/$device|d" /etc/fstab
            if [ $? -eq 0 ]; then
            echo "/media/${pi_user}/$device removed from /etc/fstab successfully."
            else
            echo "Warning: Failed to remove /media/${pi_user}/$device from /etc/fstab."
            fi
        fi

        if grep -q "$(blkid -s UUID -o value /dev/$device)" /etc/fstab; then
            echo "Removing UUID for /dev/$device from /etc/fstab..."
            sed -i "\|$(blkid -s UUID -o value /dev/$device)|d" /etc/fstab
            if [ $? -eq 0 ]; then
            echo "UUID for /dev/$device removed from /etc/fstab successfully."
            else
            echo "Warning: Failed to remove UUID for /dev/$device from /etc/fstab."
            fi
        fi
        done

    # Check if smbshare is mounted
    if mount | grep -q $hdd_path; then
        echo "Attempting to unmount $hdd_path..."
        umount -f $hdd_path 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "$hdd_path unmounted successfully."
        else
            echo "Warning: Failed to unmount $hdd_path. It may be busy."
        fi
    fi
}

# Mount each device and add to fstab using UUID
mount_device() {
    local device="$1"
    local mount_point="/media/${pi_user}/${device}"

    echo "Mounting /dev/$device to $mount_point..."

    mkdir -p "$mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create mount point for $device"
        exit 1
    fi

    local fs_type=$(lsblk -no FSTYPE "/dev/$device")
    local mount_command="mount"

    # Set ownership and permissions for the mount point
    if [ "$fs_type" == "exfat" ]; then
        mount_opts="uid=${pi_user},gid=${pi_user},umask=002"
        $mount_command -o $mount_opts "/dev/$device" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to mount $device with exfat options"
            exit 1
        fi
        chown "${pi_user}:${pi_user}" "$mount_point"
        chmod 775 "$mount_point"
    elif [ "$fs_type" == "ntfs" ]; then
        mount_opts="uid=${pi_user},gid=${pi_user},umask=002"
        $mount_command -o $mount_opts "/dev/$device" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to mount $device with ntfs options"
            exit 1
        fi
        chown "${pi_user}:${pi_user}" "$mount_point"
        chmod 775 "$mount_point"
    elif [ "$fs_type" == "ext4" ] || [ "$fs_type" == "ext3" ] || [ "$fs_type" == "ext2" ]; then
        $mount_command "/dev/$device" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to mount $device with ext* options"
            exit 1
        fi
        chown "${pi_user}:${pi_user}" "$mount_point"
        chmod 775 "$mount_point"
    fi
    
    echo "Writing $device to /etc/fstab for automatic mounting at startup using UUID..."
    local uuid=$(blkid -s UUID -o value "/dev/$device")
    local fstab_opts="defaults,auto,users,rw,nofail"

    # Add user/group options for exfat and ntfs to ensure pi_user has rw access after reboot
    if [ "$fs_type" == "exfat" ] || [ "$fs_type" == "ntfs" ]; then
        fstab_opts="${fstab_opts},uid=${pi_user},gid=${pi_user},umask=002"
    fi

    if ! grep -qs "UUID=$uuid" /etc/fstab; then
        echo "UUID=$uuid $mount_point $fs_type $fstab_opts 0 2" >> /etc/fstab
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

# Combine mount points using mergerfs
combine_mount_points() {
    local combined_mount_point="$hdd_path"
    echo "combined_mount_point: $combined_mount_point"

    mkdir -p "$combined_mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create combined mount point"
        exit 1
    fi

    # Join all mount points with colon
    local mergerfs_sources
    mergerfs_sources=$(IFS=:; echo "${mount_points[*]}")

    echo "Running: mergerfs \"$mergerfs_sources\" \"$combined_mount_point\" -o defaults,allow_other,category.create=ff,moveonenospc=true,nonempty"
    mergerfs "$mergerfs_sources" "$combined_mount_point" -o defaults,allow_other,category.create=ff,moveonenospc=true,nonempty
    if [ $? -ne 0 ]; then
        echo "Error: Failed to mount mergerfs $mergerfs_sources"
        exit 1
    fi

    # Pass all sources to the systemd unit
    create_systemd_unit "$mergerfs_sources" "$combined_mount_point"

    echo "Mergerfs mounted successfully with preferred drive at $preferred_mount"
}

# Create systemd unit for mergerfs mount
create_systemd_unit() {
local mergerfs_sources="$1"
    local combined_mount_point="$2"

    mkdir -p "$combined_mount_point"

    cat <<EOF > /etc/systemd/system/mergerfs-combined.service
[Unit]
Description=MergerFS Service for $combined_mount_point
Requires=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/mergerfs "$mergerfs_sources" "$combined_mount_point" -o defaults,allow_other,category.create=ff,moveonenospc=true,nonempty
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable mergerfs-combined.service
    systemctl start mergerfs-combined.service

    echo "Systemd service for mergerfs mount created and enabled."
}

clear_mergerfs_mount() {
    local unit_name="mergerfs-combined.service"
    echo "Disabling and removing $unit_name..."

    sudo systemctl stop "$unit_name"
    sudo systemctl disable "$unit_name"
    sudo rm -f "/etc/systemd/system/$unit_name"
    sudo systemctl daemon-reload

    echo "$unit_name has been disabled and removed."
}

# Main function
main() {
    check_root
    install_mergerfs
    # Check for -u (unmount only) flag and filter it from device list
    unmount_only=false
    devices=()
    for arg in "$@"; do
        if [ "$arg" == "-u" ]; then
            unmount_only=true
        else
            devices+=("$arg")
        fi
    done

    echo "Cleaning previous mounts: ${devices[@]}"
    clean_previous_mounts "${devices[@]}"
    clear_mergerfs_mount

    if $unmount_only; then
        echo "Unmount-only mode enabled. Exiting after cleaning previous mounts."
        exit 0
    fi
    

    mount_points=()
    for device in "${devices[@]}"; do
        mount_device "$device"
    done

    sleep 2  # Wait to ensure mounts are stable

    if [ ${#mount_points[@]} -ge 2 ]; then
        combine_mount_points
    else
        echo "Error: Not enough mount points for mergerfs. At least two are required."
        exit 1
    fi
}

# Run the main function with all passed arguments (e.g., sdb sdc)
main "$@"
