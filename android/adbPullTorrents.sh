#!/bin/bash

# Define the paths
parent_folder="/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload"
destination_folder_on_host="/media/pi/ssd"
temp_file_list="torrents.txt"
sanitize_script="./formatFile.py"
format_flag=false

while getopts "d:f" opt; do
  case ${opt} in
    d ) destination_folder_on_host="$OPTARG" ;;
    f ) format_flag=true ;;
    * ) 
      echo "Usage: $0 [-d destination_folder]"
      exit 1;; 
  esac
done
shift $((OPTIND - 1))

echo "Destination folder set to: $destination_folder_on_host"
mkdir -p "$destination_folder_on_host"

# Clean up any existing temp file
> "$temp_file_list"

# Enable debugging
set -x
adb shell <<EOF > "$temp_file_list"
find "$parent_folder" -maxdepth 1 -type f -iname "*.torrent" | while read torrent_file; do
  # Get the directory and base name of the file
  dir=\$(dirname "\$torrent_file")
  base_name=\$(basename "\$torrent_file" .torrent)

  # Check if a folder with the same name exists in the same directory
  folder_exists=\$(find "\$dir" -maxdepth 1 -type d -name "\$base_name" | wc -l)

  # Get the file's modification time in seconds since epoch using stat
  file_mod_time=\$(stat -c %Y "\$torrent_file" 2>/dev/null)
  current_time=\$(date +%s)

  # Ensure file_mod_time is valid
  if [ -z "\$file_mod_time" ]; then
    continue
  fi

  # Calculate the age of the file in seconds (7 days = 604800 seconds)
  file_age=\$((current_time - file_mod_time))

  # Include the file if it's less than 1 week old and no folder with the same name exists
  if [ "\$file_age" -lt 604800 ] && [ "\$folder_exists" -eq 0 ]; then
    echo "\$torrent_file"
  fi
done
EOF

cat $temp_file_list

# Disable debugging
# set +x

# Now read the file paths and pull each file to the host machine
while IFS= read -r video_file <&3; do
  base_filename=$(basename "$video_file")

  if [ "$format_flag" = true ]; then
    corrected_path=$(python3 "$sanitize_script" "$destination_folder_on_host" "$base_filename")
  else
    corrected_path="$destination_folder_on_host/$base_filename"
  fi

  sanitized_filename=$(echo "$corrected_path" | sed 's/[][()|&;!]/_/g')
  echo "Pulling $video_file to $sanitized_filename"
  adb pull "$video_file" "$sanitized_filename"

  # Check if the adb pull command was successful
  if [ $? -eq 0 ]; then
    echo "Successfully pulled $video_file. Deleting from device."
    adb shell rm "\"$video_file\""  # Simplified, no additional quoting or escaping
  else
    echo "Failed to pull $video_file. Skipping deletion."
    if [ -f "$sanitized_filename" ]; then
      echo "Partial file exists. Deleting $sanitized_filename."
      rm "$sanitized_filename"
    fi
  fi
done 3< "$temp_file_list"