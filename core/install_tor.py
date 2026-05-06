__version__ = "1.0.0"
__description__ = "Cross-platform helper to install Tor on macOS, Linux, and Windows."
__author__ = "Souvik"
__website__ = "https://github.com/SouvikNandi1/Velora"

import glob
import os
import platform
import shlex
import shutil
import subprocess
import sys
import webbrowser


def is_command_available(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(command, check: bool = False, shell: bool = False) -> subprocess.CompletedProcess:
    print(f"Running: {' '.join(command) if isinstance(command, (list, tuple)) else command}")
    return subprocess.run(command, check=check, shell=shell)


def require_sudo(command):
    if os.name != "nt" and os.geteuid() != 0:
        return ["sudo"] + command
    return command


def prompt_yes_no(message: str) -> bool:
    answer = input(f"{message} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def find_brew_path() -> str | None:
    candidates = [
        shutil.which("brew"),
        "/opt/homebrew/bin/brew",
        "/usr/local/bin/brew",
        "/home/linuxbrew/.linuxbrew/bin/brew",
    ]
    candidates += glob.glob("/opt/homebrew/**/brew", recursive=True)
    candidates += glob.glob("/usr/local/**/brew", recursive=True)
    candidates += glob.glob("/home/linuxbrew/**/brew", recursive=True)
    seen = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def install_tor_mac() -> None:
    brew_path = find_brew_path()
    if brew_path:
        run_command([brew_path, "install", "tor"], check=True)
        return

    print("Homebrew is not installed on this system.")
    if not prompt_yes_no("Would you like to install Homebrew and then install Tor?"):
        print("Please install Homebrew first, then run this script again to install Tor.")
        print("If you prefer a manual install, visit https://www.torproject.org/download/")
        return

    run_command("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", check=True, shell=True)

    brew_path = find_brew_path()
    if not brew_path:
        print("Homebrew was installed, but the brew command is not yet on PATH.")
        print("Try opening a new terminal or add Homebrew to your shell PATH, then rerun this script.")
        print("Common paths: /opt/homebrew/bin/brew or /usr/local/bin/brew")
        print("For zsh, add this to ~/.zprofile or ~/.zshrc:")
        print("  eval \"$(/opt/homebrew/bin/brew shellenv)\"")
        return

    run_command([brew_path, "install", "tor"], check=True)

    if os.path.dirname(brew_path) not in os.environ.get("PATH", ""):
        os.environ["PATH"] = os.path.dirname(brew_path) + os.pathsep + os.environ.get("PATH", "")


def install_tor_linux() -> None:
    package_managers = [
        ("apt-get", ["apt-get", "update"], ["apt-get", "install", "-y", "tor"]),
        ("dnf", None, ["dnf", "install", "-y", "tor"]),
        ("yum", None, ["yum", "install", "-y", "tor"]),
        ("pacman", ["pacman", "-Sy"], ["pacman", "-S", "--noconfirm", "tor"]),
        ("zypper", None, ["zypper", "install", "-y", "tor"]),
        ("emerge", None, ["emerge", "--ask", "net-anonymous/tor"]),
    ]

    for manager, update_cmd, install_cmd in package_managers:
        if is_command_available(manager):
            if update_cmd:
                run_command(require_sudo(update_cmd), check=True)
            run_command(require_sudo(install_cmd), check=True)
            return

    print("No supported Linux package manager was detected.")
    print("Supported package managers: apt-get, dnf, yum, pacman, zypper, emerge.")
    print("Please install Tor with your distribution's package manager or visit https://www.torproject.org/download/")


def install_tor_windows() -> None:
    if is_command_available("winget"):
        for package_id in ["TorProject.Tor", "TorProject.TorBrowser"]:
            try:
                run_command([
                    "winget",
                    "install",
                    "--id",
                    package_id,
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ], check=True)
                return
            except subprocess.CalledProcessError:
                print(f"Winget package {package_id} was not available or failed to install.")

    if is_command_available("choco"):
        run_command(["choco", "install", "tor", "-y"], check=True)
        return

    if is_command_available("scoop"):
        run_command(["scoop", "install", "tor"], check=True)
        return

    print("No supported Windows package manager was found.")
    print("Install Chocolatey (https://chocolatey.org), Winget, or Scoop, then rerun this script.")
    print("Alternatively, download Tor manually from https://www.torproject.org/download/")


def main() -> None:
    system = platform.system().lower()
    print(f"Detected platform: {system}")

    try:
        if system == "darwin":
            install_tor_mac()
        elif system == "linux":
            install_tor_linux()
        elif system == "windows":
            install_tor_windows()
        else:
            print(f"Unsupported platform: {system}")
            print("Visit https://www.torproject.org/download/ for manual installation instructions.")
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}")
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("Installation interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()