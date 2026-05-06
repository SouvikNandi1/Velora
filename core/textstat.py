__version__ = "1.0.1"
__description__ = "Calculates statistics for a given text or file, including word, line, and character counts."
__author__ = "Souvik"
__website__ = ""

import sys
import os

def main():
    args = sys.argv[1:]
    if not args:
        print("\x1b[33mUsage:\x1b[0m textstat <text_or_file_path>")
        return
    
    text = " ".join(args)
    if os.path.exists(args[0]) and os.path.isfile(args[0]):
        try:
            with open(args[0], 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"\x1b[36;1m=== File Statistics: {args[0]} ===\x1b[0m")
        except Exception as e:
            print(f"\x1b[31;1mError reading file:\x1b[0m {e}")
            return
    else:
        print("\x1b[36;1m=== Text Statistics ===\x1b[0m")

    chars = len(text)
    words = len(text.split())
    lines = len(text.splitlines()) if text.splitlines() else 1
    
    print(f"  \x1b[32mCharacters:\x1b[0m {chars}")
    print(f"  \x1b[32mWords:\x1b[0m      {words}")
    print(f"  \x1b[32mLines:\x1b[0m      {lines}")

if __name__ == "__main__":
    main()