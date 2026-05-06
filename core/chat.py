#!/usr/bin/env python3
__version__ = "2.5.0"
__description__ = "A secure, E2EE Tor-based messenger with realtime discovery and encrypted local history."
__author__ = "Souvik"
__website__ = "https://github.com/SouvikNandi1/Velora"

import os
import json
import socket
import threading
import sys
import time
import shutil
import getpass
import urllib.request
import urllib.parse
import urllib.error
import select
from datetime import datetime

try:
    import msvcrt
except ImportError:
    import tty
    import termios

from stem.control import Controller
from stem.process import launch_tor_with_config
import socks
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

# Velora Builtins Fallback
try:
    _encrypt = encrypt_data # type: ignore
    _decrypt = decrypt_data # type: ignore
except NameError:
    _encrypt = lambda x: x
    _decrypt = lambda x: x

HISTORY_FILE = os.path.expanduser("~/.velora_chat_history")
CONTACTS_FILE = os.path.expanduser("~/.velora_chat_contacts")
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PATH = None 

class DataManager:
    def __init__(self):
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w') as f:
                f.write(_encrypt("[]"))
        if not os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, 'w') as f:
                f.write(_encrypt("[]"))

    def save_message(self, sender, message, encrypted_blob):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "message_text": message,
            "encrypted_blob": str(encrypted_blob)
        }
        
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.loads(_decrypt(f.read().strip()))
            data.append(entry)
            with open(HISTORY_FILE, 'w') as f:
                f.write(_encrypt(json.dumps(data, indent=4)))
        except Exception as e:
            print(f"\x1b[31;1mError saving data:\x1b[0m {e}")

    def get_contacts(self):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                return json.loads(_decrypt(f.read().strip()))
        except:
            return []

    def add_contact(self, name, onion):
        contacts = self.get_contacts()
        contacts.append({"name": name, "onion": onion})
        with open(CONTACTS_FILE, 'w') as f:
            f.write(_encrypt(json.dumps(contacts, indent=4)))

class EncryptionManager:
    def __init__(self):
        # Generate RSA Keys for initial handshake
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.symmetric_key = None
        self.cipher = None

    def get_public_pem(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def set_symmetric_key(self, key):
        self.symmetric_key = key
        self.cipher = Fernet(key)

    def encrypt_msg(self, message):
        if not self.cipher:
            raise Exception("Encryption handshake not complete.")
        return self.cipher.encrypt(message.encode())

    def decrypt_msg(self, encrypted_message):
        if not self.cipher:
            raise Exception("Encryption handshake not complete.")
        return self.cipher.decrypt(encrypted_message).decode()

class DiscoveryManager:
    def __init__(self):
        # Using ntfy.sh as a public signaling channel for discovery
        self.topic = "tor_chat_global_rooms_v2" 
        self.server_url = f"https://ntfy.sh/{self.topic}"
        self.live_rooms = {} # {onion: {name, last_seen}}
        self.running = False

    def announce_loop(self, name, onion):
        self.running = True
        # Send online immediately
        self.send_status(name, onion, "online")
        while self.running:
            try:
                self.send_status(name, onion, "heartbeat")
                time.sleep(15) # Heartbeat every 15s
            except:
                time.sleep(15)
        # Send offline
        self.send_status(name, onion, "offline")

    def send_status(self, name, onion, status):
        try:
            data = json.dumps({"n": name, "o": onion, "s": status, "t": time.time()}).encode('utf-8')
            req = urllib.request.Request(self.server_url, data=data, method='POST')
            urllib.request.urlopen(req)
        except: pass

    def listen_loop(self):
        self.running = True
        try:
            # Connect to JSON stream
            resp = urllib.request.urlopen(f"{self.server_url}/json")
            for line in resp:
                if not self.running: break
                if not line: continue
                try:
                    evt = json.loads(line)
                    if 'message' in evt:
                        payload = json.loads(evt['message'])
                        onion = payload['o']
                        if payload['s'] == 'offline':
                            if onion in self.live_rooms: del self.live_rooms[onion]
                        else:
                            self.live_rooms[onion] = {'name': payload['n'], 'onion': onion, 'last_seen': time.time()}
                except: pass
        except: pass

class TorChat:
    def __init__(self):
        self.data_mgr = DataManager()
        self.crypto = EncryptionManager()
        self.peer_socket = None
        self.tor_process = None
        self.host_password = None
        self.client_password = None
        self.discovery = DiscoveryManager()
        self.host_name = "Anonymous"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        self.clear_screen()
        print(f"\x1b[36;1m============================================\x1b[0m")
        print(f"\x1b[1m    Velora Secure Messenger\x1b[0m")
        print(f"\x1b[90m    Version: {__version__}\x1b[0m")
        print(f"\x1b[36;1m============================================\x1b[0m\n")

    def get_key(self, timeout=None):
        """Reads a keypress for menu navigation with optional timeout."""
        if os.name == 'nt':
            start_time = time.time()
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\xe0':
                        key = msvcrt.getch()
                        if key == b'H': return 'up'
                        if key == b'P': return 'down'
                    if key == b'\r': return 'enter'
                    if key == b'\x03': sys.exit()
                    return key.decode('utf-8', errors='ignore')
                if timeout and (time.time() - start_time) > timeout: return None
                time.sleep(0.05)
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                rlist, _, _ = select.select([sys.stdin], [], [], timeout if timeout else None)
                if rlist:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        seq = sys.stdin.read(2)
                        if seq == '[A': return 'up'
                        if seq == '[B': return 'down'
                    if ch == '\r' or ch == '\n': return 'enter'
                    if ch == '\x03': sys.exit()
                    return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def select_contact_menu(self, contacts):
        current_idx = 0
        options = contacts + [{"name": "Enter new address", "onion": "Manual Entry"}, {"name": "Scan Live Networks", "onion": "SCAN_LIVE"}]
        
        while True:
            self.print_banner()
            print(f"\x1b[36;1m--- SELECT CONTACT (Use Up/Down/Enter) ---\x1b[0m")
            
            for idx, option in enumerate(options):
                if idx == current_idx:
                    print(f"\x1b[32;1m > {option['name']} ({option['onion']})\x1b[0m")
                else:
                    print(f"\x1b[34m   {option['name']} ({option['onion']})\x1b[0m")
            
            key = self.get_key()
            if key == 'up': current_idx = (current_idx - 1) % len(options)
            elif key == 'down': current_idx = (current_idx + 1) % len(options)
            elif key == 'enter': return options[current_idx]

    def scan_live_networks(self):
        self.discovery.live_rooms = {}
        # Start listener thread
        t = threading.Thread(target=self.discovery.listen_loop, daemon=True)
        t.start()
        
        current_idx = 0
        bar_width = 30
        bar_pos = 0
        bar_dir = 1

        while True:
            # Prune old rooms (>45s)
            now = time.time()
            active_rooms = [r for r in self.discovery.live_rooms.values() if now - r['last_seen'] < 45]
            
            self.print_banner()
            print(f"\x1b[36;1m--- LIVE GLOBAL NETWORKS (Realtime) ---\x1b[0m")
            
            # Progress Bar Animation
            bar_chars = [" "] * bar_width
            for i in range(3): # Block size of 3
                if 0 <= bar_pos + i < bar_width:
                    bar_chars[bar_pos + i] = "█"
            bar_str = "".join(bar_chars)
            
            print(f"\x1b[33mScanning: [{bar_str}] (Press Enter to join, 'q' to back)\x1b[0m\n")
            
            if not active_rooms:
                print(f"   \x1b[31mNo active rooms found yet...\x1b[0m")
            
            for idx, room in enumerate(active_rooms):
                prefix = f"\x1b[32;1m >" if idx == current_idx else f"\x1b[34m  "
                print(f"{prefix} {room['name']} ({room['onion']})\x1b[0m")
            
            key = self.get_key(timeout=0.1) # Refresh every 0.1s
            
            # Update bar position
            bar_pos += bar_dir
            if bar_pos >= bar_width - 3 or bar_pos <= 0:
                bar_dir *= -1

            if key == 'up': current_idx = (current_idx - 1) % len(active_rooms) if active_rooms else 0
            elif key == 'down': current_idx = (current_idx + 1) % len(active_rooms) if active_rooms else 0
            elif key == 'enter' and active_rooms: return active_rooms[current_idx]['onion']
            elif key == 'q': return None

    def ensure_tor(self):
        """Ensures Tor is either running or installed."""
        # Check if a Tor proxy is already active (System Tor or Tor Browser)
        for port in [9050, 9150]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.2)
                    if s.connect_ex(('127.0.0.1', port)) == 0:
                        return True
            except: pass

        # Check if tor executable is available in PATH
        if shutil.which("tor"):
            return True
            
        # Check common Windows installation paths for Tor Browser bundled Tor
        if os.name == 'nt':
            for p in [r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                      os.path.expanduser(r"~\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe")]:
                if os.path.exists(p):
                    global TOR_PATH
                    TOR_PATH = p
                    return True
                    
        print("\x1b[31;1m[!] Tor not detected.\x1b[0m")
        print("\x1b[33mMessenger requires Tor to establish secure onion-routed connections.\x1b[0m")
        print("\x1b[32;1mTip: Run the 'install_tor' command to install it automatically.\x1b[0m")
        input("\nPress Enter to return to menu...")
        return False

    def start_server(self):
        """Creates an ephemeral Hidden Service and listens."""
        if not self.ensure_tor(): return
        self.print_banner()
        print(f"\x1b[33m[*] CONFIGURING HOST SESSION\x1b[0m")
        self.host_name = input(f"\x1b[32;1mEnter a Public Name for Live List: \x1b[0m")
        self.host_password = getpass.getpass(f"\x1b[33mSet a Session Password (hidden): \x1b[0m")
        
        print("[*] Connecting to Tor Control Port...")
        try:
            controller = Controller.from_port(port=TOR_CONTROL_PORT)
            controller.authenticate() # Ensure you have Tor auth configured or cookie auth enabled
        except Exception as e:
            print(f"[!] System Tor not accessible: {e}")
            print("[*] Attempting to launch bundled Tor instance...")

            def print_bootstrap_lines(line):
                if "Bootstrapped " in line:
                    print(f"    {line}")

            try:
                self.tor_process = launch_tor_with_config(
                    config={
                        'SocksPort': str(TOR_SOCKS_PORT),
                        'ControlPort': str(TOR_CONTROL_PORT),
                        'DataDirectory': os.path.expanduser("~/.velora/tor_data")
                    },
                    tor_cmd=TOR_PATH if TOR_PATH else "tor",
                    take_ownership=True,
                    timeout=300,
                    init_msg_handler=print_bootstrap_lines,
                )
                controller = Controller.from_port(port=TOR_CONTROL_PORT)
                controller.authenticate()
            except Exception as e2:
                print(f"[!] Failed to launch Tor: {e2}")
                return

        # Setup local listener first to avoid Connection Refused (0x05)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        local_port = 5000
        while True:
            try:
                server_sock.bind(('127.0.0.1', local_port))
                break
            except OSError:
                local_port += 1

        server_sock.listen(1)

        print("[*] Creating Ephemeral Onion Service...")
        # Create a hidden service that maps port 80 of the onion to local port 5000
        response = controller.create_ephemeral_hidden_service({80: local_port}, await_publication=True)
        onion_address = f"{response.service_id}.onion"
        
        self.clear_screen()
        print(f"\x1b[36;1m╔══════════════════════════════════════════════════════╗\x1b[0m")
        print(f"\x1b[36;1m║  YOUR ONION LINK (Share this):                       ║\x1b[0m")
        print(f"\x1b[32;1m║  {onion_address:<51} ║\x1b[0m")
        print(f"\x1b[36;1m╚══════════════════════════════════════════════════════╝\x1b[0m")
        print(f"\n\x1b[33m[*] Waiting for peer to join... (Realtime)\x1b[0m")

        # Start Discovery Announcement
        disc_thread = threading.Thread(target=self.discovery.announce_loop, args=(self.host_name, onion_address), daemon=True)
        disc_thread.start()

        conn, addr = server_sock.accept()
        print(f"[+] Connection received!")
        self.peer_socket = conn
        
        if self.perform_handshake_server():
            self.chat_loop("Server")
        
        self.discovery.running = False # Stop announcing

    def connect_client(self):
        """Connects to a Hidden Service via Tor SOCKS proxy."""
        if not self.ensure_tor(): return
        contacts = self.data_mgr.get_contacts()
        
        # Use interactive menu
        selected = self.select_contact_menu(contacts)
        
        if selected['onion'] == "Manual Entry":
            onion_address = input("Enter Onion Address (e.g., xyz.onion): ")
            save = input("Save this contact? (y/n): ")
            if save.lower() == 'y':
                name = input("Enter Name: ")
                self.data_mgr.add_contact(name, onion_address)
        elif selected['onion'] == "SCAN_LIVE":
            onion_address = self.scan_live_networks()
            if not onion_address: return # Back pressed
            self.discovery.running = False # Stop listening
        else:
            onion_address = selected['onion']

        self.client_password = getpass.getpass(f"\x1b[33mEnter Host Password (hidden): \x1b[0m")
        
        # Detect available SOCKS port (9050 for System Tor, 9150 for Tor Browser)
        active_port = TOR_SOCKS_PORT
        for port in [9050, 9150]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_check:
                    s_check.settimeout(0.5)
                    if s_check.connect_ex(('127.0.0.1', port)) == 0:
                        active_port = port
                        break
            except:
                pass

        print(f"[*] Using Tor SOCKS Port: {active_port}")
        print(f"[*] Connecting to {onion_address} via Tor...")
        
        # Patch socket to use Tor SOCKS
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", active_port, rdns=True)
        socket.socket = socks.socksocket

        # Retry loop for connection (Tor HS can take time to propagate)
        for i in range(1, 11):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(30)
                s.connect((onion_address, 80))
                self.peer_socket = s
                print("[+] Connected!")
                
                if self.perform_handshake_client():
                    s.settimeout(None) # Remove timeout for chat session
                    self.chat_loop("Client")
                return
            except Exception as e:
                print(f"[!] Attempt {i}/10 failed: {e}")
                if i < 10:
                    print("    Retrying in 5 seconds... (Waiting for descriptor propagation)")
                    time.sleep(5)
        
        print("[!] Final connection failure. Check onion address or host status.")

    def perform_handshake_server(self):
        """
        Server sends Public RSA Key.
        Client generates Symmetric Key, encrypts with RSA, sends back.
        """
        print("[*] Performing E2EE Handshake...")
        # 1. Send Public Key
        pub_pem = self.crypto.get_public_pem()
        self.peer_socket.sendall(pub_pem)

        # 2. Receive Encrypted Symmetric Key
        encrypted_sym_key = b""
        while len(encrypted_sym_key) < 256:
            chunk = self.peer_socket.recv(256 - len(encrypted_sym_key))
            if not chunk:
                raise ConnectionError("Socket closed during handshake")
            encrypted_sym_key += chunk
        
        # 3. Decrypt Symmetric Key
        sym_key = self.crypto.private_key.decrypt(
            encrypted_sym_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.crypto.set_symmetric_key(sym_key)
        print("[+] E2EE Established (AES-128).")
        
        # 4. Verify Password
        print("[*] Verifying Password...")
        encrypted_pass = self.peer_socket.recv(4096)
        password = self.crypto.decrypt_msg(encrypted_pass)
        if password == self.host_password:
            self.peer_socket.send(self.crypto.encrypt_msg("AUTH_SUCCESS"))
            print(f"\x1b[32;1m[+] Password Accepted. Chat starting.\x1b[0m")
            return True
        else:
            self.peer_socket.send(self.crypto.encrypt_msg("AUTH_FAILED"))
            print(f"\x1b[31;1m[!] Invalid Password attempted.\x1b[0m")
            self.peer_socket.close()
            return False

    def perform_handshake_client(self):
        print("[*] Performing E2EE Handshake...")
        # 1. Receive Server Public Key
        received_data = b""
        while b"-----END PUBLIC KEY-----" not in received_data:
            chunk = self.peer_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Socket closed during handshake")
            received_data += chunk
        
        server_pub_key = serialization.load_pem_public_key(received_data)

        # 2. Generate Symmetric Key (Fernet)
        sym_key = Fernet.generate_key()
        self.crypto.set_symmetric_key(sym_key)

        # 3. Encrypt Symmetric Key with Server's Public Key
        encrypted_sym_key = server_pub_key.encrypt(
            sym_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.peer_socket.sendall(encrypted_sym_key)
        print("[+] E2EE Established (AES-128).")
        
        # 4. Send Password
        print("[*] Sending Password...")
        self.peer_socket.send(self.crypto.encrypt_msg(self.client_password))
        response = self.peer_socket.recv(4096)
        status = self.crypto.decrypt_msg(response)
        if status == "AUTH_SUCCESS":
            print(f"\x1b[32;1m[+] Password Accepted.\x1b[0m")
            return True
        else:
            print(f"\x1b[31;1m[!] Password Rejected by Host.\x1b[0m")
            return False

    def receive_messages(self):
        while True:
            try:
                data = self.peer_socket.recv(4096)
                if not data:
                    print(f"\n\x1b[31;1m[!] Peer has left the chat. Press Enter to exit.\x1b[0m")
                    break
                
                # Decrypt
                decrypted_msg = self.crypto.decrypt_msg(data)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n\x1b[34m[{timestamp}] Peer: {decrypted_msg}\x1b[0m")
                print(f"\x1b[32;1m[You]: \x1b[0m", end="", flush=True)
                
                # Save to JSON
                self.data_mgr.save_message("Peer", decrypted_msg, data)
            except Exception as e:
                print(f"\n\x1b[31;1m[!] Connection lost: {e}\x1b[0m")
                break

    def chat_loop(self, role):
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.clear_screen()
        print(f"\x1b[36;1m--- SECURE CHAT STARTED (Realtime) -- Type 'quit' to exit ---\x1b[0m")
        while True:
            msg = input(f"\x1b[32;1m[You]: \x1b[0m")
            if msg.lower() == 'quit':
                break
            
            if msg.strip():
                try:
                    encrypted_data = self.crypto.encrypt_msg(msg)
                    if hasattr(self.peer_socket, 'sendall'):
                        self.peer_socket.sendall(encrypted_data)
                    self.peer_socket.send(encrypted_data)
                    
                    # Save to JSON
                    self.data_mgr.save_message("Me", msg, encrypted_data)
                except Exception as e:
                    print(f"[!] Error sending: {e}")
                    break
        
        try:
            self.peer_socket.close()
        except:
            pass

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    chat_app = TorChat()
    chat_app.clear_screen()
    while True:
        print(f"\n\x1b[36;1m=== Velora Messenger v{__version__} ===\x1b[0m")
        print("  \x1b[33m1.\x1b[0m Host a Secure Chat")
        print("  \x1b[33m2.\x1b[0m Connect to a Chat")
        print("  \x1b[33m3.\x1b[0m Exit")
        choice = input(f"\n\x1b[32;1mSelect option: \x1b[0m")

        if choice == '1':
            chat_app.start_server()
        elif choice == '2':
            chat_app.connect_client()
        elif choice == '3':
            break
        else:
            print("\x1b[31mInvalid choice.\x1b[0m")

if __name__ == "__main__":
    main()
