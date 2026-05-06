# progress_bar.py
import time
import sys

total = 100

for i in range(total + 1):
    bar = "#" * (i // 2) + "-" * ((total - i) // 2)
    sys.stdout.write(f"\r[{bar}] {i}%")
    sys.stdout.flush()
    time.sleep(0.05)

print("\nDone!")