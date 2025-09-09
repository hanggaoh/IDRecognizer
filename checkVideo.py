import os
import subprocess
import argparse
import platform
from logger_setup import get_logger
from utils.constants import video_extensions

logger = get_logger()

def is_raspberry_pi():
    """Detect if the system is a Raspberry Pi."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            if "Raspberry Pi" in f.read():
                return True
    except Exception:
        return False
    return False

def is_linux():
    """Check if the operating system is Linux."""
    return platform.system() == "Linux"

def install_mediainfo():
    """Install mediainfo on Linux if it is not already installed."""
    try:
        subprocess.run(["mediainfo", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        logger.debug("Mediainfo not found. Installing mediainfo...")
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "mediainfo"])

def check_video_files(folder_path, output_file):
    # Detect system type
    raspberry_pi = is_raspberry_pi()

    # Check and install mediainfo on Linux systems
    if is_linux():
        install_mediainfo()

    brokenFiles = []

    # Open output file in write mode
    with open(output_file, "w") as f_out:
        # Loop through each file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(tuple(video_extensions)):  # Adjust extensions if needed
                file_path = os.path.join(folder_path, filename)

                # Logging the start of file processing
                logger.debug(f"Processing file: {filename}")

                # If Raspberry Pi, use mediainfo if available, otherwise use ffmpeg
                if raspberry_pi:
                    try:
                        result = subprocess.run(
                            ["mediainfo", "--Inform=Video;%Duration%", file_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        duration = result.stdout.decode("utf-8").strip()

                        if not duration or "N/A" in duration:
                            # Log and write the file name if no valid duration is found
                            f_out.write(f"{filename}\n")
                            logger.debug(f"File {filename} has issues (no valid duration)")
                        else:
                            logger.debug(f"File {filename} passed metadata check")
                    except Exception as e:
                        f_out.write(f"Error processing {filename} with mediainfo: {str(e)}\n")
                        logger.debug(f"Error processing {filename} with mediainfo: {str(e)}")
                else:
                    # Use ffprobe for a faster, shallow check of video file validity
                    try:
                        result = subprocess.run(
                            [
                                "ffprobe",
                                "-v", "error",
                                "-select_streams", "v:0",
                                "-show_entries", "stream=codec_name,duration",
                                "-of", "default=noprint_wrappers=1:nokey=1",
                                file_path
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        output = result.stdout.decode("utf-8").strip()
                        if not output or result.returncode != 0:
                            f_out.write(f"{filename}\n")
                            brokenFiles.append(filename)
                            logger.debug(f"File {filename} has issues (ffprobe failed or missing metadata)")
                        else:
                            logger.debug(f"File {filename} passed shallow ffprobe check")
                    except Exception as e:
                        f_out.write(f"Error processing {filename} with ffprobe: {str(e)}\n")
                        logger.debug(f"Error processing {filename} with ffprobe: {str(e)}")

    print(f"Check completed. Results saved to {output_file}.")
    return brokenFiles

def main():
    # Argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Check video files for metadata issues.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing video files")
    parser.add_argument("output_file", type=str, help="Path to the output file for storing results")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete broken video files detected during the check"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the arguments
    brokenFiles = check_video_files(args.folder_path, args.output_file)
    if args.delete and brokenFiles:
        for filename in brokenFiles:
            file_path = os.path.join(args.folder_path, filename)
            try:
                os.remove(file_path)
                logger.info(f"Deleted broken file: {filename}")
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {str(e)}")

if __name__ == "__main__":
    main()
