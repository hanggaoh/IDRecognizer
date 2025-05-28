#!/bin/bash

# Define the paths
parent_folder="/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload"

destination_folder_on_host="/media/pi/ssd"
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
find "$parent_folder" -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.mov" -o -iname "*.flv" -o -iname "*.wmv" -o -iname "*.webm" -o -iname "*.mpg" -o -iname "*.mpeg" -o -iname "*.m4v" -o -iname "*.3gp" -o -iname "*.3g2" -o -iname "*.vob" -o -iname "*.ogv" -o -iname "*.iso"  -o -iname "*.ts" \) | while read video_file; do
  dir=\$(dirname "\$video_file")
  base_video_file=\$(basename "\$video_file")

  js_exists=\$(ls -a "\$dir" | grep -Fc "\${base_video_file}.js")
  tail_exists=\$(ls -a "\$dir" | grep -Fc "\${base_video_file}.tail")

  if [ "\$js_exists" -eq 0 ] && [ "\$tail_exists" -eq 0 ]; then
    echo "\$video_file"
  # else
  #   # Check for .torrent file in the directory
  #   torrent_file=\$(find "\$dir" -maxdepth 1 -iname "*.torrent" | grep -o "[^/]*\.torrent" | head -n 1)
  #   if [ -n "\$torrent_file" ]; then
  #     echo "\$dir/\$torrent_file"
  #   fi
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

    # Use properly quoted paths for adb pull
    adb shell cat \"${video_file//\"/\\\"}\" | cat > "$sanitized_filename"

    # Check if the adb pull command was successful
    if [ $? -eq 0 ]; then
    echo "$(timestamp) Successfully pulled $video_file. Deleting from device."

    # Use properly quoted paths for adb rm
    adb shell "rm \"$video_file\""
    if adb shell "[ ! -f \"$video_file\" ]"; then
      echo "$(timestamp) Successfully deleted $video_file from the device."
    else
      echo "$(timestamp) Failed to delete $video_file from the device."
    fi
    else
    echo "$(timestamp) Failed to pull $video_file. Skipping deletion."
    if [ -f "$sanitized_filename" ]; then
      echo "$(timestamp) Partial file exists. Deleting $sanitized_filename."
      rm "$sanitized_filename"
    fi
    fi
  done 3< "$temp_file_list"
