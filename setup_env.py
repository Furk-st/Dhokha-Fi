import os
import subprocess
import sys

VENV_DIR = "venv"

def create_virtual_env():
    """Creates a Python virtual environment if it doesn't exist."""
    if not os.path.exists(VENV_DIR):
        print("[*] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR])
        print("[+] Virtual environment created successfully.")
    else:
        print("[!] Virtual environment already exists.")

def activate_virtual_env():
    """Activates the virtual environment."""
    activate_script = f"source {VENV_DIR}/bin/activate"
    if sys.platform == "win32":
        activate_script = f"{VENV_DIR}\\Scripts\\activate"

    print(f"[*] Run the following command to activate your virtual environment:\n{activate_script}")

def install_requirements():
    """Installs dependencies from requirements.txt."""
    print("[*] Installing dependencies from requirements.txt...")
    subprocess.run([f"{VENV_DIR}/bin/python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([f"{VENV_DIR}/bin/python", "-m", "pip", "install", "-r", "requirements.txt"])
    print("[+] Dependencies installed successfully.")

if __name__ == "__main__":
    create_virtual_env()
    install_requirements()
    activate_virtual_env()
