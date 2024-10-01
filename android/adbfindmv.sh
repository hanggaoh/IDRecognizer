#!/bin/bash

# Define the paths
parent_folder="/sdcard/Android/data/com.xunlei.downloadprovider/files/ThunderDownload"
destination_folder="/sdcard/Movies/.A"

# Connect to Android device via ADB and start a shell session
adb shell <<EOF

for dir in $parent_folder/*; do
  if [ -d "\$dir" ]; then
    # Find the video file (assuming only one video file per folder)
    video_file=\$(ls "\$dir" | grep -E "\.mp4|\.avi|\.mkv|\.mov|\.flv|\.wmv|\.webm|\.mpg|\.mpeg|\.m4v|\.3gp|\.3g2|\.vob|\.ogv" | head -n 1)

    if [ -n "\$video_file" ]; then
      echo "Checking video file: \$video_file"
      
      # Use ls and grep to check for .js and .tail files
      js_exists=\$(ls -a "\$dir" | grep -Fc "\${video_file}.js")
      tail_exists=\$(ls -a "\$dir" | grep -Fc "\${video_file}.tail")

      # Check if the .js file exists
      if [ "\$js_exists" -gt 0 ]; then
        echo ".\${video_file}.js exists."
      else
        echo ".\${video_file}.js does not exist."
      fi

      # Check if the .tail file exists
      if [ "\$tail_exists" -gt 0 ]; then
        echo ".\${video_file}.tail exists."
      else
        echo ".\${video_file}.tail does not exist."
      fi
      
      # If neither .js nor .tail exists, prepare to move the file
      if [ "\$js_exists" -eq 0 ] && [ "\$tail_exists" -eq 0 ]; then
        # If the .js file does not exist, move the video file to the destination
        echo "Move video file: \$dir/\$video_file"
        # mv "\$dir/\$video_file" "$destination_folder/"
      fi
    fi
  fi
done

EOF

echo "Process completed."
