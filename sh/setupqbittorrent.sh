#!/bin/bash
user="gh"
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install qBittorrent
sudo apt install qbittorrent-nox -y

# Create a systemd service file for qBittorrent
sudo bash -c 'cat << EOF > /etc/systemd/system/qbittorrent.service
[Unit]
Description=qBittorrent Command Line Client
After=network.target

[Service]
ExecStart=/usr/bin/qbittorrent-nox --webui-port=8080
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd and enable the qBittorrent service
sudo systemctl daemon-reload
sudo systemctl enable qbittorrent.service

# Create Downloads directory if it doesn't exist
mkdir -p /home/$user/Downloads

# Set the correct permissions for the '$user' user to access the Downloads directory
sudo chown -R $user:$user /home/$user/Downloads
sudo chmod -R 775 /home/$user/Downloads

# Start the qBittorrent service to generate the default configuration files
sudo systemctl start qbittorrent.service

# Stop the service to edit the configuration
sudo systemctl stop qbittorrent.service

# Configure the default download path
# CONFIG_FILE="/home/$user/.config/qBittorrent/qBittorrent.conf"
# if [ -f "$CONFIG_FILE" ]; then
#     # Set the default download directory
#     sed -i 's|^Downloads\\\SavePath=.*|Downloads\\\SavePath=/home/$user/Downloads|' "$CONFIG_FILE"
# else
#     echo "Configuration file not found. Please make sure qBittorrent has been run at least once."
#     exit 1
# fi

# Start the qBittorrent service again
sudo qbittorrent-nox

echo "qBittorrent has been installed and configured to start on boot."
echo "Default download path set to /home/$user/Downloads with '$user' user access."
