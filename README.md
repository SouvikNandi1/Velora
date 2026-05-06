<p align="center">
  <img src="src/velora.png" width="128" height="128" alt="Velora Logo">
</p>

<h1 align="center">Velora Terminal</h1>

<p align="center">
  <b>Elevate Your Workflow with a Next-Generation Terminal Experience.</b><br>
  A high-fidelity PyQt6 terminal emulator featuring PTY isolation, glassmorphism UI, 
  and a powerful cloud-integrated package manager.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.75.0-bd93f9?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Security-E2E_Hardening-50fa7b?style=for-the-badge" alt="Security">
  <img src="https://img.shields.io/badge/Platform-Cross--Platform-8be9fd?style=for-the-badge" alt="Platform">
</p>

---

## ✨ Key Features

*   **🎨 Glassmorphism UI**: Stunning translucent backgrounds with dynamic opacity control and high-fidelity themes.
*   **🛡️ Hardened Security**: Automatic end-to-end encryption of all local source code and history. No plaintext Python resides on your disk.
*   **📦 Velora Package Manager (VPM)**: Instant access to a cloud-hosted registry of official and community-built terminal tools.
*   **⚡ PTY Isolation**: True Pseudo-Terminal support for interactive CLI apps like `nano`, `vim`, and `htop`.
*   **🛠️ Multi-Pane Workflow**: Native support for splitting tabs side-by-side or top-to-bottom.
*   **🌐 Remote Bootstrapper**: Single-command installation and automatic desktop shortcut generation.

---

## 🚀 Quick Start (One-Command Install)

Velora is designed to be installed and launched via a single link command. Choose your operating system below:

### 🐧 Linux & 🍎 macOS
Open your terminal and run:
```bash
curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3
```

### 🪟 Windows
Open **PowerShell** and run:
```powershell
curl -O bootstrap.py https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py; python bootstrap.py
```

---

## 📦 Managing Packages (VPM)

Velora uses its own package manager to keep your environment lightweight. By default, the `core/` folder is empty. Use `vpm` to populate it with verified tools.

| Command | Description |
| :--- | :--- |
| `vpm list` | View all available packages in the Velora Cloud. |
| `vpm install all` | **Recommended.** Installs the entire official verified suite. |
| `vpm info <pkg>` | View detailed metadata and description for a package. |
| `vpm check` | Check for updates for the terminal and your tools. |
| `vpm upgrade` | Perform an over-the-air update of the main Terminal app. |

---

## 🏗️ Technical Architecture

Velora is built on a modular, event-driven architecture designed for speed and security.

*   **Loader Stub Engine**: All `.py` files are encrypted using XOR+Base64. The app runs via memory-only decryption, preventing code tampering.
*   **PTY Proxy**: Intercepts OSC sequences for dynamic window resizing, ensuring `ncurses` apps scale perfectly.
*   **TrueColor Core**: Full 24-bit ANSI rendering support for modern CLI aesthetics.

For a deep dive, see the Blueprint Documentation.

---

## 🛠️ Development & Building

If you wish to build a standalone native executable (e.g., `.exe` on Windows), ensure you have the dependencies installed and run:

```bash
python install.py
python build.py
```

The build script will use `PyInstaller` to generate a secure, single-file binary that includes all required assets.

---

## 📂 Repository Structure

```text
├── bootstrap.py     # Remote deployment & hardening script
├── terminal.py      # Main GUI application (Encrypted loader)
├── vpm.py           # Velora Package Manager
├── install.py       # Dependency setup utility
├── build.py         # Native binary compilation script
├── src/             # UI Assets & Logos
├── blueprint.html   # Technical architecture docs
└── help.html        # Core program documentation
```
*Note: The `core/` directory is omitted from Git to prioritize privacy and cloud-based distribution via VPM.*

---

## 📜 License

Proprietary Software. All rights reserved to **qelaro.in**. 
Distributed "as-is" without warranty of any kind.

---

<p align="center">
  Built with ❤️ by <b>Souvik</b>
</p>