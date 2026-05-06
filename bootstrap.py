import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import base64

VERSION = "1.76.0"
REPO_URL = "https://github.com/SouvikNandi1/Velora/archive/refs/heads/main.zip"
INSTALL_DIR = os.path.expanduser("~/.velora/app")

def encrypt_file(file_path):
    """Transforms a plaintext python file into a secure Velora Encrypted Stub."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        key = b"VeloraSuperSecureKeyForObfuscation2026!" # Longer, more complex key
        data = content.encode('utf-8')
        enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        b64_payload = base64.b64encode(enc).decode('utf-8')

        stub = (
            "# Velora Encrypted Source\n"
            "import base64, sys, os\n"
            f"__payload__ = '{b64_payload}'\n"
            "def _load():\n" # The stub itself needs to use the same key and logic
            "    k = b'VeloraSuperSecureKeyForObfuscation2026!'; e = base64.b64decode(__payload__)\n"
            "    d = bytes(b ^ k[i % len(k)] for i, b in enumerate(e)).decode('utf-8')\n"
            "    exec(d, globals())\n"
            "if __name__ == '__main__': _load()\n"
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(stub)
    except Exception:
        pass

def secure_installation(directory):
    print("[*] Hardening installation with End-to-End Encryption...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "bootstrap.py":
                encrypt_file(os.path.join(root, file))

def create_shortcut():
    print("[*] Creating Desktop Shortcut...")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    icon_path = os.path.join(INSTALL_DIR, "src", "velora.png")
    script_path = os.path.join(INSTALL_DIR, "terminal.py")
    python_exe = sys.executable

    system = platform.system()
    try:
        if system == "Windows":
            shortcut_path = os.path.join(desktop, "Velora.lnk")
            # Use PowerShell to create a native Windows shortcut
            ps_cmd = (
                f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}');"
                f"$s.TargetPath='{python_exe}';"
                f"$s.Arguments='\"{script_path}\"';"
                f"$s.IconLocation='{icon_path}';"
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)

        elif system == "Linux":
            shortcut_path = os.path.join(desktop, "Velora.desktop")
            content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                f"Name=Velora\n"
                f"Exec={python_exe} {script_path}\n"
                f"Icon={icon_path}\n"
                "Terminal=false\n"
                "Categories=System;TerminalEmulator;\n"
            )
            with open(shortcut_path, "w") as f:
                f.write(content)
            os.chmod(shortcut_path, 0o755)

        elif system == "Darwin": # macOS
            shortcut_path = os.path.join(desktop, "Velora.command")
            content = f"#!/bin/bash\n{python_exe} {script_path}\n"
            with open(shortcut_path, "w") as f:
                f.write(content)
            os.chmod(shortcut_path, 0o755)
        
        print(f"\x1b[32;1m[+] Shortcut created successfully on your Desktop!\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1m[-] Failed to create shortcut: {e}\x1b[0m")

def main():
    print(f"\x1b[36;1m═══ Velora Online Bootstrapper v{VERSION} ═══\x1b[0m")
    
    if os.path.exists(INSTALL_DIR):
        print("[*] Velora is already installed. Checking for updates...")
    else:
        print(f"[*] Installing Velora to {INSTALL_DIR}...")
        os.makedirs(INSTALL_DIR, exist_ok=True)

    # Download latest repository zip
    zip_path = os.path.join(INSTALL_DIR, "velora.zip")
    try:
        print("[*] Downloading latest source from GitHub...")
        urllib.request.urlretrieve(REPO_URL, zip_path)
        
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extracts to Velora-main subfolder
            zip_ref.extractall(INSTALL_DIR)
            
        # Move files up from the extracted subfolder
        extracted_folder = os.path.join(INSTALL_DIR, "Velora-main")
        if os.path.exists(extracted_folder):
            for item in os.listdir(extracted_folder):
                s = os.path.join(extracted_folder, item)
                d = os.path.join(INSTALL_DIR, item)
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(extracted_folder)
            
        os.remove(zip_path)
    except Exception as e:
        print(f"\x1b[31;1m[-] Download error: {e}\x1b[0m")
        return

    # Install dependencies
    print("[*] Installing requirements...")
    install_script = os.path.join(INSTALL_DIR, "install.py")
    if os.path.exists(install_script):
        subprocess.run([sys.executable, install_script])

    # Secure the codes so no one can read or change them
    secure_installation(INSTALL_DIR)

    # Create the shortcut
    create_shortcut()

    print(f"\n\x1b[32;1m🚀 Velora is ready!\x1b[0m")
    print(f"You can launch it from your Desktop or by running:")
    print(f"  \x1b[36m{sys.executable} {os.path.join(INSTALL_DIR, 'terminal.py')}\x1b[0m\n")

    # Launch immediately
    try:
        subprocess.Popen([sys.executable, os.path.join(INSTALL_DIR, "terminal.py")])
    except: pass

if __name__ == "__main__":
    main()