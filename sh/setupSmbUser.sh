#!/usr/bin/env bash
# setup_samba_user.sh
# Creates SMB user, formats disk, mounts it as user's home/share, configures Samba.
# Also supports full removal/cleanup of an existing SMB user + mount.

set -euo pipefail

# Abstracted variables (can be overridden via env)
USER_NAME="${SMB_USER:-bob}"
PASSWORD="${SMB_PASSWORD:-123456}"
MOUNTPOINT="/home/${USER_NAME}"
SHARE_NAME="${USER_NAME}"

#
# Helper Functions
#
require_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "Please run as root." >&2
    exit 1
  fi
}

backup_file() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  cp -a "$f" "${f}.bak.$(date +%Y%m%d%H%M%S)"
}

restart_samba() {
  # Try common service names; ignore failures to stay distro-agnostic
  systemctl restart smbd nmbd 2>/dev/null || true
  systemctl restart smb nmb 2>/dev/null || true
  service smbd restart 2>/dev/null || true
  service nmbd restart 2>/dev/null || true
  systemctl reload smb 2>/dev/null || true
}

install_samba() {
  echo "Installing Samba..."
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -y
    apt-get install -y samba
  elif command -v dnf >/dev/null 2>&1; then
    dnf install -y samba samba-common
    systemctl enable --now smb nmb || true
  elif command -v yum >/dev/null 2>&1; then
    yum install -y samba samba-common
    systemctl enable --now smb nmb || true
  elif command -v pacman >/dev/null 2>&1; then
    pacman -Sy --noconfirm samba
  else
    echo "Unsupported package manager. Install Samba manually." >&2
    exit 1
  fi
}

create_unix_user() {
  echo "Creating UNIX user '${USER_NAME}'..."
  if id -u "${USER_NAME}" >/dev/null 2>&1; then
    echo "User ${USER_NAME} already exists."
    usermod -d "${MOUNTPOINT}" -s /usr/sbin/nologin "${USER_NAME}" || true
  else
    useradd -m -d "${MOUNTPOINT}" -s /usr/sbin/nologin "${USER_NAME}"
  fi
  mkdir -p "${MOUNTPOINT}"
  chown -R "${USER_NAME}:${USER_NAME}" "${MOUNTPOINT}"
  chmod 700 "${MOUNTPOINT}"
}

remove_unix_user_and_group() {
  echo "Removing UNIX user '${USER_NAME}' (and primary group if empty)..."
  if id -u "${USER_NAME}" >/dev/null 2>&1; then
    # Do not rely on -r to delete a mounted FS; we unmount first elsewhere.
    userdel -r "${USER_NAME}" 2>/dev/null || userdel "${USER_NAME}" || true
  fi
  if getent group "${USER_NAME}" >/dev/null 2>&1; then
    # groupdel only works if group has no members
    groupdel "${USER_NAME}" 2>/dev/null || true
  fi
}

configure_samba() {
  echo "Configuring Samba share for '${USER_NAME}'..."
  SMB_CONF="/etc/samba/smb.conf"
  backup_file "$SMB_CONF"

  # Remove pre-existing block (if any)
  if grep -q "^\[${SHARE_NAME}\]" "$SMB_CONF"; then
    echo "Removing existing Samba share for '${USER_NAME}'..."
    awk -v share="^[[]${SHARE_NAME}[]]\$" '
      BEGIN{skip=0}
      $0 ~ share {skip=1; next}
      skip && $0 ~ /^\[/ {skip=0}
      !skip {print}
    ' "$SMB_CONF" > "${SMB_CONF}.tmp"
    mv "${SMB_CONF}.tmp" "$SMB_CONF"
  fi

  # Ensure [global]
  if ! grep -q "^\[global\]" "$SMB_CONF"; then
    cat >> "$SMB_CONF" <<'EOF'

[global]
   workgroup = WORKGROUP
   server string = Samba Server
   map to guest = Bad User
   dns proxy = no
EOF
  fi

  # Append share
  cat >> "$SMB_CONF" <<EOF

[${SHARE_NAME}]
   path = ${MOUNTPOINT}
   browseable = yes
   read only = no
   valid users = ${USER_NAME}
   force user = ${USER_NAME}
   create mask = 0660
   directory mask = 0770
   comment = ${USER_NAME}'s share
EOF

  (echo "${PASSWORD}"; echo "${PASSWORD}") | smbpasswd -a -s "${USER_NAME}"
  smbpasswd -e "${USER_NAME}" || true

  restart_samba
}

remove_samba_user_and_share() {
  echo "Removing SMB user and share for '${USER_NAME}'..."
  SMB_CONF="/etc/samba/smb.conf"
  backup_file "$SMB_CONF"

  # Remove SMB user from passdb (ignore if not present)
  smbpasswd -x "${USER_NAME}" 2>/dev/null || true
  # Some distros also have pdbedit; try to remove if exists
  command -v pdbedit >/dev/null 2>&1 && pdbedit -x "${USER_NAME}" 2>/dev/null || true

  # Remove the share block
  if [[ -f "$SMB_CONF" ]] && grep -q "^\[${SHARE_NAME}\]" "$SMB_CONF"; then
    awk -v share="^[[]${SHARE_NAME}[]]\$" '
      BEGIN{skip=0}
      $0 ~ share {skip=1; next}
      skip && $0 ~ /^\[/ {skip=0}
      !skip {print}
    ' "$SMB_CONF" > "${SMB_CONF}.tmp"
    mv "${SMB_CONF}.tmp" "$SMB_CONF"
  fi

  restart_samba
}

disk_setup() {
  local DISK_DEV="$1"
  echo "Setting up disk '${DISK_DEV}'..."

  if ! [[ -b "${DISK_DEV}" ]]; then
    echo "Disk '${DISK_DEV}' not found." >&2
    exit 1
  fi

  if mountpoint -q "${DISK_DEV}"; then
    echo "Disk '${DISK_DEV}' is already mounted." >&2
    exit 1
  fi

  if mountpoint -q "${MOUNTPOINT}"; then
    echo "Unmounting existing mount point at ${MOUNTPOINT}..."
    umount -l "${MOUNTPOINT}" || true
  fi

  echo "Formatting disk '${DISK_DEV}' with ext4..."
  mkfs.ext4 -F "${DISK_DEV}"

  local DISK_UUID
  DISK_UUID=$(blkid -o value -s UUID "${DISK_DEV}")
  local FSTAB_LINE="UUID=${DISK_UUID} ${MOUNTPOINT} ext4 defaults 0 0"
  local FSTAB_CONF="/etc/fstab"
  backup_file "$FSTAB_CONF"

  if grep -qE "[[:space:]]${MOUNTPOINT}[[:space:]]" "$FSTAB_CONF"; then
    echo "Replacing existing fstab entry for ${MOUNTPOINT}..."
    sed -i "s|^[^#].*[[:space:]]${MOUNTPOINT}[[:space:]].*|${FSTAB_LINE}|" "$FSTAB_CONF"
  else
    echo "Adding new fstab entry for ${MOUNTPOINT}..."
    echo "$FSTAB_LINE" >> "$FSTAB_CONF"
  fi

  systemctl daemon-reload || true

  echo "Mounting disk '${DISK_DEV}' to ${MOUNTPOINT}..."
  mkdir -p "${MOUNTPOINT}"
  mount "${DISK_DEV}" "${MOUNTPOINT}"

  chown -R "${USER_NAME}:${USER_NAME}" "${MOUNTPOINT}"
  chmod 700 "${MOUNTPOINT}"

  echo "Disk '${DISK_DEV}' successfully mounted to ${MOUNTPOINT}."
}

unmount_and_cleanup_mountpoint() {
  echo "Unmounting and cleaning mount point '${MOUNTPOINT}'..."
  # Unmount if mounted
  if mountpoint -q "${MOUNTPOINT}"; then
    umount -l "${MOUNTPOINT}" || true
  fi

  # Remove fstab entries for this mountpoint (non-comment lines only)
  local FSTAB_CONF="/etc/fstab"
  if [[ -f "$FSTAB_CONF" ]]; then
    backup_file "$FSTAB_CONF"
    sed -i "\|^[^#].*[[:space:]]${MOUNTPOINT}[[:space:]]|d" "$FSTAB_CONF"
    systemctl daemon-reload || true
  fi

  # Remove directory and any remaining contents
  if [[ -d "${MOUNTPOINT}" ]]; then
    rm -rf --one-file-system "${MOUNTPOINT}"
  fi
}

full_setup() {
  if [[ $# -eq 0 ]]; then
    echo "Error: --full-setup requires a disk device name (e.g., /dev/sdg)." >&2
    exit 1
  fi
  local DISK_DEV="$1"
  disk_setup "${DISK_DEV}"
  install_samba
  create_unix_user
  configure_samba
  echo "Done. Connect via SMB to //$(hostname -I 2>/dev/null | awk '{print $1}')/${SHARE_NAME} as user '${USER_NAME}'."
}

full_remove() {
  echo "Starting full removal/cleanup for user '${USER_NAME}'..."
  remove_samba_user_and_share
  unmount_and_cleanup_mountpoint
  remove_unix_user_and_group
  echo "Removal complete for user '${USER_NAME}'."
}

main() {
  require_root

  if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <option> [arguments]"
    echo "Options:"
    echo "  --install-samba             Installs the Samba package."
    echo "  --create-user               Creates the UNIX user."
    echo "  --configure-share           Configures the Samba share."
    echo "  --disk-setup <device>       Formats and mounts the specified disk."
    echo "  --full-setup <device>       Performs all setup steps."
    echo "  --remove-all                Removes SMB user/share, unmounts, cleans fstab, deletes UNIX user."
    echo
    echo "Environment variables:"
    echo "  SMB_USER                    Set the user name (default: bob)"
    echo "  SMB_PASSWORD                Set the password (default: 123456)"
    exit 1
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --install-samba)
        install_samba; shift ;;
      --create-user)
        create_unix_user; shift ;;
      --configure-share)
        configure_samba; shift ;;
      --disk-setup)
        shift
        [[ -n "${1:-}" ]] || { echo "Error: --disk-setup requires a disk device name (e.g., /dev/sdg)." >&2; exit 1; }
        disk_setup "$1"; shift ;;
      --full-setup)
        shift
        [[ -n "${1:-}" ]] || { echo "Error: --full-setup requires a disk device name (e.g., /dev/sdg)." >&2; exit 1; }
        full_setup "$1"; shift ;;
      --remove-all)
        full_remove; shift ;;
      *)
        echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
}

main "$@"
