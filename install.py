import subprocess
import sys
import os
import shutil

# Vibrant Color Palette
V_PURPLE = "\x1b[38;2;189;147;249m"
V_CYAN   = "\x1b[38;2;139;233;253m"
V_GREEN  = "\x1b[38;2;80;250;123m"
V_PINK   = "\x1b[38;2;255;121;198m"
V_ORANGE = "\x1b[38;2;255;184;108m"
V_RED    = "\x1b[38;2;255;85;85m"
V_YELLOW = "\x1b[38;2;241;250;140m"
V_GREY   = "\x1b[38;2;98;114;164m"
V_RESET  = "\x1b[0m"
V_BOLD   = "\x1b[1m"

def check_pip():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def ensure_pip():
    if check_pip(): return True
    try:
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
        return check_pip()
    except: return False

def install_package(pkg, break_packages=False):
    cmd = [sys.executable, '-m', 'pip', 'install']
    if break_packages: cmd.append('--break-system-packages')
    cmd.append(pkg)
    try:
        # We allow errors to be caught but hide the verbose pip output to keep it clean
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def main():
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'req.txt')
    if not os.path.exists(req_path):
        print(f"  {V_RED}{V_BOLD}✖{V_RESET} {V_RED}Error: req.txt not found.{V_RESET}")
        return

    if not ensure_pip():
        print(f"  {V_RED}{V_BOLD}✖{V_RESET} {V_RED}Error: pip could not be initialized.{V_RESET}")
        return

    with open(req_path, 'r') as f:
        packages = [l.split('#')[0].strip() for l in f if l.strip() and not l.strip().startswith('#')]

    print(f"  {V_PURPLE}ℹ{V_RESET} {V_GREY}Orchestrating {V_PINK}{len(packages)}{V_GREY} system dependencies...{V_RESET}")
    
    # Phase 1: Bulk Install Attempt
    try:
        print(f"  {V_CYAN}⏳{V_RESET} {V_GREY}Attempting High-Speed Bulk Synchronization...{V_RESET}")
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', req_path, '--break-system-packages']
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  {V_GREEN}✅{V_RESET} {V_GREEN}{V_BOLD}ULTIMATE MATRIX DEPLOYED SUCCESSFULLY!{V_RESET}")
        return
    except:
        print(f"  {V_ORANGE}⚠️{V_RESET} {V_GREY}Bulk sync encountered a conflict. Switching to {V_CYAN}Detailed Resilient Mode{V_GREY}...{V_RESET}\n")

    # Phase 2: Detailed Individual Install
    colors = [V_CYAN, V_PURPLE, V_PINK, V_ORANGE, V_YELLOW]
    success_count = 0
    fail_count = 0
    
    for i, pkg in enumerate(packages):
        percent = int((i + 1) * 100 / len(packages))
        color = colors[i % len(colors)]
        
        # Displaying the attempt
        sys.stdout.write(f"  {color}⏳{V_RESET} {V_GREY}[{percent:>3}%] Syncing {V_BOLD}{pkg:<35}{V_RESET}")
        sys.stdout.flush()
        
        if install_package(pkg, break_packages=True):
            sys.stdout.write(f"\r  {V_GREEN}✅{V_RESET} {V_GREY}[{percent:>3}%] {V_GREEN}Installed {V_BOLD}{pkg:<35}{V_RESET}\n")
            success_count += 1
        else:
            sys.stdout.write(f"\r  {V_RED}❌{V_RESET} {V_GREY}[{percent:>3}%] {V_RED}Skipped   {V_BOLD}{pkg:<35}{V_RESET}\n")
            fail_count += 1
        sys.stdout.flush()
    
    print(f"\n  {V_GREEN}✅{V_RESET} {V_GREEN}Sync Complete: {V_BOLD}{success_count}{V_RESET} {V_GREEN}Success, {V_RED}{fail_count}{V_RESET} {V_GREEN}Skipped.{V_RESET}")
    if fail_count > 0:
        print(f"  {V_GREY}Notice: Some modules were bypassed due to architecture incompatibility.{V_RESET}\n")

if __name__ == "__main__":
    main()