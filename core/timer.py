__version__ = "1.0.1"
__description__ = "A visual command-line countdown timer that displays remaining minutes and seconds directly in the prompt."
__author__ = "Souvik"
__website__ = ""

import sys
import time

def main():
    if len(sys.argv) < 2:
        print("\x1b[33mUsage:\x1b[0m timer <seconds>")
        return
    try:
        seconds = int(sys.argv[1])
    except ValueError:
        print("\x1b[31;1mError:\x1b[0m Please provide a valid number of seconds.")
        return

    print(f"\x1b[36;1mStarting timer for {seconds} seconds...\x1b[0m")
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timeformat = f"{mins:02d}:{secs:02d}"
            sys.stdout.write(f"\r\x1b[32;1m⏳ {timeformat}\x1b[0m")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        sys.stdout.write("\r\x1b[32;1m⏳ 00:00\x1b[0m\n")
        print("\x1b[31;1m⏰ Time's up!\x1b[0m")
    except KeyboardInterrupt:
        print("\n\x1b[31mTimer stopped.\x1b[0m")

if __name__ == "__main__":
    main()