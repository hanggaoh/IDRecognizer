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

    if mount | grep -q "$TARGET_FOLDER"; then
        echo "Attempting to unmount $TARGET_FOLDER..."
        umount -f "$TARGET_FOLDER" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "$TARGET_FOLDER unmounted successfully."
        else
            echo "Warning: Failed to unmount $TARGET_FOLDER. It may be busy."
        fi
    fi
}

# Mount each device and add it to fstab using UUID
mount_device() {
    local device="$1"
    local mount_point="/media/pi/$device"

    mkdir -p "$mount_point" || {
        echo "Error: Failed to create mount point for $device"
        exit 1
    }

    local fs_type=$(lsblk -no FSTYPE "/dev/$device")
    local mount_command="mount"
    if [ "$fs_type" == "ntfs" ]; then
        mount_command="ntfs-3g"
    fi

    $mount_command "/dev/$device" "$mount_point" || {
        echo "Error: Failed to mount $device"
        exit 1
    }

    local uuid=$(blkid -s UUID -o value "/dev/$device")
    if ! grep -qs "UUID=$uuid" /etc/fstab; then
        echo "UUID=$uuid $mount_point $fs_type defaults,auto,users,rw,nofail 0 2" >> /etc/fstab || {
            echo "Error: Failed to add $device to /etc/fstab"
            exit 1
        }
        echo "Added $device to /etc/fstab using UUID"
    else
        echo "$device is already present in /etc/fstab"
    fi

    echo "$device mounted successfully to $mount_point"
    mount_points+=("$mount_point")
}

# Create a folder inside each mounted disk
create_disk_folders() {
    for mount_point in "${mount_points[@]}"; do
        local folder_path="$mount_point/${TARGET_FOLDER##*/}"
        mkdir -p "$folder_path" || {
            echo "Error: Failed to create folder $folder_path"
            exit 1
        }
        echo "Created folder $folder_path"
    done
}

# Create and configure dynamic mergerFS service
create_mergerfs_service() {
    mkdir -p "$TARGET_FOLDER"
    chown pi:pi "$TARGET_FOLDER"

    # Merge only the specific folders created on each disk
    local merged_devices=$(IFS=:; echo "${mount_points[@]/%//${TARGET_FOLDER##*/}}")
    local service_name="mergerfs.${TARGET_FOLDER##*/}.service"
    local service_file="/etc/systemd/system/$service_name"

    echo "Creating mergerFS service at $service_file..."
    cat <<EOL > "$service_file"
[Unit]
Description=MergerFS Mount for ${TARGET_FOLDER##*/}
Requires=local-fs.target
After=local-fs.target

[Service]
Type=forking
ExecStart=/usr/bin/mergerfs $merged_devices $TARGET_FOLDER -o defaults,allow_other,use_ino,moveonenospc,category.create=ff

[Install]
WantedBy=multi-user.target
EOL

    systemctl daemon-reload
    systemctl enable "$service_name"
    systemctl start "$service_name"

    echo "MergerFS service $service_name created and started."
}

# Main function to run the entire process
main() {
    check_root
    install_mergerfs
    clean_previous_mounts "${DISK_IDENTIFIERS[@]}"

    mount_points=()
    for device in "${DISK_IDENTIFIERS[@]}"; do
        mount_device "$device"
    done

    create_disk_folders
    create_mergerfs_service

    echo "Setup complete! Merged storage is available at $TARGET_FOLDER"
}

# Check if at least one disk identifier is provided
if [ $# -lt 1 ]; then
    echo "Usage: sudo $0 <disk1> [<disk2> ...] [target_folder]"
    exit 1
fi

# Extract the last argument as the target folder if it's not a disk identifier
TARGET_FOLDER="/home/pi/${!#}"
if [[ "$TARGET_FOLDER" == "/home/pi/"* && $# -gt 1 ]]; then
    DISK_IDENTIFIERS=("${@:1:$#-1}")
else
    TARGET_FOLDER="/media/pi/smbshare"  # Default target folder
    DISK_IDENTIFIERS=("$@")
fi

# Run the main function with the provided disk identifiers
main
