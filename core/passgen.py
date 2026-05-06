__version__ = "1.0.1"
__description__ = "A secure random password generator. By default generates a 16-character password containing letters, numbers, and symbols."
__author__ = "Souvik"
__website__ = ""

import sys
import random
import string

def main():
    length = 16
    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Length must be a number.")
            return
            
    if length < 4 or length > 128:
        print("\x1b[31;1mError:\x1b[0m Length must be between 4 and 128.")
        return
        
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    password = ''.join(random.choice(chars) for _ in range(length))
    
    print(f"\x1b[32;1mGenerated Password ({length} chars):\x1b[0m\n{password}")

if __name__ == "__main__":
    main()