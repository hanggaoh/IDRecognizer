#!/bin/bash

# Directory to scan (current directory by default)
SCAN_DIR="${1:-.}" # Use first argument, or current directory if no argument provided
echo "Scanning for video files in: $SCAN_DIR"
# Check if ffprobe is installed
if ! command -v ffprobe &> /dev/null
then
    echo "Error: ffprobe is not installed. Please install ffmpeg (which includes ffprobe)."
    echo "On Ubuntu/Debian: sudo apt install ffmpeg"
    exit 1
fi

echo "Scanning directory: $SCAN_DIR"
echo "---------------------------------"

find "$SCAN_DIR" -type f \( -name "*.mp4" -o -name "*.mkv" -o -name "*.avi" -o -name "*.mov" \) -print0 | while IFS= read -r -d $'\0' video_file; do
    if [ -f "$video_file" ]; then
        CODEC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$video_file")
        if [ -n "$CODEC" ]; then # Check if CODEC variable is not empty
            echo "File: \"$video_file\" | Codec: $CODEC"
        else
            echo "File: \"$video_file\" | Codec: N/A (Could not determine or no video stream)"
        fi
    fi
done

echo "---------------------------------"
echo "Scan complete."