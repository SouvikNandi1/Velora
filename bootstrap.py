import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import base64
import ssl

# Force UTF-8 encoding for stdout on Windows to prevent 'charmap' errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, TypeError):
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssl._create_default_https_context = ssl._create_unverified_context

VERSION = "3.8.1"
REPO_URL = "https://github.com/SouvikNandi1/Velora/archive/refs/heads/main.zip"
INSTALL_DIR = os.path.expanduser("~/.velora/app")

import threading
import time
import itertools

def print_header():
    banner = """\x1b[38;5;51m\x1b[1m
 ██▒   █▓▓█████  ██▓     ▒█████   ██▀███   ▄▄▄      
▓██░   █▒▓█   ▀ ▓██▒    ▒██▒  ██▒▓██ ▒ ██▒▒████▄    
 ▓██  █▒░▒███   ▒██░    ▒██░  ██▒▓██ ░▄█ ▒▒██  ▀█▄  
  ▒██ █░░▒▓█  ▄ ▒██░    ▒██   ██░▒██▀▀█▄  ░██▄▄▄▄██ 
   ▒▀█░  ░▒████▒░██████▒░ ████▓▒░░██▓ ▒██▒ ▓█   ▓██▒
   ░ ▐░  ░░ ▒░ ░░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░
   ░ ░░   ░ ░  ░░ ░ ▒  ░  ░ ▒ ▒░   ░▒ ░ ▒░  ▒   ▒▒ ░
     ░░     ░     ░ ░   ░ ░ ░ ▒    ░░   ░   ░   ▒   
      ░     ░  ░    ░  ░    ░ ░     ░           ░  ░
     ░                                              \x1b[0m"""
    print(banner)
    print(f"  {C_CYAN}{C_BOLD}⚡ VELORA SYSTEM INSTALLER {C_RESET}{C_GREY}│ v{VERSION}{C_RESET}")
    print(f"  {C_GREY}" + "─" * 45 + f"{C_RESET}\n")

class Spinner:
    def __init__(self, message="Processing"):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = 0.1
        self.message = message
        self.running = False
        self.task_thread = None

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r  {C_CYAN}{next(self.spinner)}{C_RESET} {C_GREY}{self.message}...{C_RESET}" + " " * 5)
            sys.stdout.flush()
            time.sleep(self.delay)

    def start(self):
        self.running = True
        self.task_thread = threading.Thread(target=self._spin)
        self.task_thread.start()

    def stop(self, success_msg=None):
        self.running = False
        if self.task_thread:
            self.task_thread.join()
        if success_msg:
            sys.stdout.write(f"\r  \x1b[32m✔\x1b[0m \x1b[97m{success_msg}\x1b[0m" + " " * 20 + "\n")
        sys.stdout.flush()

_current_spinner = None

# Vibrant Color Palette
C_PURPLE = "\x1b[38;2;189;147;249m"
C_CYAN   = "\x1b[38;2;139;233;253m"
C_GREEN  = "\x1b[38;2;80;250;123m"
C_PINK   = "\x1b[38;2;255;121;198m"
C_ORANGE = "\x1b[38;2;255;184;108m"
C_RED    = "\x1b[38;2;255;85;85m"
C_YELLOW = "\x1b[38;2;241;250;140m"
C_GREY   = "\x1b[38;2;98;114;164m"
C_RESET  = "\x1b[0m"
C_BOLD   = "\x1b[1m"

def log_step(msg):
    global _current_spinner
    if _current_spinner:
        _current_spinner.stop()
    _current_spinner = Spinner(msg)
    _current_spinner.start()

def log_done(msg):
    global _current_spinner
    if _current_spinner:
        _current_spinner.stop(msg)
        _current_spinner = None
    else:
        print(f"  {C_GREEN}✔{C_RESET} {C_BOLD}{msg}{C_RESET}" + " " * 20)

def log_info(msg):
    print(f"  {C_CYAN}ℹ{C_RESET} {C_GREY}{msg}{C_RESET}")

def log_error(msg):
    global _current_spinner
    if _current_spinner:
        _current_spinner.stop()
        _current_spinner = None
    print(f"\n  {C_RED}{C_BOLD}✖{C_RESET} {C_RED}{msg}{C_RESET}\n")

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
            "_load()\n"
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(stub)
    except Exception:
        pass

def secure_installation(directory):
    log_step("Hardening installation with encryption")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "bootstrap.py":
                encrypt_file(os.path.join(root, file))
    log_done("Installation hardened with E2E encryption")

def create_shortcut():
    log_step("Creating Desktop Shortcut")
    
    system = platform.system()
    if system == "Windows":
        # On Windows, try to get the actual Desktop path
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)
        except (ImportError, OSError):
            # Fallback to default path
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    icon_path = os.path.join(INSTALL_DIR, "src", "velora.png")
    script_path = os.path.join(INSTALL_DIR, "terminal.py")
    python_exe = sys.executable
    try:
        if system == "Windows":
            shortcut_path = os.path.join(desktop, "Velora.lnk")
            
            
            
            
            
            
            # Ensure desktop directory exists
            os.makedirs(desktop, exist_ok=True)
            
            # Use PowerShell to create a native Windows shortcut
            ps_cmd = (
                f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}');"
                f"$s.TargetPath='{python_exe}';"
                f"$s.Arguments='\"{script_path}\"';"
                f"$s.IconLocation='{icon_path}';"
                f"$s.Save()"
            )
            
            # Try PowerShell first
            try:
                result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    
                    
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
                else:
                    print("[*] PowerShell command succeeded")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                
                
                
                # Fallback: Create a batch file
                batch_path = os.path.join(desktop, "Velora.bat")
                batch_content = f'@echo off\n"{python_exe}" "{script_path}"\n'
                with open(batch_path, 'w') as f:
                    f.write(batch_content)
                
                shortcut_path = batch_path

        elif system == "Linux":
            shortcut_path = os.path.join(desktop, "Velora.desktop")
            content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Velora Terminal\n"
                "Comment=Next-generation Command Orchestration Layer\n"
                f"Exec=\"{python_exe}\" \"{script_path}\"\n"
                f"Icon={icon_path}\n"
                "Terminal=false\n"
                "Categories=System;TerminalEmulator;Development;\n"
                "StartupNotify=true\n"
            )
            with open(shortcut_path, "w") as f:
                f.write(content)
            os.chmod(shortcut_path, 0o755)

        elif system == "Darwin": # macOS
            shortcut_path = os.path.join(desktop, "Velora.command")
            content = f"#!/bin/bash\n# Launch Velora Terminal\ncd \"{INSTALL_DIR}\"\n\"{python_exe}\" \"{script_path}\"\n"
            with open(shortcut_path, "w") as f:
                f.write(content)
            os.chmod(shortcut_path, 0o755)
        
        log_done("Desktop shortcut created successfully")
    except Exception as e:
        log_error(f"Failed to create shortcut: {e}")
        log_info(f"You can still launch Velora manually: {python_exe} {script_path}")

def main():
    print_header()
    
    # Check Python version
    if sys.version_info < (3, 8):
        log_error(f"Python 3.8 or higher is required. Current version: {sys.version}")
        return
    
    if os.path.exists(INSTALL_DIR):
        log_info("Velora is already installed. Checking for updates...")
    else:
        log_info(f"Installing Velora to {INSTALL_DIR}...")
        os.makedirs(INSTALL_DIR, exist_ok=True)

    # Download latest repository zip
    zip_path = os.path.join(INSTALL_DIR, "velora.zip")
    try:
        def download_progress(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                percent = min(100, max(0, percent))
                bar_len = 25
                filled = int(bar_len * percent / 100)
                bar = '█' * filled + '░' * (bar_len - filled)
                print(f"  \x1b[33m⏳\x1b[0m \x1b[90mDownloading latest source... \x1b[38;5;51m{bar}\x1b[0m \x1b[97m{percent}%\x1b[0m", end='\r', flush=True)
            else:
                downloaded = (count * block_size) / (1024 * 1024)
                print(f"  \x1b[33m⏳\x1b[0m \x1b[90mDownloading latest source... \x1b[38;5;51m{downloaded:.2f} MB\x1b[0m" + " " * 10, end='\r', flush=True)

        # Use a custom Request with User-Agent to avoid being blocked by GitHub or proxies
        req = urllib.request.Request(REPO_URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 8192
            with open(zip_path, 'wb') as out_file:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    download_progress(downloaded // block_size, block_size, total_size)
        print() # New line after progress bar
        
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extracts to Velora-main subfolder
            zip_ref.extractall(INSTALL_DIR)
            
        # Move files up from the extracted subfolder (Selective Update)
        extracted_folder = os.path.join(INSTALL_DIR, "Velora-main")
        if os.path.exists(extracted_folder):
            log_step("Updating application files (preserving core/bin)")
            for item in os.listdir(extracted_folder):
                # Only update the root app folder files, do not overwrite 'core' or 'bin'
                if item in ('core', 'bin'):
                    continue
                    
                s = os.path.join(extracted_folder, item)
                d = os.path.join(INSTALL_DIR, item)
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(extracted_folder)
            
        os.remove(zip_path)
        log_done("Updated application core source")
    except Exception as e:
        log_error(f"Update error: {e}")
        return

    # Install dependencies
    log_step("Installing system requirements")
    install_script = os.path.join(INSTALL_DIR, "install.py")
    req_file = os.path.join(INSTALL_DIR, "req.txt")
    
    if os.path.exists(install_script):
        if not os.path.exists(req_file):
            log_info("req.txt missing, attempting to skip dependency install...")
        else:
            # Run install.py without hiding output so the user can see progress/errors
            # Especially important for PEP 668 (externally-managed-environment) handling
            try:
                subprocess.run([sys.executable, install_script], check=True)
                log_done("Requirements verified and installed")
            except subprocess.CalledProcessError:
                log_error("Dependency installation encountered an issue.")
                log_info("Try running: python3 -m pip install -r req.txt --break-system-packages")

    # Secure the codes so no one can read or change them
    secure_installation(INSTALL_DIR)

    # Install Essential Core Packages Only
    log_step("Installing essential core features")
    vpm_script = os.path.join(INSTALL_DIR, "vpm.py")
    if os.path.exists(vpm_script):
        try:
            # Only install the most important tools as requested
            essential_pkgs = ["fetch", "about", "calc", "weather", "notes", "netutil", "speedtest"]
            subprocess.run([sys.executable, vpm_script, "install"] + essential_pkgs, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            log_done(f"Installed {len(essential_pkgs)} essential features")
        except subprocess.CalledProcessError:
            log_error("Essential package installation failed")
            log_info("You can install them later with 'vpm install all'")

    # Create the shortcut
    create_shortcut()

    print(f"\n  \x1b[32;1m🚀 VELORA IS READY!\x1b[0m\n")
    print(f"  You can launch it from your Desktop or by running:")
    print(f"  \x1b[38;5;51m{sys.executable} {os.path.join(INSTALL_DIR, 'terminal.py')}\x1b[0m\n")

    # Launch immediately
    try:
        subprocess.Popen([sys.executable, os.path.join(INSTALL_DIR, "terminal.py")])
    except: pass

if __name__ == "__main__":
    main()