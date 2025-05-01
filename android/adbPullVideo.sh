#!/bin/bash

# Define the paths
parent_folder="/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload"
destination_folder_on_host="/media/pi/ssd"
temp_file_list="videos.txt"
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
    adb shell rm "$video_file"
  else
    echo "Failed to pull $video_file. Skipping deletion."
    if [ -f "$sanitized_filename" ]; then
      echo "Partial file exists. Deleting $sanitized_filename."
      rm "$sanitized_filename"
    fi
  fi
done 3< "$temp_file_list"