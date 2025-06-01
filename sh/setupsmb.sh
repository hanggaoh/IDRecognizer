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
movie_path="$SMB_MOVIES_PATH"
movie_user="$SMB_MOVIES_USER"
movie_user_password="$SMB_MOVIES_USER_PASSWORD"
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


echo "Creating default Samba configuration file..."
echo "
[homes]
    valid users = %S
    read only = no
    browseable = no
    writable = yes" | sudo tee /etc/samba/smb.conf


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

echo "Creating home for smb_user..."
if [ -d "/home/$smb_user" ]; then
    echo "Home directory for smb_user already exists."
    rm -rf /home/$smb_user/*
    echo "Cleared contents of /home/$smb_user."
else
    echo "Creating home directory for smb_user..."
    sudo mkdir -p /home/$smb_user
    sudo chown $smb_user:$smb_user /home/$smb_user
    sudo chmod 755 /home/$smb_user
fi
ln -s $ssd_path /home/$smb_user/ssd
ln -s $hdd_path /home/$smb_user/hdd

if [ -d "/home/$movie_user" ]; then
    echo "Home directory for movie_user already exists."
else
    echo "Creating home directory for movie_user..."
    sudo mkdir -p /home/$movie_user
    sudo chown $movie_user:$movie_user /home/$movie_user
    sudo chmod 755 /home/$movie_user
fi
ln -s $movie_path /home/$movie_user/movies

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
    browseable = no
    writable = yes
    create mask = 0775
    directory mask = 0775
    valid users = ${smb_user}
    force user = ${smb_user}
    admin users = ${smb_user}
    guest ok = no
    public = no

[hdd]
    path = ${hdd_path}
    browseable = no
    writable = yes
    create mask = 0775
    directory mask = 0775
    valid users = ${smb_user}
    force user = ${smb_user}
    admin users = ${smb_user}
    guest ok = no
    public = no

[logs]
    path = ${logs_path}
    browseable = no
    writable = yes
    create mask = 0775
    directory mask = 0775
    valid users = ${smb_user}
    force user = ${smb_user}
    admin users = ${smb_user}
    guest ok = no
    public = no

[movies]
    path = ${movie_path}
    browseable = no
    writable = yes
    create mask = 0775
    directory mask = 0775
    valid users = ${movie_user}
    force user = ${movie_user}
    force group = ${movie_user}
    guest ok = no
    public = no
    read only = no
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

# Set Samba user and password for movie user
if [ -n "$movie_user" ] && [ -n "$movie_user_password" ]; then
    echo "Setting Samba password for movie user '$movie_user'..."
    # Ensure the movie user exists
    if ! id "$movie_user" &>/dev/null; then
        sudo useradd -M -s /sbin/nologin "$movie_user"
    fi
    echo -ne "$movie_user_password\n$movie_user_password" | sudo smbpasswd -a -s "$movie_user"
else
    echo "Skipping movie user setup: SMB_MOVIES_USER or SMB_MOVIES_USER_PASSWORD not set."
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
