#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <parent_folder> <file_list.txt>"
  exit 1
fi

# Assign arguments to variables
parent_folder="$1"
input_file="$2"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "File list not found: $input_file"
  exit 1
fi

# Read the input file line by line
while IFS= read -r file; do
  # Construct the full file path
  full_file_path="$parent_folder/$file"
  
  # Check if the file exists
  if [ -f "$full_file_path" ]; then
    # Delete the file
    rm "$full_file_path"
    echo "Deleted: $full_file_path"
  else
    echo "File not found: $full_file_path"
  fi
done < "$input_file"