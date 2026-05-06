__version__ = "1.17.1"
__description__ = "The Velora Package Manager. Download, update, publish, or unpublish custom core programs. Use install all to easily grab the entire official suite."
__author__ = "Souvik"
__website__ = "https://github.com/SouvikNandi1/Velora"

import sys
import os
import json
import urllib.request
import ssl
import base64
import shutil
import re
import time
import py_compile

def _vd(s): # Decrypts Velora Data (IDs, Keys)
    # This key must be consistent with the one used in terminal.py and bootstrap.py
    # for encrypting sensitive strings.
    k = b"VeloraSuperSecureKeyForObfuscation2026!"
    e = base64.b64decode(s)
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(e)).decode()

# Encrypted PROJECT_ID and API_KEY
PROJECT_ID = _vd('JToZEhYmI2Y=')
API_KEY = _vd('JTwdE0E/RkQXFRMXRkMDEBYWRUZGRUdEUxYWRUVFUxMWEw==')
BASE_URL = f"https://sncloud.in/api/db/{PROJECT_ID}/packages"

IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN: BUNDLED_CORE_DIR = os.path.join(getattr(sys, '_MEIPASS'), 'core')
else: BUNDLED_CORE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_CORE_DIR = os.path.expanduser("~/.velora/core")
os.makedirs(USER_CORE_DIR, exist_ok=True)
VPM_CACHE = os.path.expanduser("~/.velora/vpm_cache.json")

def get_local_packages_dict():
    pkgs = {}
    for d in (BUNDLED_CORE_DIR, USER_CORE_DIR):
        if not os.path.exists(d): continue
        for file in os.listdir(d):
            if file.endswith('.py') and file not in ('__init__.py', 'vpm.py'):
                pkg = file[:-3]
                pkgs[pkg] = os.path.join(d, file)
    return pkgs

def get_context():
    # Unverified SSL context to prevent macOS/Windows certificate errors
    return ssl._create_unverified_context()

def create_wrapper(pkg_name):
    velora_bin = os.path.expanduser("~/.velora/bin")
    os.makedirs(velora_bin, exist_ok=True)
    wrapper_path = os.path.join(velora_bin, pkg_name)
    
    if IS_FROZEN:
        command_prefix = f'"{sys.executable}" --run-core {pkg_name}'
    else:
        term_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
        command_prefix = f'"{sys.executable}" "{term_path}" --run-core {pkg_name}'
        
    if os.name == 'nt':
        wrapper_path += '.cmd'
        with open(wrapper_path, 'w') as f:
            f.write(f'@echo off\n{command_prefix} %*\n')
    else:
        with open(wrapper_path, 'w') as f:
            f.write(f'#!/bin/sh\nexec {command_prefix} "$@"\n')
        os.chmod(wrapper_path, 0o755)

def remove_wrapper(pkg_name):
    velora_bin = os.path.expanduser("~/.velora/bin")
    wrapper_path = os.path.join(velora_bin, pkg_name)
    if os.name == 'nt': wrapper_path += '.cmd'
    if os.path.exists(wrapper_path):
        os.remove(wrapper_path)

def download_with_progress(req):
    with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
        total_size = int(response.info().get('Content-Length', 0))
        if total_size > 0:
            downloaded = 0
            chunk_size = max(1024, total_size // 20)
            chunks = []
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                chunks.append(chunk)
                downloaded += len(chunk)
                percent = min(100, int((downloaded / total_size) * 100))
                bar = "#" * (percent // 2) + "-" * (50 - (percent // 2))
                sys.stdout.write(f"\r  \x1b[36m[\x1b[32;1m{bar}\x1b[36m] {percent}%\x1b[0m")
                sys.stdout.flush()
            
            bar = "#" * 50
            sys.stdout.write(f"\r  \x1b[36m[\x1b[32;1m{bar}\x1b[36m] 100%\x1b[0m\n")
            data = b"".join(chunks)
        else:
            data = response.read()
            for i in range(0, 101, 5):
                bar = "#" * (i // 2) + "-" * (50 - (i // 2))
                sys.stdout.write(f"\r  \x1b[36m[\x1b[32;1m{bar}\x1b[36m] {i}%\x1b[0m")
                sys.stdout.flush()
                time.sleep(0.01)
            sys.stdout.write("\n")
        return json.loads(data.decode('utf-8'))

def list_packages():
    url = f"{BASE_URL}.json?_t={int(time.time())}"
    local_pkgs = get_local_packages_dict()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Save cache for terminal suggestions
            try:
                with open(VPM_CACHE, 'w') as f:
                    json.dump(data, f)
            except: pass

            if not data or data == 'null':
                print("\n  \x1b[90mNo packages found in the cloud.\x1b[0m")
                return
            
            official = []
            community = []
            for pkg, info in data.items():
                if not isinstance(info, dict): continue
                if "✅" in info.get('description', ''):
                    official.append((pkg, info))
                else:
                    community.append((pkg, info))

            official.sort()
            community.sort()

            print("\n\x1b[38;2;189;147;249m┏━━━━ Velora Cloud Registry ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\x1b[0m")
            print(f"\x1b[90m┃ {'Package':<17} {'Version':<10} {'Author':<14} {'Description':<29} ┃\x1b[0m")

            def print_section(title, items, pkg_color):
                print(f"\x1b[90m┣━━ \x1b[35;1m{title:<68}\x1b[90m ━━┫\x1b[0m")
                for pkg, info in items:
                    icon = "✅" if title == "Verified Official Suite" else "  "
                    version = info.get('version', 'v1.0.0')
                    author = info.get('author', 'Unknown')[:12]
                    desc = info.get('description', '').replace('✅', '').strip()
                    desc = (desc[:29] + '..') if len(desc) > 29 else desc
                    is_installed = "*" if pkg in local_pkgs else " "
                    
                    print(f"\x1b[90m┃\x1b[0m {icon}{is_installed} {pkg_color}{pkg:<13}\x1b[0m {version:<10} \x1b[33m{author:<14}\x1b[0m {desc:<29} \x1b[90m┃\x1b[0m")

            if official:
                print_section("Verified Official Suite", official, "\x1b[36;1m")
            
            if community:
                if official: print("\x1b[90m┃ " + " " * 73 + " ┃\x1b[0m")
                print_section("Community Registry", community, "\x1b[32m")

            print("\x1b[38;2;189;147;249m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\x1b[0m")
            print(f"\x1b[90m Total: {len(data)} packages  │  * = Installed  │  Use 'vpm info <pkg>'\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError fetching packages:\x1b[0m {e}")

def list_local_packages():
    print("\n\x1b[36;1m═══ 📂 LOCAL INSTALLED PACKAGES ═══\x1b[0m")
    count = 0
    pkgs = get_local_packages_dict()
    for pkg, file_path in sorted(pkgs.items()):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            v_m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            version = v_m.group(1) if v_m else "1.0.0"
            a_m = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            author = a_m.group(1) if a_m else "Unknown"
            w_m = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            website = w_m.group(1) if w_m else ""
            d_m = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            desc = d_m.group(1) if d_m else "Local Velora program"

            print(f"\n  \x1b[90m╭─────────────────────────────────────────────────────╮\x1b[0m")
            print(f"  \x1b[90m│\x1b[0m  \x1b[32;1m{pkg:<25}\x1b[0m \x1b[33m{('v'+version):>10}\x1b[0m              \x1b[90m│\x1b[0m")
            print(f"  \x1b[90m│\x1b[0m  \x1b[90mStatus:\x1b[0m \x1b[32;1mInstalled\x1b[0m{(' ' * 36)}\x1b[90m│\x1b[0m")
            print(f"  \x1b[90m│\x1b[0m  \x1b[90mBy:\x1b[0m {author:<45}  \x1b[90m│\x1b[0m")
            print(f"  \x1b[90m├─────────────────────────────────────────────────────┤\x1b[0m")
            display_desc = (desc[:49] + '..') if len(desc) > 49 else desc
            print(f"  \x1b[90m│\x1b[0m  {display_desc:<49}  \x1b[90m│\x1b[0m")
            print(f"  \x1b[90m╰─────────────────────────────────────────────────────╯\x1b[0m")
            count += 1
        except Exception: pass

    term_ver = os.environ.get("VELORA_VERSION")
    term_author, term_site, term_desc = "Souvik", "https://github.com/SouvikNandi1/Velora", "Velora Terminal Core Application"

    if term_ver:
        term_path = os.environ.get("VELORA_TERMINAL_PATH")
        if not term_path or not os.path.exists(term_path):
            term_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
        if os.path.exists(term_path):
            try:
                with open(term_path, 'r', encoding='utf-8') as f: term_code = f.read()
                a_m = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                if a_m: term_author = a_m.group(1)
                w_m = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                if w_m: term_site = w_m.group(1)
                d_m = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                if d_m: term_desc = d_m.group(1)
            except Exception: pass

        print(f"\n  \x1b[90m╭─────────────────────────────────────────────────────╮\x1b[0m")
        print(f"  \x1b[90m│\x1b[0m  \x1b[36;1mVelora Terminal App\x1b[0m       \x1b[33m{('v'+term_ver):>10}\x1b[0m              \x1b[90m│\x1b[0m")
        print(f"  \x1b[90m│\x1b[0m  \x1b[90mStatus:\x1b[0m \x1b[32;1mInstalled\x1b[0m{(' ' * 36)}\x1b[90m│\x1b[0m")
        print(f"  \x1b[90m│\x1b[0m  \x1b[90mBy:\x1b[0m {term_author:<45}  \x1b[90m│\x1b[0m")
        print(f"  \x1b[90m├─────────────────────────────────────────────────────┤\x1b[0m")
        display_desc = (term_desc[:49] + '..') if len(term_desc) > 49 else term_desc
        print(f"  \x1b[90m│\x1b[0m  {display_desc:<49}  \x1b[90m│\x1b[0m")
        print(f"  \x1b[90m╰─────────────────────────────────────────────────────╯\x1b[0m")
    else:
        term_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
        if os.path.exists(term_path):
            try:
                with open(term_path, 'r', encoding='utf-8') as f: term_code = f.read()
                v_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                term_ver = v_match.group(1) if v_match else "unknown"
                author = "Unknown"
                a_match = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                if a_match: author = a_match.group(1)
                website = ""
                w_match = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', term_code, re.MULTILINE)
                if w_match: website = w_match.group(1)
                auth_str = f" \x1b[90mby {author}\x1b[0m" if author != 'Unknown' else ""
                site_str = f" \x1b[34;4m({website})\x1b[0m" if website else ""
                print(f"\n  \x1b[36;1mVelora Terminal App\x1b[0m \x1b[33m(v{term_ver})\x1b[0m{auth_str}{site_str}")
            except Exception: pass

def install_package(pkg_name):
    url = f"{BASE_URL}/{urllib.parse.quote(pkg_name)}.json?_t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        data = download_with_progress(req)
        if not data or data == 'null':
            print(f"\x1b[31;1mError:\x1b[0m Package '{pkg_name}' not found on SNCloud.")
            return
        
        target_path = os.path.join(USER_CORE_DIR, f"{pkg_name}.py")
        lib_dir = os.path.join(USER_CORE_DIR, f"{pkg_name}_lib")
        
        if not IS_FROZEN and os.path.exists(os.path.join(BUNDLED_CORE_DIR, f"{pkg_name}.py")):
            target_path = os.path.join(BUNDLED_CORE_DIR, f"{pkg_name}.py")
            lib_dir = os.path.join(BUNDLED_CORE_DIR, f"{pkg_name}_lib")
            
            # Clean up any lingering user updates so they don't mask the newly bundled core files
            user_file = os.path.join(USER_CORE_DIR, f"{pkg_name}.py")
            user_lib = os.path.join(USER_CORE_DIR, f"{pkg_name}_lib")
            if os.path.exists(user_file): os.remove(user_file)
            if os.path.exists(user_lib): shutil.rmtree(user_lib)
            
        if 'files_b64' in data:
            # Multi-file project installation
            if os.path.exists(lib_dir):
                shutil.rmtree(lib_dir)
            os.makedirs(lib_dir, exist_ok=True)
            
            entry = data.get('entry', 'main.py')
            
            for rel_path, b64_content in data['files_b64'].items():
                file_path = os.path.join(lib_dir, rel_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                raw_bytes = base64.b64decode(b64_content)
                if file_path.endswith('.py'):
                    try:
                        code_str = raw_bytes.decode('utf-8')
                        key = b"VeloraSuperSecureKeyForObfuscation2026!" # Consistent key
                        code_bytes = code_str.encode('utf-8')
                        enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(code_bytes))
                        b64_code = base64.b64encode(enc).decode('utf-8')
                        enc_stub = "# Velora Encrypted Core Program\n" f"__encrypted_payload__ = '{b64_code}'\n"
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(enc_stub)
                    except Exception:
                        with open(file_path, 'wb') as f: f.write(raw_bytes)
                else:
                    with open(file_path, 'wb') as f: f.write(raw_bytes)
                        
            version = data.get('version', '1.0.0')
            desc = data.get('description', 'A custom Velora core package')
            author = data.get('author', 'Unknown')
            website = data.get('website', '')
            
            exec_logic = f"import os, sys\nlib_dir = os.path.join(os.path.dirname(__file__), '{pkg_name}_lib')\nentry_file = os.path.join(lib_dir, '{entry}')\nsys.path.insert(0, lib_dir)\nrun_encrypted(entry_file, run_name='__main__')\n"
            
            key = b"velora_secure_123"
            code_bytes = exec_logic.encode('utf-8')
            enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(code_bytes))
            b64_code = base64.b64encode(enc).decode('utf-8')
            
            safe_desc = desc.replace(chr(39), chr(92)+chr(39))
            safe_author = author.replace(chr(39), chr(92)+chr(39))
            safe_website = website.replace(chr(39), chr(92)+chr(39))
            
            stub_code = (
                f"__version__ = '{version}'\n"
                f"__description__ = '{safe_desc}'\n"
                f"__author__ = '{safe_author}'\n"
                f"__website__ = '{safe_website}'\n"
                "# Velora Encrypted Core Program\n"
                f"__encrypted_payload__ = '{b64_code}'\n"
            )
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(stub_code)
        else:
            # Legacy single-file installation
            code = data.get('code')
            if not code:
                print(f"\x1b[31;1mError:\x1b[0m Invalid package payload from server.")
                return
                
            version = "1.0.0"
            v_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if v_match: version = v_match.group(1)
            
            desc = "A custom Velora core package"
            d_match = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if d_match: desc = d_match.group(1)
            
            author = "Unknown"
            a_match = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if a_match: author = a_match.group(1)
            
            website = ""
            w_match = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if w_match: website = w_match.group(1)
            
            key = b"velora_secure_123"
            code_bytes = code.encode('utf-8')
            enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(code_bytes))
            b64_code = base64.b64encode(enc).decode('utf-8')
            
            safe_desc = desc.replace(chr(39), chr(92)+chr(39))
            safe_author = author.replace(chr(39), chr(92)+chr(39))
            safe_website = website.replace(chr(39), chr(92)+chr(39))
            
            stub_code = (
                f"__version__ = '{version}'\n"
                f"__description__ = '{safe_desc}'\n"
                f"__author__ = '{safe_author}'\n"
                f"__website__ = '{safe_website}'\n"
                "# Velora Encrypted Core Program\n"
                f"__encrypted_payload__ = '{b64_code}'\n"
            )
                
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(stub_code)
                
        create_wrapper(pkg_name)
        print(f"\x1b[32;1mSuccessfully installed '{pkg_name}'!\x1b[0m")
        print(f"  \x1b[90mLocation: {target_path}\x1b[0m")
        print(f"  \x1b[36mExecutable ready: you can now run \x1b[32;1m{pkg_name}\x1b[36m anywhere.\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError installing package:\x1b[0m {e}")

def install_all_official():
    print("\x1b[36;1mFetching official Velora packages from SNCloud...\x1b[0m")
    url = f"{BASE_URL}.json?_t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data or data == 'null':
                print("  \x1b[90mNo packages found in the cloud.\x1b[0m")
                return
            
            count = 0
            for pkg, info in data.items():
                if isinstance(info, dict) and '✅' in info.get('description', ''):
                    print(f"\n\x1b[36;1mInstalling official package: '{pkg}'...\x1b[0m")
                    install_package(pkg)
                    count += 1
            
            print(f"\n\x1b[32;1mFinished installing {count} official packages.\x1b[0m")
            
            build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
            if not IS_FROZEN and os.path.exists(build_script):
                print("\x1b[36;1mAutomatically building new executable version...\x1b[0m")
                import subprocess
                try:
                    subprocess.call([sys.executable, build_script])
                except Exception as e:
                    print(f"\x1b[31;1mBuild error:\x1b[0m {e}")
    except Exception as e:
        print(f"\x1b[31;1mError fetching packages for install-all:\x1b[0m {e}")

def locate_package(pkg_name):
    target_path_user = os.path.join(USER_CORE_DIR, f"{pkg_name}.py")
    target_path_bundled = os.path.join(BUNDLED_CORE_DIR, f"{pkg_name}.py")
    
    if os.path.exists(target_path_user):
        print(f"\x1b[36;1mPackage '{pkg_name}' is located at:\x1b[0m")
        print(f"  \x1b[32m{target_path_user}\x1b[0m (User Update)")
        lib_target = os.path.join(USER_CORE_DIR, f"{pkg_name}_lib")
        if os.path.exists(lib_target):
            print(f"  \x1b[32m{lib_target}\x1b[0m (Library Directory)")
    elif os.path.exists(target_path_bundled):
        print(f"\x1b[36;1mPackage '{pkg_name}' is located at:\x1b[0m")
        print(f"  \x1b[32m{target_path_bundled}\x1b[0m (Bundled natively inside Velora)")
    else:
        print(f"\x1b[31;1mError:\x1b[0m Package '{pkg_name}' is not installed locally.")

def update_all():
    print("\x1b[36;1mChecking for updates for all installed packages...\x1b[0m")
    count = 0
    pkgs = get_local_packages_dict()
    
    url = f"{BASE_URL}.json?_t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not isinstance(data, dict): data = {}
    except Exception as e:
        print(f"\x1b[31;1mError fetching updates from SNCloud:\x1b[0m {e}")
        return

    for pkg, file_path in pkgs.items():
        cloud_info = data.get(pkg, {})
        if not isinstance(cloud_info, dict): continue
        
        cloud_ver = cloud_info.get('version', '1.0.0').strip()
        local_ver = "1.0.0"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.MULTILINE)
                if m: local_ver = m.group(1).strip()
        except Exception: pass
        
        needs_update = False
        try:
            if [int(x) for x in cloud_ver.split('.')] > [int(x) for x in local_ver.split('.')]: needs_update = True
        except Exception:
            if cloud_ver != local_ver: needs_update = True
            
        if needs_update:
            print(f"  \x1b[90mUpdating '{pkg}' (v{local_ver} -> v{cloud_ver})...\x1b[0m")
            install_package(pkg)
            count += 1

    if count == 0:
        print("  \x1b[32;1m✅ All local packages are already up to date.\x1b[0m")
    else:
        print(f"\x1b[32;1mFinished updating {count} packages.\x1b[0m")
        build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
        if not IS_FROZEN and os.path.exists(build_script):
            print("\x1b[36;1mAutomatically building new executable version...\x1b[0m")
            import subprocess
            try:
                subprocess.call([sys.executable, build_script])
            except Exception as e:
                print(f"\x1b[31;1mBuild error:\x1b[0m {e}")

def upgrade_terminal():
    if IS_FROZEN:
        print("\x1b[31;1mError:\x1b[0m Cannot perform over-the-air terminal upgrades on compiled native binaries.")
        print("Please download the latest executable installer or rebuild using build.py.")
        return
    url = f"https://sncloud.in/api/db/{PROJECT_ID}/app/terminal.json?_t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        data = download_with_progress(req)
        if not data or data == 'null':
            print("\x1b[31;1mError:\x1b[0m Terminal update not found on SNCloud.")
            return
        
        code = data.get('code')
        if not code:
            print("\x1b[31;1mError:\x1b[0m Invalid terminal payload from server.")
            return
        
        target_path = os.environ.get("VELORA_TERMINAL_PATH")
        if not target_path or not os.path.exists(target_path):
            target_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("\x1b[32;1mSuccessfully upgraded the Velora Terminal App!\x1b[0m")
        
        build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
        if not IS_FROZEN and os.path.exists(build_script):
            print("\x1b[36;1mAutomatically building new executable version...\x1b[0m")
            import subprocess
            try:
                subprocess.call([sys.executable, build_script])
            except Exception as e:
                print(f"\x1b[31;1mBuild error:\x1b[0m {e}")
                
        print("\x1b[33;1mPlease completely close and restart Velora to apply the update.\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError upgrading terminal:\x1b[0m {e}")

def check_updates():
    print("\x1b[36;1mChecking for updates on SNCloud...\x1b[0m")
    app_update = None
    app_current = "1.0.0"
    pkg_updates = []
    
    try:
        req = urllib.request.Request(f"https://sncloud.in/api/db/{PROJECT_ID}/app/terminal.json?_t={int(time.time())}", headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, context=get_context(), timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and data != 'null':
                cloud_ver = data.get('version', '1.0.0') if isinstance(data, dict) else '1.0.0'
                local_ver = os.environ.get("VELORA_VERSION")
                if not local_ver:
                    term_path = os.environ.get("VELORA_TERMINAL_PATH")
                    if not term_path or not os.path.exists(term_path):
                        term_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
                    local_ver = "1.0.0"
                    if os.path.exists(term_path):
                        with open(term_path, 'r', encoding='utf-8') as f:
                            m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.MULTILINE)
                            if m: local_ver = m.group(1)
                app_current = local_ver
                try:
                    if [int(x) for x in cloud_ver.split('.')] > [int(x) for x in local_ver.split('.')]: app_update = cloud_ver
                except Exception:
                    if cloud_ver != local_ver: app_update = cloud_ver
                    
        req = urllib.request.Request(f"{BASE_URL}.json?_t={int(time.time())}", headers={'User-Agent': 'Velora/1.0', 'X-API-Key': API_KEY, 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, context=get_context(), timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict):
                for pkg, info in data.items():
                    if isinstance(info, dict):
                        cloud_ver = info.get('version', '1.0.0').strip()
                        target_user = os.path.join(USER_CORE_DIR, f"{pkg}.py")
                        target_bundled = os.path.join(BUNDLED_CORE_DIR, f"{pkg}.py")
                        local_path = target_user if os.path.exists(target_user) else target_bundled
                        if os.path.exists(local_path):
                            try:
                                with open(local_path, 'r', encoding='utf-8') as f:
                                    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.MULTILINE)
                                    local_ver = m.group(1).strip() if m else "1.0.0"
                                try:
                                    if [int(x) for x in cloud_ver.split('.')] > [int(x) for x in local_ver.split('.')]: pkg_updates.append((pkg, local_ver, cloud_ver))
                                except Exception:
                                    if cloud_ver != local_ver: pkg_updates.append((pkg, local_ver, cloud_ver))
                            except Exception: pass
                            
        print("\n\x1b[36;1m=== 🖥️  Velora Terminal Status ===\x1b[0m")
        if app_update:
            print(f"  \x1b[31;1mOutdated\x1b[0m \x1b[90m(v{app_current} ->\x1b[0m \x1b[32;1mv{app_update}\x1b[0m)")
            print("  \x1b[33m🔔 Run \x1b[32;1mvpm upgrade\x1b[33m to install the new version.\x1b[0m")
        else:
            print(f"  \x1b[32;1m✅ Up to date\x1b[0m \x1b[90m(v{app_current})\x1b[0m")

        print("\n\x1b[36;1m=== 📦 Upgradable Packages ===\x1b[0m")
        if pkg_updates:
            for p, l_ver, c_ver in pkg_updates: 
                print(f"  \x1b[31;1m{p}\x1b[0m \x1b[90m(v{l_ver} ->\x1b[0m \x1b[32;1mv{c_ver}\x1b[90m)\x1b[0m")
            print(f"\n  \x1b[33m🔔 Run \x1b[32;1mvpm update-all\x1b[33m to update {len(pkg_updates)} package(s).\x1b[0m")
        else:
            print("  \x1b[32;1m✅ All local packages are up to date!\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError checking updates:\x1b[0m {e}")

def publish_package(pkg_name, file_path, description="", entry_file=""):
    if not os.path.exists(file_path):
        print(f"\x1b[31;1mError:\x1b[0m Local file '{file_path}' not found.")
        return
        
    try:
        payload_dict = {"description": description}
        
        if os.path.isdir(file_path):
            # Multi-file project publishing
            if not entry_file:
                entry_file = "main.py"
            if not os.path.exists(os.path.join(file_path, entry_file)):
                print(f"\x1b[31;1mError:\x1b[0m Entry file '{entry_file}' not found in directory '{file_path}'.")
                return
                
            files_b64 = {}
            for root, _, filenames in os.walk(file_path):
                for filename in filenames:
                    if '__pycache__' in root or filename.endswith('.pyc'): continue
                    abs_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(abs_path, file_path).replace('\\', '/')
                    
                    with open(abs_path, 'rb') as f: raw = f.read()
                    
                    if filename.endswith('.py'):
                        try:
                            code = raw.decode('utf-8')
                            if "# Velora Encrypted Core Program\n__encrypted_payload__" in code:
                                m = re.search(r"__encrypted_payload__\s*=\s*['\"]([A-Za-z0-9+/=]+)['\"]", code)
                                if m:
                                    enc = base64.b64decode(m.group(1))
                                    key = b"velora_secure_123"
                                    raw = bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))
                        except Exception: pass
                        
                    files_b64[rel_path] = base64.b64encode(raw).decode('utf-8')
                        
            payload_dict["type"] = "multi"
            payload_dict["entry"] = entry_file
            payload_dict["files_b64"] = files_b64
            
            entry_file_path = os.path.join(file_path, entry_file)
            with open(entry_file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            version = "1.0.0"
            v_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if v_match: version = v_match.group(1)
            payload_dict["version"] = version
            
            a_match = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if a_match: payload_dict["author"] = a_match.group(1)
            w_match = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if w_match: payload_dict["website"] = w_match.group(1)
        else:
            # Single-file publishing
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            if "# Velora Encrypted Core Program\n__encrypted_payload__" in code:
                m = re.search(r"__encrypted_payload__\s*=\s*['\"]([A-Za-z0-9+/=]+)['\"]", code)
                if m:
                    try:
                        enc = base64.b64decode(m.group(1))
                        key = b"velora_secure_123"
                        code = bytes(b ^ key[i % len(key)] for i, b in enumerate(enc)).decode('utf-8')
                    except Exception:
                        pass
            
            version = "1.0.0"
            v_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if v_match: version = v_match.group(1)
            
            d_match = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if d_match and (not description or description == "A custom Velora core package" or description.startswith("✅")):
                prefix = "✅ " if "✅" in description else ""
                description = prefix + d_match.group(1)
            
            payload_dict["description"] = description
            payload_dict["code"] = code
            payload_dict["version"] = version
            
            a_match = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if a_match: payload_dict["author"] = a_match.group(1)
            w_match = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            if w_match: payload_dict["website"] = w_match.group(1)
            
        payload = json.dumps(payload_dict).encode('utf-8')
        url = f"{BASE_URL}/{urllib.parse.quote(pkg_name)}.json"
        
        req = urllib.request.Request(url, data=payload, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-Key', API_KEY)
        req.add_header('User-Agent', 'Velora/1.0')
        
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            print(f"\x1b[32;1mSuccessfully published '{pkg_name}' to SNCloud!\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError publishing package:\x1b[0m {e}")

def unpublish_package(pkg_name):
    url = f"{BASE_URL}/{urllib.parse.quote(pkg_name)}.json"
    try:
        req = urllib.request.Request(url, method='DELETE')
        req.add_header('X-API-Key', API_KEY)
        req.add_header('User-Agent', 'Velora/1.0')
        
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            print(f"\x1b[32;1mSuccessfully removed '{pkg_name}' from SNCloud!\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError removing package from SNCloud:\x1b[0m {e}")

def publish_core_files(password):
    if password != "86531Souvik@":
        print("\x1b[31;1mError:\x1b[0m Unauthorized. Incorrect password.")
        return
        
    print("\x1b[36;1mPublishing all core files to SNCloud...\x1b[0m")
    
    help_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), 'help.html')
    descriptions = {}
    if os.path.exists(help_path):
        with open(help_path, 'r', encoding='utf-8') as f:
            content = f.read()
        cards = re.findall(r'<div class="card">\s*<h2>.*?([\w-]+)</h2>\s*<p>(.*?)</p>', content, re.DOTALL)
        for pkg_name, desc in cards:
            clean_desc = re.sub(r'<[^>]+>', '', desc.strip())
            descriptions[pkg_name] = clean_desc

    count = 0
    pkgs = get_local_packages_dict()
    for pkg, file_path in pkgs.items():
        base_desc = descriptions.get(pkg, "Official Velora Core Program")
        publish_package(pkg, file_path, f"✅ {base_desc}")
        count += 1
    print(f"\x1b[32;1mFinished publishing {count} core files.\x1b[0m")

def publish_terminal():
    if IS_FROZEN:
        print("\x1b[31;1mError:\x1b[0m Cannot publish terminal source from a compiled native binary.")
        return
    target_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
    if not os.path.exists(target_path):
        print(f"\x1b[31;1mError:\x1b[0m Local terminal file '{target_path}' not found.")
        return
        
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        version = "1.0.0"
        v_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
        if v_match: version = v_match.group(1)
            
        description = "Velora Terminal Core Application"
        d_match = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
        if d_match: description = d_match.group(1)
        
        payload_dict = {"description": description, "code": code, "version": version}
        a_match = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
        if a_match: payload_dict["author"] = a_match.group(1)
        w_match = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
        if w_match: payload_dict["website"] = w_match.group(1)
        
        payload = json.dumps(payload_dict).encode('utf-8')
        url = f"https://sncloud.in/api/db/{PROJECT_ID}/app/terminal.json"
        
        req = urllib.request.Request(url, data=payload, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-Key', API_KEY)
        req.add_header('User-Agent', 'Velora/1.0')
        
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            print("\x1b[32;1mSuccessfully published Velora Terminal to SNCloud!\x1b[0m")
    except Exception as e:
        print(f"\x1b[31;1mError publishing terminal:\x1b[0m {e}")

def build_executable():
    if IS_FROZEN:
        print("\x1b[31;1mError:\x1b[0m Already running a compiled binary.")
        return
    build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
    if os.path.exists(build_script):
        print("\x1b[36;1mBuilding native executable using PyInstaller...\x1b[0m")
        import subprocess
        try:
            subprocess.call([sys.executable, build_script])
        except Exception as e:
            print(f"\x1b[31;1mBuild error:\x1b[0m {e}")
    else:
        print(f"\x1b[31;1mError:\x1b[0m build.py not found in the project root.")

def main():
    # Force UTF-8 standard output to prevent 'charmap' encoding errors with emojis on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    args = sys.argv[1:]
    if not args:
        print("\x1b[36;1mVelora Package Manager (VPM)\x1b[0m\n")
        print("  \x1b[33mUsage:\x1b[0m")
        print("  vpm list                          \x1b[90m- List all packages on SNCloud\x1b[0m")
        print("  vpm local                         \x1b[90m- List local installed packages and versions\x1b[0m")
        print("  vpm check                         \x1b[90m- Check SNCloud for available updates\x1b[0m")
        print("  vpm locate <pkg>                  \x1b[90m- Show the installation path of a package\x1b[0m")
        print("  vpm install <pkg>                 \x1b[90m- Download and install a package\x1b[0m")
        print("  vpm install all                   \x1b[90m- Install all official verified packages\x1b[0m")
        print("  vpm update <pkg>                  \x1b[90m- Update an installed package\x1b[0m")
        print("  vpm update-all                    \x1b[90m- Update all installed packages\x1b[0m")
        print("  vpm upgrade                       \x1b[90m- Upgrade the main Velora Terminal App\x1b[0m")
        print("  vpm remove <pkg>                  \x1b[90m- Delete a local package\x1b[0m")
        print("  vpm build                         \x1b[90m- Compile Velora to a standalone executable\x1b[0m")
        print("  vpm publish <pkg> <file/dir> [desc] [entry] \x1b[90m- Upload to SNCloud\x1b[0m")
        print("  vpm unpublish <pkg>               \x1b[90m- Delete a package from SNCloud\x1b[0m")
        print("  vpm publish-app                   \x1b[90m- Upload terminal.py to SNCloud\x1b[0m")
        print("  vpm publish-main <password>       \x1b[90m- Upload all core files to SNCloud\x1b[0m")
        return
        
    cmd = args[0].lower()
    if cmd == 'list': list_packages()
    elif cmd == 'local': list_local_packages()
    elif cmd == 'check': check_updates()
    elif cmd == 'locate' and len(args) > 1: locate_package(args[1])
    elif cmd == 'install' and len(args) > 1:
        if args[1].lower() == 'all':
            install_all_official()
        else:
            install_package(args[1])
    elif cmd == 'update' and len(args) > 1:
        target_user = os.path.join(USER_CORE_DIR, f"{args[1]}.py")
        target_bundled = os.path.join(BUNDLED_CORE_DIR, f"{args[1]}.py")
        if not os.path.exists(target_user) and not os.path.exists(target_bundled):
            print(f"\x1b[33mPackage '{args[1]}' is not installed locally. Use 'vpm install {args[1]}' instead.\x1b[0m")
        else:
            print(f"\x1b[36;1mUpdating '{args[1]}'...\x1b[0m")
            install_package(args[1])
    elif cmd == 'update-all': update_all()
    elif cmd == 'upgrade': upgrade_terminal()
    elif cmd in ('remove', 'rm') and len(args) > 1:
        target = os.path.join(USER_CORE_DIR, f"{args[1]}.py")
        lib_target = os.path.join(USER_CORE_DIR, f"{args[1]}_lib")
        removed = False
        if os.path.exists(target):
            os.remove(target)
            removed = True
        if os.path.exists(lib_target):
            shutil.rmtree(lib_target)
            removed = True
        if removed:
            print(f"\x1b[31;1mRemoved user-updated package '{args[1]}'.\x1b[0m")
            if os.path.exists(os.path.join(BUNDLED_CORE_DIR, f"{args[1]}.py")):
                create_wrapper(args[1])
            else:
                remove_wrapper(args[1])
        else:
            if os.path.exists(os.path.join(BUNDLED_CORE_DIR, f"{args[1]}.py")):
                print(f"\x1b[33mPackage '{args[1]}' is natively bundled with the compiled app and cannot be removed.\x1b[0m")
            else:
                print(f"\x1b[33mPackage '{args[1]}' is not installed locally.\x1b[0m")
    elif cmd == 'build': build_executable()
    elif cmd == 'publish' and len(args) > 2:
        desc = args[3] if len(args) > 3 else "A custom Velora core package"
        entry = args[4] if len(args) > 4 else "main.py"
        publish_package(args[1], args[2], desc, entry)
    elif cmd == 'unpublish' and len(args) > 1: unpublish_package(args[1])
    elif cmd == 'publish-app': publish_terminal()
    elif cmd == 'publish-main':
        if len(args) > 1:
            publish_core_files(args[1])
        else:
            print("\x1b[31;1mError:\x1b[0m Password required. Usage: vpm publish-main <password>")
    else:
        print("\x1b[31;1mInvalid command or missing arguments.\x1b[0m")

if __name__ == "__main__":
    main()