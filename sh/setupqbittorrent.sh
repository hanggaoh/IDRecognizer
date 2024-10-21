#!/bin/bash

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
User=pi
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
mkdir -p /media/pi/ssd/Downloads/

# Set the correct permissions for the 'pi' user to access the Downloads directory
sudo chown -R pi:pi /media/pi/ssd/Downloads/
sudo chmod -R 775 /media/pi/ssd/Downloads/

# Start the qBittorrent service to generate the default configuration files
sudo systemctl start qbittorrent.service

# Stop the service to edit the configuration
sudo systemctl stop qbittorrent.service

# Configure the default download path
CONFIG_FILE="/home/pi/.config/qBittorrent/qBittorrent.conf"
if [ -f "$CONFIG_FILE" ]; then
    # Set the default download directory
    sed -i 's|^Downloads\\\SavePath=.*|Downloads\\\SavePath=/media/pi/ssd/Downloads/|' "$CONFIG_FILE"
else
    echo "Configuration file not found. Please make sure qBittorrent has been run at least once."
    exit 1
fi

# Start the qBittorrent service again
sudo systemctl start qbittorrent.service

echo "qBittorrent has been installed and configured to start on boot."
echo "Default download path set to /media/pi/ssd/Downloads/ with 'pi' user access."
