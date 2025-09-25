# Use a base image with a recent OS and install dependencies.
# We'll use Debian as it's very common.
FROM debian:bullseye-slim

# Install dependencies: adb, python3, bash, and procps (for `ps` command if needed)
RUN apt-get update && \
    apt-get install -y adb python3 procps mediainfo bash && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the .env file for configuration
COPY .env .env

# Copy the necessary scripts and utility files
COPY android/listen_adb.sh ./android/
COPY android/adbPullVideo.sh ./android/
COPY formatFile.py .
COPY utils/ ./utils/
COPY matcher/ ./matcher/
COPY logger_setup.py ./logger_setup.py
COPY __init__.py ./__init__.py


# Create the logs directory and make scripts executable
RUN mkdir logs && \
    chmod +x ./android/listen_adb.sh && \
    chmod +x ./android/adbPullVideo.sh

# The command to run when the container starts
CMD ["/bin/bash", "./android/listen_adb.sh"]