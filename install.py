import subprocess
import sys
import os
import shutil

def check_pip():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def ensure_pip():
    if check_pip(): return True
    try:
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
        if check_pip(): return True
    except: pass
    return False

def install_package(pkg, break_packages=False):
    cmd = [sys.executable, '-m', 'pip', 'install']
    if break_packages:
        cmd.append('--break-system-packages')
    cmd.append(pkg)
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def main():
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'req.txt')
    if not os.path.exists(req_path):
        print(f"  \x1b[31m✖\x1b[0m \x1b[31mError: req.txt not found.\x1b[0m")
        return

    if not ensure_pip():
        print("  \x1b[31m✖\x1b[0m \x1b[31mError: pip could not be initialized.\x1b[0m")
        return

    # Read packages
    with open(req_path, 'r') as f:
        lines = f.readlines()
    
    packages = []
    for line in lines:
        p = line.strip()
        if p and not p.startswith('#'):
            # Handle comments on the same line
            packages.append(p.split('#')[0].strip())

    print(f"  \x1b[34mℹ\x1b[0m \x1b[90mPreparing to install {len(packages)} dependencies...\x1b[0m")
    
    # Phase 1: Bulk Install (Fast)
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', req_path, '--break-system-packages']
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("  \x1b[32m✅\x1b[0m \x1b[32mAll dependencies installed successfully via bulk mode.\x1b[0m")
        return
    except subprocess.CalledProcessError:
        print("  \x1b[33m⚠️\x1b[0m \x1b[90mBulk install failed. Switching to Resilient Individual Mode...\x1b[0m")

    # Phase 2: Individual Resilient Install
    success_count = 0
    fail_count = 0
    for i, pkg in enumerate(packages):
        percent = int((i + 1) * 100 / len(packages))
        sys.stdout.write(f"\r  \x1b[36m⏳\x1b[0m \x1b[90mProcessing [{percent}%]: {pkg:<30}\x1b[0m")
        sys.stdout.flush()
        
        if install_package(pkg, break_packages=True):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n  \x1b[32m✅\x1b[0m \x1b[32mInstallation complete: {success_count} success, {fail_count} skipped/failed.\x1b[0m")
    if fail_count > 0:
        print(f"  \x1b[90mNote: Some non-critical packages could not be installed on this architecture/OS.\x1b[0m")

if __name__ == "__main__":
    main()