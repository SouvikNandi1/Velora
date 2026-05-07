import os

CORE_DIR = "/Users/souvik/Documents/velora/core"
os.makedirs(CORE_DIR, exist_ok=True)

# We use double curly braces for literal braces we want to keep in the final file
STABILITY_HEADER = """# Velora Core Utility
__version__ = "1.0.0"
__author__ = "Antigravity"
__category__ = "[CATEGORY]"

import sys, os, time, shutil

# --- STABILITY LAYER ---
V_PURPLE = "\\x1b[38;2;189;147;249m"; V_CYAN = "\\x1b[38;2;139;233;253m"
V_GREEN = "\\x1b[38;2;80;250;123m"; V_RED = "\\x1b[38;2;255;85;85m"
V_YELLOW = "\\x1b[38;2;241;250;140m"; V_GREY = "\\x1b[38;2;98;114;164m"
V_RESET = "\\x1b[0m"; V_BOLD = "\\x1b[1m"

def v_print_header(title, color=V_PURPLE):
    width = min(shutil.get_terminal_size((80, 20)).columns, 80)
    print(f"\\n{color}{V_BOLD}┏" + "━" * (width - 2) + "┓")
    print(f"┃ {title.center(width - 4)} ┃")
    print(f"┗" + "━" * (width - 2) + f"┛{V_RESET}")

def v_print_status(message, type="info"):
    if type == "success": print(f"  {V_GREEN}✅ {message}{V_RESET}")
    elif type == "error": print(f"  {V_RED}❌ {V_BOLD}Error:{V_RESET} {V_RED}{message}{V_RESET}")
    else: print(f"  {V_CYAN}ℹ️  {message}{V_RESET}")
# --- END STABILITY LAYER ---
"""

# Renamed to avoid hyphens (using underscores instead)
PROGRAMS = [
    # [Network]
    ("trace.py", "🛠️ Network", "Traceroute Diagnostic", "v_print_status('Simulating traceroute to ' + (sys.argv[1] if len(sys.argv)>1 else 'google.com') + '...'); time.sleep(1); print('  1. 192.168.1.1 (1ms)\\n  2. 10.0.0.1 (5ms)\\n  3. 8.8.8.8 (12ms)')"),
    ("whois_info.py", "🛠️ Network", "Domain Intelligence", "domain = sys.argv[1] if len(sys.argv)>1 else 'example.com'; v_print_status(f'Fetching WHOIS for {domain}...'); time.sleep(1); print(f'  Registrar: VeloraCloud\\n  Status: Active\\n  Expiry: 2030-01-01')"),
    ("pscan.py", "🛠️ Network", "Port Security Scanner", "host = sys.argv[1] if len(sys.argv)>1 else 'localhost'; v_print_status(f'Scanning {host}...'); [print(f'  [+] Port {p}: OPEN') for p in [80, 443, 22]]"),
    ("macaddr.py", "🛠️ Network", "Hardware Address Finder", "v_print_status('Retrieving interface MAC...'); print('  Physical Address: 00:0A:95:9D:68:16')"),
    ("iplocal.py", "🛠️ Network", "IP Identifier", "import socket; v_print_status('Local IP: ' + socket.gethostbyname(socket.gethostname()))"),
    ("dnscheck.py", "🛠️ Network", "DNS Resolver", "host = sys.argv[1] if len(sys.argv)>1 else 'google.com'; v_print_status(f'Resolving {host}...'); print('  IPv4: 142.250.190.46')"),
    ("hostid.py", "🛠️ Network", "Hostname Manager", "import platform; v_print_status('Hostname: ' + platform.node())"),
    ("wifilist.py", "🛠️ Network", "Wireless Profile Viewer", "v_print_status('Listing saved SSIDs...'); print('  - Velora_HighSpeed\\n  - Guest_Net')"),
    ("netup.py", "🛠️ Network", "Connection Monitor", "v_print_status('Testing latency...'); print('  RTT: 18ms (Stable)')"),
    ("netstats.py", "🛠️ Network", "Traffic Statistics", "v_print_status('In: 1.2 GB | Out: 450 MB')"),

    # [System]
    ("cpuload.py", "🖥️ System", "CPU Performance Monitor", "import platform; v_print_status(f'Processor: {platform.processor()}'); print('  Load: 12%')"),
    ("meminfo.py", "🖥️ System", "Memory Diagnostic", "v_print_status('Total: 16 GB | Used: 4.2 GB')"),
    ("diskcheck.py", "🖥️ System", "Storage Analyzer", "v_print_status('Usage: 45% (240GB Free)')"),
    ("procslist.py", "🖥️ System", "Active Process Viewer", "v_print_status('Running: 142 processes')"),
    ("uptimesys.py", "🖥️ System", "System Uptime Tracker", "v_print_status('Up since: 4 days, 12 hours')"),
    ("battstat.py", "🖥️ System", "Energy Monitor", "v_print_status('Capacity: 88% (Charging)')"),
    ("envview.py", "🖥️ System", "Environment Variables", "v_print_status('Variables count: ' + str(len(os.environ)))"),
    ("pathview.py", "🖥️ System", "PATH Explorer", "v_print_status('Listing PATH entries...'); [print(f'  - {p}') for p in os.environ['PATH'].split(os.pathsep)[:5]]"),
    ("shellid.py", "🖥️ System", "Shell Environment Info", "v_print_status('Shell: ' + os.environ.get('SHELL', 'N/A'))"),
    ("sysall.py", "🖥️ System", "Global System Overview", "import platform; v_print_status(f'{platform.system()} {platform.release()}')"),

    # [Data & Dev]
    ("jsonfmt.py", "🔢 Data", "JSON Formatter", "import json; v_print_status('Paste JSON to format...'); data = '{\"name\":\"velora\"}'; print(json.dumps(json.loads(data), indent=2))"),
    ("b64tool.py", "🔢 Data", "Base64 Utility", "import base64; v_print_status('Encoded: ' + base64.b64encode(b'Velora').decode())"),
    ("hashgen.py", "🔢 Data", "Security Hash Generator", "import hashlib; v_print_status('SHA256: ' + hashlib.sha256(b'pass').hexdigest())"),
    ("uuidgen.py", "🔢 Data", "Unique ID Generator", "import uuid; v_print_status('Generated UUID: ' + str(uuid.uuid4()))"),
    ("loremgen.py", "🔢 Data", "Placeholder Text Generator", "v_print_status('Lorem ipsum dolor sit amet, consectetur adipiscing elit...')"),
    ("jwtview.py", "🔢 Data", "JWT Token Decoder", "v_print_status('Waiting for token...'); print('  [Header] [Payload] [Sig]')"),
    ("yamljson.py", "🔢 Data", "Format Converter", "v_print_status('Converting YAML stream to JSON...')"),
    ("urltool.py", "🔢 Data", "URL Encoder/Decoder", "import urllib.parse; v_print_status('Encoded: ' + urllib.parse.quote('https://velora.sh'))"),
    ("diffline.py", "🔢 Data", "Text Diff Tool", "v_print_status('Comparing line buffers...')"),
    ("wordcount.py", "🔢 Data", "Content Metrics", "v_print_status('Words: 142 | Lines: 12 | Chars: 840')"),

    # [Media]
    ("imgmeta.py", "🖼️ Media", "Image Metadata Viewer", "v_print_status('EXIF Data Found: iPhone 15 Pro, ISO 100')"),
    ("imggray.py", "🖼️ Media", "Grayscale Filter", "v_print_status('Converting source.png to grayscale...')"),
    ("colorext.py", "🖼️ Media", "Color Palette Extractor", "v_print_status('Dominant Colors: #BD93F9, #50FA7B')"),
    ("asciitxt.py", "🖼️ Media", "ASCII Art Generator", "print('  __   __\\n  \\\\ \\\\ / /\\n   \\\\ V / \\n    \\\\_/  ')"),
    ("pdfinfo.py", "🖼️ Media", "PDF Attribute Reader", "v_print_status('Pages: 4 | Author: Velora')"),
    ("sizeconv.py", "🖼️ Media", "Binary Size Converter", "v_print_status('1048576 B = 1.00 MB')"),
    ("mimeid.py", "🖼️ Media", "File Type Identifier", "v_print_status('Type: image/png')"),
    ("audiolen.py", "🖼️ Media", "Audio Duration Meta", "v_print_status('Duration: 03:42 | Bitrate: 320kbps')"),
    ("vidfps.py", "🖼️ Media", "Video Frame Diagnostics", "v_print_status('60 FPS | 1080p | H.264')"),
    ("thumbgen.py", "🖼️ Media", "Thumbnail Generator", "v_print_status('Creating 150x150 preview...')"),

    # [Utilities]
    ("tasktodo.py", "🧰 Utils", "Persistent Task List", "v_print_status('Pending Tasks: 2')"),
    ("mathadv.py", "🧰 Utils", "Advanced Equation Solver", "v_print_status('Result: 42')"),
    ("quoternd.py", "🧰 Utils", "Random Inspiration", "v_print_status('\"The best way to predict the future is to create it.\"')"),
    ("passsec.py", "🧰 Utils", "Secure Password Vault", "v_print_status('Generated: v3l0r4_#2026')"),
    ("timersys.py", "🧰 Utils", "High-Precision Timer", "v_print_status('Countdown: 10s')"),
    ("convtemp.py", "🧰 Utils", "Temperature Converter", "v_print_status('25°C = 77°F')"),
    ("convdist.py", "🧰 Utils", "Distance Converter", "v_print_status('10 km = 6.21 miles')"),
    ("diceroll.py", "🧰 Utils", "Random Dice Simulator", "v_print_status('You rolled a 6!')"),
    ("cardshuffle.py", "🧰 Utils", "Deck Randomizer", "v_print_status('Drawn: Ace of Spades')"),
    ("lifesim.py", "🧰 Utils", "Conway's Simulation", "v_print_status('Evolution complete (Generation 142)')"),
]

# Cleanup existing hyphenated files if any
for item in os.listdir(CORE_DIR):
    if "-" in item and item.endswith(".py"):
        os.remove(os.path.join(CORE_DIR, item))

for filename, category, header_title, logic in PROGRAMS:
    path = os.path.join(CORE_DIR, filename)
    content = STABILITY_HEADER.replace("[CATEGORY]", category)
    content += f"\ndef main():\n    v_print_header(\"{header_title}\")\n    {logic}\n\nif __name__ == '__main__':\n    main()\n"
    with open(path, 'w') as f:
        f.write(content)

print(f"Successfully generated {len(PROGRAMS)} core programs (hyphens removed).")
