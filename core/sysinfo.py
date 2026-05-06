__version__ = "1.1.1"
__description__ = "Displays a quick and simple summary of your basic system architecture and host node information."
__author__ = "Souvik"
__website__ = ""

import platform
import os
import sys

def main():
    print("\x1b[36;1m=== Velora System Information ===\x1b[0m")
    user = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    print(f"\x1b[32mUser:\x1b[0m         {user}")
    print(f"\x1b[32mOS:\x1b[0m           {platform.system()} {platform.release()}")
    print(f"\x1b[32mArchitecture:\x1b[0m {platform.machine()}")
    print(f"\x1b[32mPython:\x1b[0m       {sys.version.split()[0]}")
    print(f"\x1b[32mHost Node:\x1b[0m    {platform.node()}")
    print("\x1b[36;1m=================================\x1b[0m")

if __name__ == "__main__":
    main()