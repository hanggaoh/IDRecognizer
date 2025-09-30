#!/bin/bash
workingDir="$(dirname "$(dirname "$0")")"

cd "$workingDir"
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi
# Define the paths
parent_folder="/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload"

destination_folder_on_host="$ADB_PULL_DESTINATION"
temp_file_list="$(mktemp /tmp/adb_videos_XXXXXX.txt)"
sanitize_script="./formatFile.py"
format_flag=false
skip_pull=0

while getopts "p:d:fs" opt; do
  case ${opt} in
    p ) parent_folder="$OPTARG" ;;
    d ) destination_folder_on_host="$OPTARG" ;;
    f ) format_flag=true ;;
    s ) skip_pull=1 ;;
    * ) 
      echo "$(timestamp) Usage: $0 [-d destination_folder] [-f] [-s]"
      exit 1;; 
    esac
  done
shift $((OPTIND - 1))

# Function to get the current timestamp
timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

echo "$(timestamp) Destination folder set to: $destination_folder_on_host"
mkdir -p "$destination_folder_on_host"
echo "$(timestamp) Parent folder set to: $parent_folder"
# Clean up any existing temp file
> "$temp_file_list"

# Capture the file list using adb shell and store it in a temporary file
adb shell <<EOF > "$temp_file_list"
# Define the parent folder on the remote shell
parent_folder="$parent_folder"

# Use find to list all video files, safely handling all characters
find "\$parent_folder" -type f \( \
  -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.mov" -o -iname "*.flv" -o -iname "*.wmv" -o -iname "*.webm" -o -iname "*.mpg" -o -iname "*.mpeg" -o -iname "*.m4v" -o -iname "*.3gp" -o -iname "*.3g2" -o -iname "*.vob" -o -iname "*.ogv" -o -iname "*.iso" -o -iname "*.ts" -o -iname "*.rmvb"  -o -iname "*.rm" \
  -o -iname "*.asf" -o -iname "*.f4v" -o -iname "*.divx" -o -iname "*.m2ts" -o -iname "*.mts" -o -iname "*.dat" -o -iname "*.amv" -o -iname "*.mpe" -o -iname "*.mp2" -o -iname "*.mpv" -o -iname "*.svi" -o -iname "*.mxf" -o -iname "*.roq" -o -iname "*.nsv" -o -iname "*.drc" -o -iname "*.ogm" -o -iname "*.wtv" -o -iname "*.yuv" -o -iname "*.viv" -o -iname "*.bik" -o -iname "*.evo" \
\) -print | while read -r video_file; do

  # Extract directory and base filename safely
  dir=\$(dirname "\$video_file")
  base_video_file=\$(basename "\$video_file")

  # Construct the full, absolute path for the unfinished files
  # Correct format: /dir/.basename.ext.tail
  js_file_path="\${dir}/.\${base_video_file}.js"
  tail_file_path="\${dir}/.\${base_video_file}.tail"

  # Use test -e (or [ -e ]) to check for existence
  if ! [ -e "\$js_file_path" ] && ! [ -e "\$tail_file_path" ]; then
    echo "\$video_file"
  fi
done
EOF

cat "$temp_file_list"

# Exit early if skip_pull is set
if [ $skip_pull -eq 1 ]; then
  echo "$(timestamp) Skipping video pull as --skip is provided."
  exit 0
fi

trap 'echo "Interrupted. Cleaning up $sanitized_filename"; [ -f "$sanitized_filename" ] && rm -f "$sanitized_filename"; exit 1' SIGINT

  # Now read the file paths and pull each file to the host machine
  while IFS= read -r video_file <&3; do
    base_filename=$(basename "$video_file")
    echo "$(timestamp) Processing $video_file"

    if [ "$format_flag" = true ]; then
      echo "$(timestamp) Formatting filename for $video_file"
      corrected_path=$(python3 "$sanitize_script" "$destination_folder_on_host" "$video_file")
    else
      echo "$(timestamp) No formatting applied to filename for $video_file"
      corrected_path="$destination_folder_on_host/$base_filename"
    fi

    sanitized_filename=$(echo "$corrected_path" | sed 's/[][()|&;!]/_/g')
    echo "$(timestamp) Pulling $video_file to $sanitized_filename"

    # Check if adb device is connected before pulling
    if ! adb get-state 1>/dev/null 2>&1; then
      echo "$(timestamp) No adb device detected. Skipping $video_file."
      continue
    fi

    adb shell "cat \"$video_file\"" | cat > "$sanitized_filename.partial"
    adb_status=$?

    # Check status and perform cleanup (using .partial suffix logic)
    if [ $adb_status -eq 0 ]; then
      mv "$sanitized_filename.partial" "$sanitized_filename"
      echo "$(timestamp) Successfully pulled $video_file. Deleting from device."
      adb shell "rm \"$video_file\""
      if adb shell "[ ! -f \"$video_file\" ]"; then
        echo "$(timestamp) Successfully deleted $video_file from the device."
      else
        echo "$(timestamp) Failed to delete $video_file from the device."
      fi
    else
      echo "$(timestamp) Failed to pull $video_file (ADB exit code $adb_status). Skipping deletion."
      if [ -f "$sanitized_filename.partial" ]; then
        echo "$(timestamp) Partial file exists. Deleting $sanitized_filename.partial."
        rm "$sanitized_filename.partial"
      elif [ -f "$sanitized_filename" ]; then 
        echo "$(timestamp) Partial file exists under final name. Deleting $sanitized_filename."
        rm "$sanitized_filename"
      fi
    fi
  done 3< "$temp_file_list"