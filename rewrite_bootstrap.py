import re

with open("/Users/souvik/Documents/velora/bootstrap.py", "r") as f:
    content = f.read()

helpers = """
def print_header():
    print(f"\\n\\x1b[38;5;51m\\x1b[1m⚡ VELORA SYSTEM INSTALLER \\x1b[0m\\x1b[90mv{VERSION}\\x1b[0m\\n")

def log_step(msg):
    print(f"  \\x1b[33m⏳\\x1b[0m \\x1b[90m{msg}...\\x1b[0m", end='\\r', flush=True)

def log_done(msg):
    print(f"  \\x1b[32m✔\\x1b[0m \\x1b[97m{msg}" + " " * 20)

def log_info(msg):
    print(f"  \\x1b[34mℹ\\x1b[0m \\x1b[90m{msg}\\x1b[0m")

def log_error(msg):
    print(f"\\n  \\x1b[31;1m✖\\x1b[0m \\x1b[31m{msg}\\x1b[0m\\n")
"""

content = content.replace('def encrypt_file(file_path):', helpers + '\ndef encrypt_file(file_path):')

content = content.replace('print("[*] Hardening installation with End-to-End Encryption...")', 'log_step("Hardening installation with encryption")')

# remove secure_installation done? No we can add it.
content = content.replace('encrypt_file(os.path.join(root, file))', 'encrypt_file(os.path.join(root, file))\n    log_done("Installation hardened with E2E encryption")')

content = content.replace('print("[*] Creating Desktop Shortcut...")', 'log_step("Creating Desktop Shortcut")')

# Remove powershell debug prints
content = re.sub(r'print\(f"\[\*\] (Desktop path|Shortcut path|Python exe|Script path|Icon path|Running PowerShell|PowerShell command succeeded|Created batch).*?"\)', '', content)
content = re.sub(r'print\("\[\*\] Falling back.*?"\)', '', content)
content = re.sub(r'print\(f"\[!\] PowerShell error.*?"\)', '', content)
content = re.sub(r'print\(f"\[!\] PowerShell stdout.*?"\)', '', content)
content = re.sub(r'print\(f"\[!\] PowerShell shortcut creation failed.*?"\)', '', content)

content = content.replace('print(f"\\x1b[32;1m[+] Shortcut created successfully on your Desktop!\\x1b[0m")', 'log_done("Desktop shortcut created successfully")')
content = content.replace('print(f"\\x1b[31;1m[-] Failed to create shortcut: {e}\\x1b[0m")', 'log_error(f"Failed to create shortcut: {e}")')
content = content.replace('print(f"\\x1b[33m[!] You can still launch Velora manually: {python_exe} {script_path}\\x1b[0m")', 'log_info(f"You can still launch Velora manually: {python_exe} {script_path}")')


content = content.replace('print(f"\\x1b[36;1m═══ Velora Online Bootstrapper v{VERSION} ═══\\x1b[0m")', 'print_header()')
content = content.replace('print(f"\\x1b[31;1m[-] Python 3.8 or higher is required. Current version: {sys.version}\\x1b[0m")', 'log_error(f"Python 3.8 or higher is required. Current version: {sys.version}")')

content = content.replace('print("[*] Velora is already installed. Checking for updates...")', 'log_info("Velora is already installed. Checking for updates...")')
content = content.replace('print(f"[*] Installing Velora to {INSTALL_DIR}...")', 'log_info(f"Installing Velora to {INSTALL_DIR}...")')

content = content.replace('print("[*] Downloading latest source from GitHub...")', 'log_step("Downloading latest source from GitHub")')
content = content.replace('os.remove(zip_path)', 'os.remove(zip_path)\n        log_done("Downloaded latest source from GitHub")')

content = content.replace('print(f"\\x1b[31;1m[-] Download error: {e}\\x1b[0m")', 'log_error(f"Download error: {e}")')

content = content.replace('print("[*] Installing requirements...")', 'log_step("Installing requirements")')
content = content.replace('subprocess.run([sys.executable, install_script])', 'subprocess.run([sys.executable, install_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n        log_done("Installed requirements")')

content = content.replace('print("[*] Installing core packages...")', 'log_step("Installing core packages")')
content = content.replace('subprocess.run([sys.executable, vpm_script, "install", "all"], check=True)', 'subprocess.run([sys.executable, vpm_script, "install", "all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)\n            log_done("Installed core packages")')
content = content.replace('print("[!] Core packages installation failed. You can install them later with \'vpm install all\'")', 'log_error("Core packages installation failed")\n            log_info("You can install them later with \'vpm install all\'")')

content = content.replace('print(f"\\n\\x1b[32;1m🚀 Velora is ready!\\x1b[0m")', 'print(f"\\n  \\x1b[32;1m🚀 VELORA IS READY!\\x1b[0m\\n")')
content = content.replace('print(f"You can launch it from your Desktop or by running:")', 'print(f"  You can launch it from your Desktop or by running:")')
content = content.replace('print(f"  \\x1b[36m{sys.executable} {os.path.join(INSTALL_DIR, \'terminal.py\')}\\x1b[0m\\n")', 'print(f"  \\x1b[38;5;51m{sys.executable} {os.path.join(INSTALL_DIR, \'terminal.py\')}\\x1b[0m\\n")')

with open("bootstrap_new.py", "w") as f:
    f.write(content)
