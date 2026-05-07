__version__ = "2.1.3"
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
import subprocess
import platform
# Force local imports to prevent collision with system packages
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import velora_utils


def clean_version(v):
    if not v: return "0.0.0"
    v = str(v).strip().lower().lstrip('v')
    return re.sub(r'[^0-9.]', '', v)

def is_newer(cloud_v, local_v):
    c = clean_version(cloud_v)
    l = clean_version(local_v)
    try:
        cp = [int(x) for x in c.split('.') if x.isdigit()]
        lp = [int(x) for x in l.split('.') if x.isdigit()]
        return cp > lp
    except:
        return c != l

PROJECT_ID = None
API_KEY = None
CREDENTIALS_PATH = os.path.expanduser("~/.velora/vpm_secrets.json")
LOCAL_CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".velora", "vpm_secrets.json")
ENC_PROJECT_ID = "NAdaDRZYMUY="
ENC_API_KEY = "JQszWEBYMBEVVhFiVAJMRgYpVhh+XkUqVlQWEAJXQlwJV1c="


def _vd(s):
    key = b"VeloraSuperSecureKeyForObfuscation2026!"
    try:
        enc = base64.b64decode(s)
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(enc)).decode('utf-8')
    except Exception:
        return s


def get_remote_credentials():
    project_id = os.getenv("VELORA_SN_PROJECT_ID")
    api_key = os.getenv("VELORA_SN_API_KEY")
    if project_id and api_key:
        return project_id, api_key

    for path in (CREDENTIALS_PATH, LOCAL_CREDENTIALS_PATH):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                project_id = project_id or data.get("PROJECT_ID")
                api_key = api_key or data.get("API_KEY")
                if project_id and api_key:
                    return project_id, api_key
            except Exception:
                pass

    project_id = project_id or _vd(ENC_PROJECT_ID)
    api_key = api_key or _vd(ENC_API_KEY)
    if project_id and api_key:
        return project_id, api_key

    raise RuntimeError(
        "Missing VPM credentials. Set VELORA_SN_PROJECT_ID and VELORA_SN_API_KEY "
        "environment variables or save them in ~/.velora/vpm_secrets.json."
    )


def get_base_url():
    project_id, _ = get_remote_credentials()
    return f"https://sncloud.in/api/db/{project_id}/packages"


def get_request(url, data=None, method=None):
    _, api_key = get_remote_credentials()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    req.add_header('X-API-Key', api_key)
    req.add_header('Cache-Control', 'no-cache')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    return req

IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN: BUNDLED_CORE_DIR = os.path.join(getattr(sys, '_MEIPASS'), 'core')
else: 
    _base = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(_base, 'core')):
        BUNDLED_CORE_DIR = os.path.join(_base, 'core')
    else:
        BUNDLED_CORE_DIR = _base

USER_CORE_DIR = os.path.expanduser("~/.velora/core")
os.makedirs(USER_CORE_DIR, exist_ok=True)
VPM_CACHE = os.path.expanduser("~/.velora/vpm_cache.json")

def get_local_packages_dict():
    pkgs = {}
    ignore = ('__init__.py', 'vpm.py', 'terminal.py', 'bootstrap.py', 'install.py', 'build.py', 'git.py')
    for d in (BUNDLED_CORE_DIR, USER_CORE_DIR):
        if not os.path.exists(d): continue
        for file in os.listdir(d):
            if file.endswith('.py') and file not in ignore:
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
                velora_utils.progress_bar(downloaded, total_size, prefix="Downloading:", suffix=f"({downloaded/1024:.1f} KB)")
            data = b"".join(chunks)
        else:
            data = response.read()
            # Fake progress for unknown size
            for i in range(1, 101, 5):
                velora_utils.progress_bar(i, 100, prefix="Downloading:", suffix="...")
                time.sleep(0.02)
            velora_utils.progress_bar(100, 100, prefix="Downloading:", suffix="Done")
        return json.loads(data.decode('utf-8'))

def list_packages():
    url = f"{get_base_url()}.json?_t={int(time.time())}"
    local_pkgs = get_local_packages_dict()
    try:
        req = get_request(url)
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Save cache for terminal suggestions
            try:
                with open(VPM_CACHE, 'w') as f:
                    json.dump(data, f)
            except: pass

            if not data or data == 'null':
                velora_utils.print_status("No packages found in the cloud.", type="info")
                return
            
            categories = {
                "🛠️ Tools": [],
                "🖥️ System": [],
                "🎮 Games": [],
                "✨ Fun": [],
                "📦 Other": []
            }

            # Mapping for official packages to categories
            OFFICIAL_MAPPING = {
                "calc": "🛠️ Tools", "unitconv": "🛠️ Tools", "baseconv": "🛠️ Tools", "hash": "🛠️ Tools", 
                "textstat": "🛠️ Tools", "todo": "🛠️ Tools", "notes": "🛠️ Tools", "passgen": "🛠️ Tools", 
                "uuidgen": "🛠️ Tools", "url": "🛠️ Tools", "b32": "🛠️ Tools", "b64": "🛠️ Tools", 
                "jsonfmt": "🛠️ Tools", "hashfile": "🛠️ Tools", "currency": "🛠️ Tools", "translator": "🛠️ Tools",
                "timer": "🛠️ Tools", "stopwatch": "🛠️ Tools", "cal": "🛠️ Tools",
                "fetch": "🖥️ System", "ipinfo": "🖥️ System", "sysinfo": "🖥️ System", "weather": "🖥️ System", 
                "worldclock": "🖥️ System", "install-tor": "🖥️ System",
                "quote": "✨ Fun", "matrix": "✨ Fun", "roll": "✨ Fun", "chat": "✨ Fun"
            }

            for pkg, info in data.items():
                if not isinstance(info, dict): continue
                desc = info.get('description', '')
                is_official = "✅" in desc
                
                # Determine category
                cat = OFFICIAL_MAPPING.get(pkg)
                if not cat:
                    if "game" in desc.lower() or "play" in desc.lower(): cat = "🎮 Games"
                    elif "tool" in desc.lower() or "utility" in desc.lower(): cat = "🛠️ Tools"
                    elif is_official: cat = "🛠️ Tools" # Fallback for official
                    else: cat = "📦 Other"
                
                categories[cat].append((pkg, info))

            # Stats for dashboard
            total_pkgs = len(data)
            official_count = sum(1 for pkg, info in data.items() if isinstance(info, dict) and "✅" in info.get('description', ''))
            community_count = total_pkgs - official_count
            installed_count = sum(1 for pkg in data if pkg in local_pkgs)

            velora_utils.print_header("Velora Cloud Registry", color=velora_utils.PURPLE)
            
            # Summary Dashboard
            print(f"  {velora_utils.CYAN}Total:{velora_utils.RESET} {total_pkgs:<5} "
                  f"{velora_utils.GREEN}Official:{velora_utils.RESET} {official_count:<5} "
                  f"{velora_utils.PINK}Community:{velora_utils.RESET} {community_count:<5} "
                  f"{velora_utils.YELLOW}Installed:{velora_utils.RESET} {installed_count}")
            print(f"  {velora_utils.GREY}" + "─" * 60 + f"{velora_utils.RESET}\n")

            for cat_name, items in categories.items():
                if not items: continue
                
                velora_utils.print_section(cat_name, color=velora_utils.CYAN)
                table = velora_utils.Table(["Package", "Version", "Author", "Description"], 
                                             colors=[velora_utils.CYAN, velora_utils.YELLOW, velora_utils.PINK, velora_utils.RESET])

                items.sort()
                for pkg, info in items:
                    version = info.get('version', 'v1.0.0')
                    author = info.get('author', 'Unknown')[:12]
                    desc = info.get('description', '').replace('✅', '').strip()
                    desc = (desc[:29] + '..') if len(desc) > 29 else desc
                    is_installed = "*" if pkg in local_pkgs else " "
                    icon = "✅ " if "✅" in info.get('description', '') else ""
                    
                    table.add_row([f"{icon}{is_installed}{pkg}", version, author, desc])
                
                table.print()
                print()

            print(f"  {velora_utils.GREY}Total: {len(data)} packages  │  * = Installed  │  Use 'vpm info <pkg>'{velora_utils.RESET}")
            print(f"  {velora_utils.GREY}Total: {len(data)} packages  │  * = Installed  │  Use 'vpm info <pkg>'{velora_utils.RESET}")
    except Exception as e:
        velora_utils.print_status(f"Error fetching packages: {e}", type="error")

def get_cloud_packages():
    """Returns a dictionary of packages from SNCloud for UI consumption."""
    url = f"{get_base_url()}.json?_t={int(time.time())}"
    try:
        req = get_request(url)
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data or data == 'null': return {}
            return data
    except Exception:
        return {}

def get_local_packages_info():
    """Returns a list of dictionaries with metadata for all local packages."""
    pkgs_info = []
    local_pkgs = get_local_packages_dict()
    
    for pkg, file_path in sorted(local_pkgs.items()):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            v_m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            a_m = re.search(r'^__author__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            w_m = re.search(r'^__website__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            d_m = re.search(r'^__description__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            c_m = re.search(r'^__category__\s*=\s*["\']([^"\']+)["\']', code, re.MULTILINE)
            
            pkgs_info.append({
                "name": pkg,
                "version": v_m.group(1) if v_m else "1.0.0",
                "author": a_m.group(1) if a_m else "Unknown",
                "website": w_m.group(1) if w_m else "",
                "description": d_m.group(1) if d_m else "Local Velora program",
                "category": c_m.group(1) if c_m else "Tools",
                "path": file_path,
                "type": "user" if USER_CORE_DIR in file_path else "bundled"
            })
        except Exception: pass
        
    return pkgs_info

def list_local_packages():
    velora_utils.print_header("Local Installed Packages", color=velora_utils.CYAN)
    
    pkgs = get_local_packages_info()
    
    # Categorize local packages
    categories = {}
    for pkg in pkgs:
        cat = pkg.get('category', '🛠️ Tools')
        if cat not in categories: categories[cat] = []
        categories[cat].append(pkg)
    
    # Add Terminal app to System category
    if "🖥️ System" not in categories: categories["🖥️ System"] = []
    term_ver = os.environ.get("VELORA_VERSION", "2.1.3")
    categories["🖥️ System"].append({
        "name": "Velora Terminal",
        "version": term_ver,
        "author": "Souvik",
        "description": "Velora Terminal Core Application"
    })

    for cat_name, items in sorted(categories.items()):
        velora_utils.print_section(cat_name, color=velora_utils.PURPLE)
        table = velora_utils.Table(["Package", "Version", "Author", "Description"], 
                                     colors=[velora_utils.GREEN, velora_utils.YELLOW, velora_utils.PINK, velora_utils.RESET])
        
        for pkg in sorted(items, key=lambda x: x['name']):
            table.add_row([pkg['name'], pkg['version'], pkg['author'], pkg['description']])
        
        table.print()
        print()
    
    velora_utils.print_status(f"Found {len(pkgs) + 1} installed components.", type="info")

def install_package(pkg_name):
    url = f"{get_base_url()}/{urllib.parse.quote(pkg_name)}.json?_t={int(time.time())}"
    try:
        req = get_request(url)
        data = download_with_progress(req)
        if not data or data == 'null':
            velora_utils.print_status(f"Package '{pkg_name}' not found on SNCloud.", type="error")
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
                        key = b"VeloraSuperSecureKeyForObfuscation2026!"
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
            
            exec_logic = f"import os, sys\nlib_dir = os.path.join(os.path.dirname(__file__), '{pkg_name}_lib')\nentry_file = os.path.join(lib_dir, '{entry}')\nrun_encrypted(entry_file, run_name='__main__')\n"
            
            key = b"VeloraSuperSecureKeyForObfuscation2026!"
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
                velora_utils.print_status("Invalid package payload from server.", type="error")
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
            
            key = b"VeloraSuperSecureKeyForObfuscation2026!"
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
        velora_utils.print_status(f"Successfully installed '{pkg_name}'!", type="success")
        velora_utils.print_labeled("Location", target_path)
    except Exception as e:
        velora_utils.print_status(f"Error installing package: {e}", type="error")

def install_all_official():
    velora_utils.print_status(f"Fetching official Velora packages from SNCloud...", type="info")
    url = f"{get_base_url()}.json?_t={int(time.time())}"
    try:
        req = get_request(url)
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data or data == 'null':
                velora_utils.print_status("No packages found in the cloud.", type="info")
                return
            
            count = 0
            for pkg, info in data.items():
                if isinstance(info, dict) and '✅' in info.get('description', ''):
                    velora_utils.print_status(f"Installing official package: '{pkg}'...", type="info")
                    install_package(pkg)
                    count += 1
            
            velora_utils.print_status(f"Finished installing {count} official packages.", type="success")
            
            build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
            if not IS_FROZEN and os.path.exists(build_script):
                velora_utils.print_status("Automatically building new executable version...", type="info")
                import subprocess
                try:
                    subprocess.call([sys.executable, build_script])
                except Exception as e:
                    velora_utils.print_status(f"Build error: {e}", type="error")
    except Exception as e:
        velora_utils.print_status(f"Error fetching packages for install-all: {e}", type="error")

def locate_package(pkg_name):
    target_path_user = os.path.join(USER_CORE_DIR, f"{pkg_name}.py")
    target_path_bundled = os.path.join(BUNDLED_CORE_DIR, f"{pkg_name}.py")
    path_to_reveal = None
    if os.path.exists(target_path_user):
        path_to_reveal = target_path_user
        velora_utils.print_status(f"Package '{pkg_name}' is located at:", type="info")
        print(f"  {velora_utils.GREEN}{target_path_user}{velora_utils.RESET} (User Update)")
        lib_target = os.path.join(USER_CORE_DIR, f"{pkg_name}_lib")
        if os.path.exists(lib_target):
            print(f"  {velora_utils.GREEN}{lib_target}{velora_utils.RESET} (Library Directory)")
    elif os.path.exists(target_path_bundled):
        path_to_reveal = target_path_bundled
        velora_utils.print_status(f"Package '{pkg_name}' is located at:", type="info")
        print(f"  {velora_utils.GREEN}{target_path_bundled}{velora_utils.RESET} (Bundled natively inside Velora)")
    else:
        velora_utils.print_status(f"Package '{pkg_name}' is not installed locally.", type="error")
        return

    if path_to_reveal:
        try:
            if sys.platform == 'darwin':
                subprocess.call(['open', '-R', path_to_reveal])
            elif os.name == 'nt':
                subprocess.call(['explorer', '/select,', os.path.normpath(path_to_reveal)])
            else:
                subprocess.call(['xdg-open', os.path.dirname(path_to_reveal)])
        except: pass

def update_all():
    velora_utils.print_status("Checking for updates for all installed packages...", type="info")
    count = 0
    pkgs = get_local_packages_dict()
    
    url = f"{get_base_url()}.json?_t={int(time.time())}"
    try:
        req = get_request(url)
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not isinstance(data, dict): data = {}
    except Exception as e:
        velora_utils.print_status(f"Error fetching updates from SNCloud: {e}", type="error")
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
        
        needs_update = is_newer(cloud_ver, local_ver)
            
        if needs_update:
            velora_utils.print_status(f"Updating '{pkg}' (v{local_ver} -> v{cloud_ver})...", type="info")
            install_package(pkg)
            count += 1

    if count == 0:
        velora_utils.print_status("All local packages are already up to date.", type="success")
    else:
        velora_utils.print_status(f"Finished updating {count} packages.", type="success")
        build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
        if not IS_FROZEN and os.path.exists(build_script):
            velora_utils.print_status("Automatically building new executable version...", type="info")
            import subprocess
            try:
                subprocess.call([sys.executable, build_script])
            except Exception as e:
                velora_utils.print_status(f"Build error: {e}", type="error")

def upgrade_terminal():

    if IS_FROZEN:
        velora_utils.print_status("Cannot perform over-the-air terminal upgrades on compiled native binaries.", type="error")
        print(f"  {velora_utils.GREY}Please download the latest executable installer or rebuild using build.py.{velora_utils.RESET}")
        return
    project_id, _ = get_remote_credentials()
    url = f"https://sncloud.in/api/db/{project_id}/app/terminal.json?_t={int(time.time())}"
    try:
        req = get_request(url)
        data = download_with_progress(req)
        if not data or data == 'null':
            velora_utils.print_status("Terminal update not found on SNCloud.", type="error")
            return
        
        code = data.get('code')
        if not code:
            velora_utils.print_status("Invalid terminal payload from server.", type="error")
            return
        
        target_path = os.environ.get("VELORA_TERMINAL_PATH")
        if not target_path or not os.path.exists(target_path):
            target_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(code)
        velora_utils.print_status("Successfully upgraded the Velora Terminal App!", type="success")
        
        build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
        if not IS_FROZEN and os.path.exists(build_script):
            print("\x1b[36;1mAutomatically building new executable version...\x1b[0m")
            import subprocess
            try:
                subprocess.call([sys.executable, build_script])
            except Exception as e:
                print(f"\x1b[31;1mBuild error:\x1b[0m {e}")
                
        print(f"  {velora_utils.YELLOW}Please completely close and restart Velora to apply the update.{velora_utils.RESET}")
    except Exception as e:
        velora_utils.print_status(f"Upgrade failed: {e}", type="error")

def check_updates():
    velora_utils.print_status("Checking for updates on SNCloud...", type="info")
    app_update = None
    app_current = "1.0.0"
    pkg_updates = []
    bootstrap_update = None
    bootstrap_current = "1.0.0"
    
    try:
        # Check bootstrap update
        try:
            req = urllib.request.Request("https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py", headers={'User-Agent': 'Velora-VPM'})
            with urllib.request.urlopen(req, context=get_context(), timeout=5) as response:
                content = response.read().decode('utf-8')
                m = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                if m:
                    cloud_bootstrap_ver = m.group(1)
                    # Get local bootstrap version
                    local_bootstrap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bootstrap.py")
                    if not os.path.exists(local_bootstrap_path):
                        local_bootstrap_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "bootstrap.py")
                    if not os.path.exists(local_bootstrap_path):
                        local_bootstrap_path = os.path.expanduser("~/.velora/app/bootstrap.py")

                    if os.path.exists(local_bootstrap_path):
                        with open(local_bootstrap_path, 'r', encoding='utf-8') as f:
                            local_content = f.read()
                            m2 = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', local_content, re.MULTILINE)
                            if m2: bootstrap_current = m2.group(1)
                    try:
                        if is_newer(cloud_bootstrap_ver, bootstrap_current): bootstrap_update = cloud_bootstrap_ver
                    except Exception:
                        if cloud_bootstrap_ver != bootstrap_current: bootstrap_update = cloud_bootstrap_ver
        except Exception: pass

        project_id, _ = get_remote_credentials()
        req = get_request(f"https://sncloud.in/api/db/{project_id}/app/terminal.json?_t={int(time.time())}")
        with urllib.request.urlopen(req, context=get_context(), timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and data != 'null':
                cloud_ver = data.get('version', '1.0.0') if isinstance(data, dict) else '1.0.0'
                term_path = os.environ.get("VELORA_TERMINAL_PATH")
                if not term_path or not os.path.exists(term_path):
                    term_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
                
                local_ver = "1.0.0"
                if os.path.exists(term_path):
                    try:
                        with open(term_path, 'r', encoding='utf-8') as f:
                            m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.MULTILINE)
                            if m: local_ver = m.group(1)
                    except: pass
                else:
                    local_ver = os.environ.get("VELORA_VERSION", "1.0.0")

                app_current = local_ver
                if is_newer(cloud_ver, local_ver): app_update = cloud_ver
                    
        req = get_request(f"{get_base_url()}.json?_t={int(time.time())}")
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
                                if is_newer(cloud_ver, local_ver): pkg_updates.append((pkg, local_ver, cloud_ver))
                            except Exception: pass
                            
        velora_utils.print_header("Velora Update Center", color=velora_utils.PURPLE)
        
        # Terminal Status
        velora_utils.print_section("Terminal Application", color=velora_utils.CYAN)
        if app_update:
            velora_utils.print_status(f"Outdated: {velora_utils.RED}{app_current}{velora_utils.RESET} -> {velora_utils.GREEN}{app_update}{velora_utils.RESET}", type="warning")
            print(f"  {velora_utils.YELLOW}🔔 Run 'vpm upgrade' to install the new version.{velora_utils.RESET}")
        else:
            velora_utils.print_status(f"Up to date (v{app_current})", type="success")

        # Bootstrap Status
        velora_utils.print_section("Bootstrap Installer", color=velora_utils.CYAN)
        if bootstrap_update:
            velora_utils.print_status(f"Outdated: {velora_utils.RED}{bootstrap_current}{velora_utils.RESET} -> {velora_utils.GREEN}{bootstrap_update}{velora_utils.RESET}", type="warning")
            print(f"  {velora_utils.YELLOW}🔔 Re-run the bootstrap installer to update:{velora_utils.RESET}")
            if platform.system() == "Windows":
                cmd = 'powershell.exe -Command "cd $env:USERPROFILE; Invoke-WebRequest -Uri https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py -OutFile bootstrap.py; python bootstrap.py"'
            else:
                cmd = "curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3"
            print(f"  {velora_utils.CYAN}{velora_utils.BOLD}{cmd}{velora_utils.RESET}")
        else:
            velora_utils.print_status(f"Up to date (v{bootstrap_current})", type="success")

        # Package Status
        if pkg_updates:
            print(f"\n  {velora_utils.BOLD}{velora_utils.CYAN}Upgradable Packages:{velora_utils.RESET}")
            for p, l_ver, c_ver in pkg_updates: 
                print(f"  {velora_utils.PINK}• {p:<15}{velora_utils.RESET} {velora_utils.RED}{l_ver}{velora_utils.RESET} -> {velora_utils.GREEN}{c_ver}{velora_utils.RESET}")
            print(f"\n  {velora_utils.YELLOW}🔔 Run 'vpm update-all' to update {len(pkg_updates)} package(s).{velora_utils.RESET}")
        else:
            velora_utils.print_status("All local packages are up to date!", type="success")
            
    except Exception as e:
        velora_utils.print_status(f"Error checking updates: {e}", type="error")

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
                                    key = b"VeloraSuperSecureKeyForObfuscation2026!"
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
                        key = b"VeloraSuperSecureKeyForObfuscation2026!"
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
        url = f"{get_base_url()}/{urllib.parse.quote(pkg_name)}.json"
        
        req = get_request(url, data=payload, method='PUT')
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            velora_utils.print_status(f"Successfully published '{pkg_name}' to SNCloud!", type="success")
    except Exception as e:
        velora_utils.print_status(f"Error publishing package: {e}", type="error")

def unpublish_package(pkg_name):
    url = f"{get_base_url()}/{urllib.parse.quote(pkg_name)}.json"
    try:
        req = get_request(url, method='DELETE')
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            velora_utils.print_status(f"Successfully removed '{pkg_name}' from SNCloud!", type="success")
    except Exception as e:
        velora_utils.print_status(f"Error removing package from SNCloud: {e}", type="error")

def publish_core_files(password):
    if password != "86531Souvik@":
        velora_utils.print_status("Unauthorized. Incorrect password.", type="error")
        return
        
    velora_utils.print_status("Publishing all core files to SNCloud...", type="info")
    
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
    velora_utils.print_status(f"Finished publishing {count} core files.", type="success")

def publish_terminal():
    if IS_FROZEN:
        velora_utils.print_status("Cannot publish terminal source from a compiled native binary.", type="error")
        return
    target_path = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "terminal.py")
    if not os.path.exists(target_path):
        velora_utils.print_status(f"Local terminal file '{target_path}' not found.", type="error")
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
        project_id, _ = get_remote_credentials()
        url = f"https://sncloud.in/api/db/{project_id}/app/terminal.json"
        
        req = get_request(url, data=payload, method='PUT')
        
        with urllib.request.urlopen(req, context=get_context(), timeout=10) as response:
            velora_utils.print_status("Successfully published Velora Terminal to SNCloud!", type="success")
    except Exception as e:
        velora_utils.print_status(f"Error publishing terminal: {e}", type="error")

def build_executable():
    if IS_FROZEN:
        velora_utils.print_status("Already running a compiled binary.", type="error")
        return
    build_script = os.path.join(os.path.dirname(BUNDLED_CORE_DIR), "build.py")
    if os.path.exists(build_script):
        velora_utils.print_status("Building native executable using PyInstaller...", type="info")
        import subprocess
        try:
            subprocess.call([sys.executable, build_script])
        except Exception as e:
            print(f"\x1b[31;1mBuild error:\x1b[0m {e}")
    else:
        velora_utils.print_status("build.py not found in the project root.", type="error")

def main():
    # Force UTF-8 standard output to prevent 'charmap' encoding errors with emojis on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    args = sys.argv[1:]
    args = sys.argv[1:]
    if not args:
        velora_utils.print_header("Velora Package Manager (VPM)", color=velora_utils.PURPLE)
        print(f"  {velora_utils.BOLD}{velora_utils.YELLOW}Usage:{velora_utils.RESET}")
        
        help_table = velora_utils.Table(["Command", "Description"], colors=[velora_utils.CYAN, velora_utils.GREY])
        help_table.add_row(["list", "List all packages on SNCloud"])
        help_table.add_row(["local", "List local installed packages and versions"])
        help_table.add_row(["check", "Check SNCloud for available updates"])
        help_table.add_row(["locate <pkg>", "Show the installation path of a package"])
        help_table.add_row(["install <pkg>", "Download and install a package"])
        help_table.add_row(["install all", "Install all official verified packages"])
        help_table.add_row(["update <pkg>", "Update an installed package"])
        help_table.add_row(["update-all", "Update all installed packages"])
        help_table.add_row(["upgrade", "Upgrade the main Velora Terminal App"])
        help_table.add_row(["remove <pkg>", "Delete a local package"])
        help_table.add_row(["build", "Compile Velora to a standalone executable"])
        help_table.add_row(["publish <pkg> <file/dir>", "Upload a custom package to SNCloud"])
        help_table.add_row(["unpublish <pkg>", "Delete a package from SNCloud"])
        help_table.add_row(["publish-app", "Upload the core terminal source to SNCloud"])
        help_table.add_row(["publish-main <pwd>", "Upload all official core files (Admin)"])
        help_table.print()
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
            velora_utils.print_status(f"Package '{args[1]}' is not installed locally. Use 'vpm install {args[1]}' instead.", type="warning")
        else:
            velora_utils.print_status(f"Updating '{args[1]}'...", type="info")
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
            velora_utils.print_status(f"Removed user-updated package '{args[1]}'.", type="success")
            if os.path.exists(os.path.join(BUNDLED_CORE_DIR, f"{args[1]}.py")):
                create_wrapper(args[1])
            else:
                remove_wrapper(args[1])
        else:
            if os.path.exists(os.path.join(BUNDLED_CORE_DIR, f"{args[1]}.py")):
                velora_utils.print_status(f"Package '{args[1]}' is natively bundled with the compiled app and cannot be removed.", type="warning")
            else:
                velora_utils.print_status(f"Package '{args[1]}' is not installed locally.", type="error")
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
            velora_utils.print_status("Password required. Usage: vpm publish-main <password>", type="error")
    else:
        velora_utils.print_status("Invalid command or missing arguments.", type="error")

if __name__ == "__main__":
    main()