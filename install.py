import subprocess
import sys
import os
import shutil

def check_pip():
    try:
        # Test if pip is available
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def ensure_pip():
    if check_pip():
        return True

    print("pip module not found. Attempting to bootstrap pip using ensurepip...")
    try:
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
        if check_pip():
            return True
    except subprocess.CalledProcessError:
        pass
        
    print("\nFailed to bootstrap pip.")
    if sys.platform.startswith('linux'):
        print("Attempting to install pip using the system package manager (may require sudo password)...")
        if shutil.which('apt'):
            try:
                subprocess.check_call(['sudo', 'apt', 'update'])
                subprocess.check_call(['sudo', 'apt', 'install', '-y', 'python3-pip'])
                if check_pip(): return True
            except subprocess.CalledProcessError:
                pass
        elif shutil.which('dnf'):
            try:
                subprocess.check_call(['sudo', 'dnf', 'install', '-y', 'python3-pip'])
                if check_pip(): return True
            except subprocess.CalledProcessError:
                pass
        elif shutil.which('pacman'):
            try:
                subprocess.check_call(['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'])
                if check_pip(): return True
            except subprocess.CalledProcessError:
                pass
                
        print("\nFailed to automatically install pip.")
        print("On Linux, you often need to install pip via your system package manager.")
        print("For Ubuntu/Debian: sudo apt install python3-pip")
        print("For Fedora: sudo dnf install python3-pip")
        print("For Arch: sudo pacman -S python-pip")
    elif sys.platform == 'darwin':
        print("On macOS, consider installing Python via Homebrew: brew install python")
    else:
        print("Please install pip manually from https://pip.pypa.io/en/stable/installation/")
    return False

def main():
    # Get the path to req.txt in the same directory as this script
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'req.txt')
    
    if not os.path.exists(req_path):
        print(f"Error: {req_path} not found.")
        sys.exit(1)
        
    if not ensure_pip():
        sys.exit(1)

    print(f"Installing dependencies from {req_path}...")
    try:
        # Run: python -m pip install -r req.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_path])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("Standard install failed (possibly due to externally-managed-environment).")
        print("Retrying with --break-system-packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-r', req_path])
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\nAn error occurred while installing dependencies.")
            print("If you encountered a permissions error or an 'externally-managed-environment' error, try running:")
            print(f"  {sys.executable} -m pip install --user --break-system-packages -r req.txt")
            print("\nAlternatively, use a virtual environment (recommended):")
            print(f"  {sys.executable} -m venv venv")
            if os.name == 'nt':
                print(f"  venv\\Scripts\\activate")
            else:
                print(f"  source venv/bin/activate")
            print(f"  python -m pip install -r req.txt")
            sys.exit(1)

if __name__ == "__main__":
    main()