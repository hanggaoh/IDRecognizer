#!/bin/bash
# Function to check if adb is installed
check_adb_installed() {
    if ! command -v adb &> /dev/null; then
        echo "ADB not found. Installing ADB..."
        sudo apt update
        sudo apt install -y android-tools-adb
    else
        echo "ADB is already installed."
    fi
}

# Check if adb is installed
check_adb_installed
# Create the service file
SERVICE_FILE="/etc/systemd/system/adbListen.service"

echo "[Unit]
Description=ADB Listen Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/IDRecognizer
ExecStart=/bin/bash /home/pi/IDRecognizer/android/listen_adb.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

# Reload the systemd manager configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable adbListen.service

# Start the service immediately (optional)
sudo systemctl start adbListen.service

# Check the service status
sudo systemctl status adbListen.service
