import os
import re
import json

def scan_wifi():
    """Scans for available Wi-Fi networks and returns a list of networks with details."""
    networks = []
    # Run the Wi-Fi scan command
    scan_result = os.popen("sudo iwlist wlan0 scan").read()

    # Split by cell (each cell represents a Wi-Fi network)
    cells = scan_result.split("Cell")

    for cell in cells[1:]:  # Skip the first split part (not needed)
        ssid = re.search(r'ESSID:"([^"]+)"', cell)
        mac = re.search(r'Address: ([\w:]+)', cell)
        signal = re.search(r'Signal level=(-\d+) dBm', cell)
        channel = re.search(r'Channel (\d+)', cell)

        if ssid and mac and signal and channel:
            networks.append({
                "SSID": ssid.group(1),
                "BSSID": mac.group(1),
                "Signal": f"{signal.group(1)} dBm",
                "Channel": channel.group(1)
            })
    return networks

if __name__ == "__main__":
    wifi_networks = scan_wifi()
    print(json.dumps(wifi_networks, indent=4))  # Output as JSON

