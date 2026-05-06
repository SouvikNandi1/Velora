__version__ = "1.0.1"
__description__ = "Generates one or more random, unique v4 UUIDs."
__author__ = "Souvik"
__website__ = ""

import sys
import uuid

def main():
    count = 1
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
        
    for _ in range(count):
        print(f"\x1b[32;1m{uuid.uuid4()}\x1b[0m")

if __name__ == "__main__":
    main()