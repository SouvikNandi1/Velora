__version__ = "1.0.1"
__description__ = "A dice roller for D&D or tabletop style rolling. Specify the number of dice and sides (e.g., 2d6)."
__author__ = "Souvik"
__website__ = ""

import random
import sys
import re

def main():
    args = sys.argv[1:]
    if not args:
        print("\x1b[33mUsage:\x1b[0m roll <NdM> [e.g., roll 2d6]")
        return

    expr = "".join(args).lower()
    match = re.match(r'^(\d*)d(\d+)$', expr)
    
    if match:
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        
        if count > 100 or sides > 1000:
            print("\x1b[31;1mError:\x1b[0m Too many dice or sides! (Max 100d1000)")
            return
            
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        print(f"\x1b[36;1mRolling {count}d{sides}:\x1b[0m {rolls} = \x1b[32;1m{total}\x1b[0m")
    else:
        print("\x1b[31;1mInvalid format.\x1b[0m Use NdM (e.g., 2d6).")

if __name__ == "__main__":
    main()