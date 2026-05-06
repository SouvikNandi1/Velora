__version__ = "1.0.1"
__description__ = "A fast URL encoder and decoder utility for formatting web strings safely."
__author__ = "Souvik"
__website__ = ""

import sys
import urllib.parse

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ('enc', 'dec'):
        print("\x1b[33mUsage:\x1b[0m url [enc|dec] <text>")
        return
        
    mode = args[0]
    text = " ".join(args[1:])
    
    if mode == 'enc':
        print(f"\x1b[36;1mEncoded:\x1b[0m {urllib.parse.quote(text)}")
    elif mode == 'dec':
        print(f"\x1b[36;1mDecoded:\x1b[0m {urllib.parse.unquote(text)}")

if __name__ == "__main__":
    main()