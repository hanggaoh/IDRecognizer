#!/bin/bash

if [[ "$1" == "-u" ]]; then
    echo "Uninstalling Deluge and cleaning up..."

    # Stop and disable services
    sudo systemctl stop deluged deluge-web
    sudo systemctl disable deluged deluge-web

    # Remove systemd service files
    sudo rm -f /etc/systemd/system/deluged.service
    sudo rm -f /etc/systemd/system/deluge-web.service

    # Reload systemd daemon
    sudo systemctl daemon-reload

    # Uninstall Deluge packages
    sudo apt remove --purge -y deluge deluged deluge-console deluge-web
    sudo apt autoremove -y

    # Remove Deluge config directory
    sudo rm -rf /home/pi/.config/deluge

    echo "Deluge has been uninstalled and all related files have been removed."
    exit 0
fi

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Deluge and required dependencies
sudo apt install -y deluge deluged deluge-console deluge-web

# Create a systemd service for Deluge daemon (deluged)
sudo tee /etc/systemd/system/deluged.service > /dev/null <<EOF
[Unit]
Description=Deluge Bittorrent Client Daemon
After=network-online.target

[Service]
Type=simple
User=pi
Group=pi
UMask=002
ExecStart=/usr/bin/deluged -d
Restart=on-failure
TimeoutStopSec=300

[Install]
WantedBy=multi-user.target
EOF

# Create a systemd service for Deluge Web UI (deluge-web)
sudo tee /etc/systemd/system/deluge-web.service > /dev/null <<EOF
[Unit]
Description=Deluge Bittorrent Client Web Interface
After=deluged.service

[Service]
Type=simple
User=pi
Group=pi
UMask=002
ExecStart=/usr/bin/deluge-web
Restart=on-failure
TimeoutStopSec=300

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the Deluge services
sudo systemctl enable deluged
sudo systemctl enable deluge-web
sudo systemctl start deluged
sudo systemctl start deluge-web

# Ensure the pi user owns the deluge config directory
sudo mkdir -p /home/pi/.config/deluge
sudo chown -R pi:pi /home/pi/.config/deluge

# Allow Deluge to manage files with user permissions
sudo chmod -R 775 /home/pi/.config/deluge

# Print success message with access information
echo "Deluge has been set up and is running."
echo "Access the Deluge Web UI at http://<RaspberryPi_IP>:8112"
