import time
import re
import pyperclip
from deluge_client import DelugeRPCClient

# Deluge connection setup
client = DelugeRPCClient('pinas.local', 58846, 'deluge', '687878')
client.connect()

# Regular expression pattern to detect magnet links
magnet_pattern = r'magnet:\?xt=urn:btih:[a-zA-Z0-9]*'

# Function to check if clipboard contains a magnet link
def check_clipboard_for_magnet():
    clipboard_content = pyperclip.paste()
    magnet_match = re.search(magnet_pattern, clipboard_content)
    if magnet_match:
        return magnet_match.group(0)  # Return the magnet link if found
    return None

# Main loop to continuously check the clipboard
print("Listening to clipboard for magnet links... Press Ctrl+C to stop.")
previous_clipboard_content = ""

try:
    while True:
        magnet_link = check_clipboard_for_magnet()
        
        if magnet_link and magnet_link != previous_clipboard_content:
            # Add the magnet link to Deluge
            client.call('core.add_torrent_magnet', magnet_link, {})
            print(f"Magnet link added: {magnet_link}")
            previous_clipboard_content = magnet_link
        
        time.sleep(5)  # Check clipboard every 5 seconds
except KeyboardInterrupt:
    print("\nStopped listening to clipboard.")

