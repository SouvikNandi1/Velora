__version__ = "1.0.3"
__description__ = "An OS-specific system fetch tool that prints an ASCII logo and system information including Kernel, Arch, and Python version."
__author__ = "Souvik"
__website__ = ""

import platform
import sys
import os
import re

def get_logo():
    system = platform.system()
    if system == "Darwin":
        return [
            "\x1b[32m                    'c.         \x1b[0m",
            "\x1b[32m                 ,xNMM.         \x1b[0m",
            "\x1b[32m               .OMMMMo          \x1b[0m",
            "\x1b[33m               OMMM0,           \x1b[0m",
            "\x1b[33m     .;loddo:' loolloddol;.     \x1b[0m",
            "\x1b[33m   cKMMMMMMMMMMNWMMMMMMMMMM0:   \x1b[0m",
            "\x1b[31m .KMMMMMMMMMMMMMMMMMMMMMMMWd.   \x1b[0m",
            "\x1b[31m XMMMMMMMMMMMMMMMMMMMMMMMX.     \x1b[0m",
            "\x1b[35m ;MMMMMMMMMMMMMMMMMMMMMMMM:     \x1b[0m",
            "\x1b[35m :MMMMMMMMMMMMMMMMMMMMMMMM:     \x1b[0m",
            "\x1b[34m .MMMMMMMMMMMMMMMMMMMMMMMMX.    \x1b[0m",
            "\x1b[34m  kMMMMMMMMMMMMMMMMMMMMMMMMWd.  \x1b[0m",
            "\x1b[36m  .XMMMMMMMMMMMMMMMMMMMMMMMMMMk \x1b[0m",
            "\x1b[36m   .XMMMMMMMMMMMMMMMMMMMMMMMMK. \x1b[0m",
            "\x1b[36m     kMMMMMMMMMMMMMMMMMMMMMMd   \x1b[0m",
            "\x1b[36m      ;KMMMMMMWMWNNNWMMMMWk.    \x1b[0m",
            "\x1b[36m        .cooc,.    .,coo:.      \x1b[0m"
        ]
    elif system == "Windows":
        return [
            "\x1b[38;2;127;186;0m                                ..,  \x1b[0m",
            "\x1b[38;2;127;186;0m                    ....,,:;+ccllll  \x1b[0m",
            "\x1b[38;2;242;80;34m      ...,,+:;  \x1b[38;2;127;186;0mcllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;242;80;34m,cclllllllllll  \x1b[38;2;127;186;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;242;80;34mllllllllllllll  \x1b[38;2;127;186;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;242;80;34mllllllllllllll  \x1b[38;2;127;186;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;242;80;34mllllllllllllll  \x1b[38;2;127;186;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;242;80;34mllllllllllllll  \x1b[38;2;127;186;0mlllllllllllllllllll  \x1b[0m",
            "                                     ",
            "\x1b[38;2;0;164;239mllllllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239mllllllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239mllllllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239mllllllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239mllllllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239m`'ccllllllllll  \x1b[38;2;255;185;0mlllllllllllllllllll  \x1b[0m",
            "\x1b[38;2;0;164;239m       `' \\*::  \x1b[38;2;255;185;0m:ccllllllllllllllll  \x1b[0m",
            "\x1b[38;2;255;185;0m                       ````''*::cll  \x1b[0m",
            "\x1b[38;2;255;185;0m                                 ``  \x1b[0m"
        ]
    elif system == "Linux":
        return [
            "\x1b[37;1m         .--.              \x1b[0m",
            "\x1b[37;1m        |o_o |             \x1b[0m",
            "\x1b[37;1m        |:_/ |             \x1b[0m",
            "\x1b[37;1m       //   \\ \\            \x1b[0m",
            "\x1b[33;1m      (|     | )           \x1b[0m",
            "\x1b[33;1m     /'\\_   _/`\\\\          \x1b[0m",
            "\x1b[33;1m     \\___)=(___/           \x1b[0m",
            f"\x1b[36;1m   {platform.system()} {platform.release()}   \x1b[0m"
        ]
    else:
        return [
            "\x1b[35;1m       /\\_/\\       \x1b[0m",
            "\x1b[35;1m      ( o.o )      \x1b[0m",
            "\x1b[35;1m       > ^ <       \x1b[0m",
            "\x1b[35;1m                   \x1b[0m"
        ]

def main():
    logo = get_logo()
    
    user = os.environ.get('USER', os.environ.get('USERNAME', 'user'))
    
    info = [
        f"\x1b[36;1mUser\x1b[0m:   {user}@{platform.node()}",
        f"\x1b[36;1mOS\x1b[0m:     {platform.system()} {platform.release()}",
        f"\x1b[36;1mHost\x1b[0m:   {platform.node()}",
        f"\x1b[36;1mKernel\x1b[0m: {platform.version()}",
        f"\x1b[36;1mArch\x1b[0m:   {platform.machine()}",
        f"\x1b[36;1mPython\x1b[0m: {platform.python_version()}"
    ]
    
    # Center the info text vertically relative to the logo
    vertical_padding = max(0, (len(logo) - len(info)) // 2)
    info = [""] * vertical_padding + info
    
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    pad_len = max(len(ansi_escape.sub('', line)) for line in logo)
    pad_str = " " * pad_len

    print()
    for i in range(max(len(logo), len(info))):
        l_str = logo[i] if i < len(logo) else pad_str
        i_str = info[i] if i < len(info) else ""
        print(f"  {l_str}   {i_str}")
    print()

if __name__ == "__main__":
    main()