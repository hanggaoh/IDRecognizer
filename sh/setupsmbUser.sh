#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Arguments
USERNAME=$1
PARENT_PATH=${2:-/media/pi/ssd}
USER_FOLDER="$PARENT_PATH/$USERNAME"

# Check if username is provided
if [ -z "$USERNAME" ]; then
  echo "Usage: $0 <username> [parent_path]"
  exit 1
fi

# Create the user
echo "Creating user: $USERNAME..."
sudo useradd -M -s /sbin/nologin "$USERNAME"

# Set the Samba password
echo "Setting Samba password for $USERNAME..."
(echo "Enter password for $USERNAME: "; sudo smbpasswd -a "$USERNAME")

# Create the directory for the user
echo "Creating directory: $USER_FOLDER..."
sudo mkdir -p "$USER_FOLDER"

# Set ownership and permissions
echo "Setting permissions..."
sudo chown "$USERNAME":"$USERNAME" "$USER_FOLDER"
sudo chmod 770 "$USER_FOLDER"

# Add the folder to the Samba configuration
echo "Adding Samba share for $USERNAME..."
SHARE_CONFIG="\n[$USERNAME]\n   path = $USER_FOLDER\n   valid users = $USERNAME\n   read only = no\n   browsable = yes\n   create mask = 0770\n   directory mask = 0770"
sudo bash -c "echo -e '$SHARE_CONFIG' >> /etc/samba/smb.conf"

# Restart Samba service
echo "Restarting Samba service..."
sudo systemctl restart smbd

echo "Samba setup complete for user: $USERNAME"
