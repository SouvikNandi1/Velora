__version__ = "1.0.1"
__description__ = "Computes cryptographic hashes (MD5, SHA1, SHA256) for a given text string."
__author__ = "Souvik"
__website__ = ""

import sys
import hashlib

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("\x1b[33mUsage:\x1b[0m hash [md5|sha1|sha256] <text>")
        return
    
    algo = args[0].lower()
    text = " ".join(args[1:])
    
    if algo == 'md5':
        result = hashlib.md5(text.encode()).hexdigest()
    elif algo == 'sha1':
        result = hashlib.sha1(text.encode()).hexdigest()
    elif algo == 'sha256':
        result = hashlib.sha256(text.encode()).hexdigest()
    else:
        print(f"\x1b[31;1mError:\x1b[0m Unsupported algorithm '{algo}'. Use md5, sha1, or sha256.")
        return
        
    print(f"\x1b[36;1m{algo.upper()}:\x1b[0m {result}")

if __name__ == "__main__":
    main()