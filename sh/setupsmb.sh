#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Remove any existing Samba installation
echo "Removing any existing Samba installation..."
sudo apt remove --purge -y samba samba-common
sudo apt autoremove -y

# Install Samba
echo "Installing Samba..."
sudo apt update
sudo apt install -y samba

# Verify if smb.conf file exists; create it if necessary
if [ ! -f /etc/samba/smb.conf ]; then
    echo "Creating default Samba configuration file..."
    echo "[global]
        workgroup = WORKGROUP
        server string = %h server (Samba)
        netbios name = raspberrypi
        security = user
        map to guest = bad user
        dns proxy = no

    [homes]
        comment = Home Directories
        browseable = no
        writable = yes" | sudo tee /etc/samba/smb.conf
fi

# Create shared directories if they don't exist
echo "Creating shared directories..."
[ ! -d "/home/pi/ssd" ] && mkdir -p /home/pi/ssd
[ ! -d "/home/pi/smbshare" ] && mkdir -p /home/pi/smbshare

# Set permissions for the directories
echo "Setting permissions for the shared directories..."
sudo chown pi:pi /home/pi/ssd
sudo chown pi:pi /home/pi/smbshare
sudo chmod 2775 /home/pi/ssd
sudo chmod 2775 /home/pi/smbshare

# Backup current smb.conf
echo "Backing up the current Samba configuration..."
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Configure smb.conf to add shared directories
echo "Configuring Samba shares..."
sudo bash -c 'cat >> /etc/samba/smb.conf << EOF

[ssd]
   path = /media/pi/ssd
   browseable = yes
   writable = yes
   create mask = 0775
   directory mask = 0775
   valid users = pi

[smbshare]
   path = /home/pi/smbshare
   browseable = yes
   writable = yes
   create mask = 0775
   directory mask = 0775
   valid users = pi
EOF'

# Set Samba user and password for pi
if command_exists smbpasswd; then
    echo "Setting Samba password for user 'pi'..."
    sudo smbpasswd -a pi
else
    echo "Error: smbpasswd command not found. Samba may not be correctly installed."
    exit 1
fi

# Restart Samba services
echo "Restarting Samba services..."
if command_exists systemctl; then
    sudo systemctl restart smbd
    sudo systemctl restart nmbd
else
    echo "Error: systemctl command not found. Unable to restart Samba services."
    exit 1
fi

echo "Samba setup is complete. Directories /home/pi/ssd and /home/pi/smbshare are now shared."
