import os
import subprocess

def install_system_packages():
    """Installs required system dependencies for Wi-Fi hacking."""
    print("[*] Updating package list...")
    os.system("sudo apt update")

    print("[*] Installing essential system dependencies...")
    os.system("""
        sudo apt install -y \
        aircrack-ng \
        hostapd \
        dnsmasq \
        iw \
        iptables \
        apache2 \
        python3-pip \
        tcpdump \
        net-tools
    """)

    print("[*] Ensuring Python dependencies are installed...")
    os.system("pip3 install --upgrade pip")

    print("[+] System dependencies installed successfully.")

if __name__ == "__main__":
    install_system_packages()

