#!/bin/bash
workingDir="$(dirname "$(dirname "$0")")"

source "${workingDir}/sh/utils.sh"

IMG_FOLDER="${IMG_FOLDER:-/home/gh/imgs}"
IMG_NAME="media.img"
IMG_PATH="${IMG_FOLDER}/${IMG_NAME}"
MOUNT_PATH="${SSD_PATH:-/mnt/media}"
IMG_SIZE="${IMG_SIZE:-100G}"

add_fstab_entry() {
    local img_path="$1"
    local mount_path="$2"
    echo "${img_path} ${mount_path} ext4 loop 0 0" | sudo tee -a /etc/fstab
}

echo "Using image folder: $IMG_FOLDER"

if [ ! -d "$IMG_FOLDER" ]; then
    echo "Image folder does not exist. Creating: $IMG_FOLDER"
    mkdir -p "$IMG_FOLDER"
fi


# Create image file if it doesn't exist
if [ ! -f "$IMG_PATH" ]; then
    echo "Creating image file at $IMG_PATH"
    sudo dd if=/dev/zero of="$IMG_PATH" bs=1G count=$(( ${IMG_SIZE%G} ))
    sudo mkfs.ext4 "$IMG_PATH"
fi

# Create mount directory if it doesn't exist
if [ ! -d "$MOUNT_PATH" ]; then
    echo "Creating mount directory at $MOUNT_PATH"
    sudo mkdir -p "$MOUNT_PATH"
fi

# Mount the image
sudo mount -o loop "$IMG_PATH" "$MOUNT_PATH"

add_fstab_entry "$IMG_PATH" "$MOUNT_PATH"