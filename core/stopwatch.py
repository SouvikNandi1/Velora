__version__ = "1.0.1"
__description__ = "A visual command-line stopwatch that counts up until stopped with Ctrl+C."
__author__ = "Souvik"
__website__ = ""

import sys
import time

def main():
    print("\x1b[36;1mStarting stopwatch... Press Ctrl+C to stop.\x1b[0m")
    start_time = time.time()
    try:
        while True:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            hrs, mins = divmod(mins, 60)
            timeformat = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"
            sys.stdout.write(f"\r\x1b[32;1m⏱️  {timeformat}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        hrs, mins = divmod(mins, 60)
        timeformat = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"
        print(f"\n\n\x1b[31;1mStopwatch stopped at {timeformat}\x1b[0m")

if __name__ == "__main__":
    main()