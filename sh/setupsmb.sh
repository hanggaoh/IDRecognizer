#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi
# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

workingDir="$(cd "$(dirname "$0")/.." && pwd)"

pi_user="$PI_USER"
smb_user="$SMB_USER"
ssd_path="$SSD_PATH"
hdd_path="$HDD_PATH"
logs_path="$workingDir/logs"
smb_password="$SMB_PASSWORD"

# Check if required environment variables are set
if [ -z "$pi_user" ] || [ -z "$smb_user" ] || [ -z "$ssd_path" ] || [ -z "$hdd_path" ] || [ -z "$smb_password" ]; then
    echo "Error: One or more required environment variables are not set."
    echo "Please ensure PI_USER, SMB_USER, SSD_PATH, HDD_PATH, and SMB_PASSWORD are set."
    exit 1
fi

# Parse arguments
REINSTALL=0
for arg in "$@"; do
    case "$arg" in
        --reinstall|-r)
            REINSTALL=1
            ;;
    esac
done

# Function to check if Samba is installed
is_samba_installed() {
    dpkg -s samba >/dev/null 2>&1
}

if [ "$REINSTALL" -eq 1 ]; then
    echo "Removing any existing Samba installation..."
    sudo apt remove --purge -y samba samba-common
    sudo apt autoremove -y
fi

if ! is_samba_installed; then
    echo "Samba is not installed. Installing Samba..."
    sudo apt update
    sudo apt install -y samba
else
    echo "Samba is already installed."
fi

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
[ ! -d "$ssd_path" ] && mkdir -p $ssd_path
[ ! -d "$hdd_path" ] && mkdir -p $hdd_path

# Set permissions for the directories
echo "Setting permissions for the shared directories..."
sudo chown $pi_user:$pi_user $ssd_path
sudo chown $pi_user:$pi_user $hdd_path
sudo chmod 2775 $ssd_path
sudo chmod 2775 $hdd_path

# Set permissions for the logs directory
echo "Setting permissions for the logs directory..."
[ ! -d "$logs_path" ] && mkdir -p $logs_path
sudo chown $pi_user:$pi_user $logs_path
sudo chmod 2775 $logs_path

# Add smb_user to the group that owns the shared directories
sudo usermod -aG $pi_user $smb_user

# Set group ownership of the shared directories to $pi_user group
sudo chown -R $pi_user:$pi_user $ssd_path
sudo chown -R $pi_user:$pi_user $hdd_path
sudo chown -R $pi_user:$pi_user $logs_path

# Ensure permissions are set to 2775 (setgid)
sudo chmod 2775 $ssd_path
sudo chmod 2775 $hdd_path
sudo chmod 2775 $logs_path

# Backup current smb.conf
echo "Backing up the current Samba configuration..."
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Configure smb.conf to add shared directories
echo "Configuring Samba shares..."
sudo bash -c "cat >> /etc/samba/smb.conf << EOF
[global]
   unix extensions = no
   max protocol = SMB3
   min protocol = SMB2
   vfs objects = fruit streams_xattr  
   fruit:metadata = stream
   fruit:model = MacSamba
   fruit:veto_appledouble = no
   fruit:nfs_aces = no
   fruit:wipe_intentionally_left_blank_rfork = yes 
   fruit:delete_empty_adfiles = yes 
   fruit:posix_rename = yes 
   unix charset = UTF-8
   mangled names = yes
   mangling method = hash
   name resolve order = bcast host
   max stat cache size = 64

[ssd]
   path = ${ssd_path}
   browseable = yes
   writable = yes
   create mask = 0775
   directory mask = 0775
   valid users = ${smb_user}

[hdd]
   path = ${hdd_path}
   browseable = yes
   writable = yes
   create mask = 0775
   directory mask = 0775
   valid users = ${smb_user}
   
[logs]
   path = ${logs_path}
   browseable = yes
   writable = yes
   create mask = 0775
   directory mask = 0775
   valid users = ${smb_user}
EOF"

# Set Samba user and password for pi
if command_exists smbpasswd; then
    echo "Setting Samba password for user '$smb_user'..."
    if [ -z "$smb_password" ]; then
        echo "Error: smb_password environment variable is not set."
        exit 1
    fi
    # Ensure the Samba user exists
    if ! id "$smb_user" &>/dev/null; then
        sudo useradd -M -s /sbin/nologin "$smb_user"
    fi
    echo -ne "$smb_password\n$smb_password" | sudo smbpasswd -a -s "$smb_user"
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

echo "Samba setup is complete."
