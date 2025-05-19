#!/bin/bash

# Set up environment variables
QBITTORRENT_IMAGE="lscr.io/linuxserver/qbittorrent:latest"
CONTAINER_NAME="qbittorrent"
CONFIG_PATH="$(pwd)/qbittorrent/appdata"
DOWNLOADS_PATH="$(pwd)/downloads"

# Run qBittorrent container
docker run -d \
  --name=$CONTAINER_NAME \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Etc/UTC \
  -e WEBUI_PORT=8080 \
  -e TORRENTING_PORT=6881 \
  -p 8080:8080 \
  -p 6881:6881 \
  -p 6881:6881/udp \
  -v $CONFIG_PATH:/config \
  -v $DOWNLOADS_PATH:/downloads \
  --restart unless-stopped \
  $QBITTORRENT_IMAGE

echo "qBittorrent Docker container is now running!"
