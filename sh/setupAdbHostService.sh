#!/bin/bash

# This script sets up a systemd service to run the ADB server on a Linux host,
# allowing Docker containers to connect to it over the network, similar to the macOS setup.

# Ensure the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Check for adb
if ! command -v adb &> /dev/null; then
    echo "ADB not found. Please install it first (e.g., 'sudo apt install adb')."
    exit 1
fi

# Define the user to run the service.
# It's crucial to run as a non-root user who owns the ~/.android/adbkey files.
# We use the SUDO_USER variable to get the name of the user who invoked sudo.
SERVICE_USER=${SUDO_USER:-pi}
echo "Configuring systemd service to run as user: $SERVICE_USER"

ADB_PATH=$(which adb)
SERVICE_FILE="/etc/systemd/system/adb-host.service"

echo "Creating systemd service file at $SERVICE_FILE..."

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=ADB Host Server for Docker
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
ExecStart=$ADB_PATH -a -P 5037 server nodaemon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling and starting adb-host.service..."
systemctl enable adb-host.service
systemctl start adb-host.service

echo "Service setup complete. You can check the status with:"
echo "sudo systemctl status adb-host.service"