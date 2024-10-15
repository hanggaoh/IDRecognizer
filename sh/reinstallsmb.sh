#!/bin/bash

# Update package list and reinstall Samba
echo "Updating package list and reinstalling Samba..."
sudo apt-get update
sudo apt-get purge -y samba
sudo apt-get install -y samba

# Backup existing Samba configuration
if [ -f /etc/samba/smb.conf ]; then
    echo "Backing up existing smb.conf..."
    sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
fi

# Generate a new smb.conf file with provided settings
echo "Creating new smb.conf..."

sudo bash -c 'cat > /etc/samba/smb.conf <<EOF
[global]
   workgroup = WORKGROUP
   server string = Raspberry Pi
   security = user
   map to guest = Bad User
   smb protocol = SMB3

[ssd]
   path = /media/pi/ssd
   browseable = yes
   writable = yes
   guest ok = no
   valid users = pi
   force user = pi
   create mask = 0775
   directory mask = 0775

[smbshare]
   path = /home/pi/smbshare
   browseable = yes
   writable = yes
   guest ok = no
   valid users = pi
   force user = pi
   create mask = 0775
   directory mask = 0775
EOF'

# Create the directories if they do not exist
echo "Creating shared directories..."
sudo mkdir -p /media/pi/ssd
sudo mkdir -p /home/pi/smbshare

# Set appropriate permissions
echo "Setting permissions..."
sudo chmod -R 775 /media/pi/ssd
sudo chmod -R 775 /home/pi/smbshare
sudo chown -R pi:pi /media/pi/ssd
sudo chown -R pi:pi /home/pi/smbshare

# Create Samba user 'pi' and set password
echo "Adding Samba user 'pi'..."
sudo smbpasswd -x pi 2>/dev/null  # Remove existing Samba user if any
sudo smbpasswd -a pi              # Add 'pi' user to Samba and prompt for a password
sudo smbpasswd -e pi              # Enable the 'pi' Samba account

# Restart Samba services
echo "Restarting Samba services..."
sudo systemctl restart smbd
sudo systemctl enable smbd

# Print completion message
echo "Samba setup with user 'pi' completed successfully!"
