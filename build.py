import os
import sys
import subprocess
import platform
import shutil

def main():
    # Ensure we are executing in the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print(f"Building Velora Terminal natively for {platform.system()}...")
    
    # Ensure PyInstaller is installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    except subprocess.CalledProcessError:
        print("Standard pip install failed (possibly due to externally-managed-environment).")
        print("Retrying with --break-system-packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "pyinstaller"])
        except subprocess.CalledProcessError:
            print("\nFailed to install PyInstaller. Please install it manually or use a virtual environment.")
            sys.exit(1)
    
    sep = ';' if os.name == 'nt' else ':'
    
    # Run PyInstaller with all required data folders attached
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=Velora",
        f"--add-data=core{sep}core",
        f"--add-data=src{sep}src",
        "terminal.py"
    ]
    
    subprocess.check_call(cmd)
    
    # Automatically move the compiled binary to the root directory to replace the old one
    exe_name = "Velora.exe" if os.name == 'nt' else "Velora"
    dist_exe = os.path.join("dist", exe_name)
    
    if os.path.exists(dist_exe):
        try:
            if os.path.exists(exe_name):
                try: os.remove(exe_name)
                except OSError:
                    # Windows workaround: rename running executables so they can be replaced
                    old_exe = exe_name + ".old"
                    if os.path.exists(old_exe):
                        try: os.remove(old_exe)
                        except: pass
                    os.rename(exe_name, old_exe)
            shutil.copy2(dist_exe, exe_name)
            print(f"\n✅ Build complete! The new executable has replaced the old one in the main directory: {exe_name}")
        except Exception as e:
            print(f"\n✅ Build complete! The secure native executable is located in the 'dist' folder.")
            print(f"⚠️ Could not automatically replace '{exe_name}' in the root directory: {e}")
    else:
        print(f"\n✅ Build complete! The secure native executable is located in the 'dist' folder.")

if __name__ == "__main__":
    main()