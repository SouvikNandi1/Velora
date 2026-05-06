__version__ = "1.0.1"
__description__ = "A fast Base64 encoder and decoder utility for encoding text directly from the command prompt."
__author__ = "Souvik"
__website__ = ""

import sys
import base64

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ('enc', 'dec'):
        print("\x1b[33mUsage:\x1b[0m b64 [enc|dec] <text>")
        return
        
    mode = args[0]
    text = " ".join(args[1:])
    
    try:
        if mode == 'enc':
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            print(f"\x1b[36;1mEncoded:\x1b[0m {result}")
        elif mode == 'dec':
            result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
            print(f"\x1b[36;1mDecoded:\x1b[0m {result}")
    except Exception as e:
        print(f"\x1b[31;1mError:\x1b[0m Invalid Base64 input.")

if __name__ == "__main__":
    main()