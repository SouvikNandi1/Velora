__version__ = "1.0.1"
__description__ = "Displays a classic falling green code matrix effect in the terminal."
__author__ = "Souvik"
__website__ = ""

import sys
import time
import random
import os

def main():
    print("\x1b[?25l") # Hide cursor
    width = 80
    if os.name != 'nt':
        try:
            width = os.get_terminal_size().columns
        except OSError:
            pass
            
    drops = [0] * width
    try:
        while True:
            line = ""
            for i in range(width):
                if drops[i] > 0:
                    if random.random() > 0.1:
                        line += f"\x1b[32;1m{chr(random.randint(33, 126))}\x1b[0m"
                    else:
                        line += f"\x1b[37;1m{chr(random.randint(33, 126))}\x1b[0m"
                    drops[i] -= 1
                else:
                    line += " "
                    if random.random() < 0.05:
                        drops[i] = random.randint(5, 20)
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\x1b[?25h\x1b[0m") # Show cursor, reset color

if __name__ == "__main__":
    main()