# Velora Terminal

<p align="center">
  <img src="src/velora.png" width="128" height="128" alt="Velora Logo">
</p>

**Elevate your workflow with a modern terminal experience.**

Velora is a PyQt6-powered terminal application with cloud-integrated package management, secure local execution, and a polished UI.

---

## 🚀 Highlights

- **Modern UI** with glassmorphism and theme support
- **Cloud package management** via `vpm`
- **Secure local files** using encrypted stubs
- **True PTY support** for `nano`, `vim`, `htop`, and other interactive tools
- **Local git helper** support with `git.py`

---

## 📥 Installation

### Linux / macOS

```bash
curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3
```

### Windows (PowerShell)

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py -OutFile bootstrap.py
python bootstrap.py
```

---

## 📦 Package Management (`vpm`)

Velora uses a cloud-backed package registry to keep the repo lightweight and secure.

| Command | Description |
| --- | --- |
| `vpm list` | Show available packages from the Velora registry |
| `vpm install <pkg>` | Install a package locally |
| `vpm install all` | Install the full official suite |
| `vpm info <pkg>` | Show package metadata and website |
| `vpm check` | Check for available app and package updates |
| `vpm upgrade` | Update the terminal app itself |

---

## 🔒 Secrets & Configuration

Velora avoids storing secrets in plain text in the repository.

Credentials may be provided by:

- `VELORA_SN_PROJECT_ID`
- `VELORA_SN_API_KEY`
- `~/.velora/vpm_secrets.json`

A secure fallback is also included for embedded operation without exposing raw keys in source.

---

## 🧰 Local Git Helper

A local helper script is available for faster commit and push workflows:

```bash
./git.py -m "Update to version vX.Y.Z"
```

If you omit `-m`, it generates a message from `version.txt`.

> `git.py` is ignored by the repository and is only for local use.

---

## 🏗️ Build from Source

To build a standalone executable:

```bash
python install.py
python build.py
```

This will package the application using `PyInstaller`.

---

## 📁 Repository Layout

```text
├── bootstrap.py      # Bootstrap installer and hardening script
├── terminal.py       # Main GUI terminal app
├── vpm.py            # Velora package manager
├── git.py            # Local git helper (ignored by git)
├── install.py        # Dependency setup utility
├── build.py          # Packaging script
├── src/              # UI assets and icons
├── blueprint.html    # Architecture documentation
├── help.html         # Core program docs
└── version.txt       # Release version history
```

`core/` is intentionally excluded from version control and populated via VPM.

---

## 📜 License

Proprietary software. All rights reserved to **qelaro.in**.

---

Built with ❤️ by **Souvik**
