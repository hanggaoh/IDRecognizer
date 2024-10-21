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
        if [ $? -eq 0 ]; then
            echo "/home/pi/smbshare unmounted successfully."
        else
            echo "Warning: Failed to unmount /home/pi/smbshare. It may be busy."
        fi
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

# Combine mount points using mergerfs
combine_mount_points() {
    local preferred_mount="${mount_points[0]}"
    local secondary_mount="${mount_points[1]}"
    local combined_mount_point="/home/pi/smbshare"

    mkdir -p "$combined_mount_point"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create combined mount point"
        exit 1
    fi

    mergerfs "$preferred_mount:$secondary_mount" "$combined_mount_point" -o defaults,allow_other,category.create=ff,moveonenospc=true,nonempty
    if [ $? -ne 0 ]; then
        echo "Error: Failed to mount mergerfs"
        exit 1
    fi

    # Add the mergerfs entry to a systemd mount unit file
    create_systemd_unit "$preferred_mount" "$secondary_mount" "$combined_mount_point"

    echo "Mergerfs mounted successfully with preferred drive at $preferred_mount"
}

# Create systemd unit for mergerfs mount
create_systemd_unit() {
    local preferred_mount="$1"
    local secondary_mount="$2"
    local combined_mount_point="$3"

    # Create the combined mount point directory if it doesn't exist
    mkdir -p "$combined_mount_point"

    # Write the systemd mount unit file
    cat <<EOF > /etc/systemd/system/home-pi-smbshare.mount
[Unit]
Description=MergerFS Mount for $combined_mount_point
Requires=network-online.target
After=network-online.target
[Mount]
What=$preferred_mount:$secondary_mount
Where=$combined_mount_point
Type=fuse.mergerfs
Options=defaults,allow_other,category.create=ff,moveonenospc=true,nonempty

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd daemon and enable the mount
    systemctl daemon-reload
    systemctl enable home-pi-smbshare.mount
    systemctl start home-pi-smbshare.mount

    echo "Systemd unit for mergerfs mount created and enabled."
}

# Main function
main() {
    check_root
    install_mergerfs
    clean_previous_mounts "$@"

    mount_points=()
    for device in "$@"; do
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
