import os
import re

core_dir = "/Users/souvik/Documents/velora/core"
files = [f for f in os.listdir(core_dir) if f.endswith('.py')]

versions = {}
for f in files:
    path = os.path.join(core_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        match = re.search(r'__version__ = "([^"]+)"', content)
        if match:
            versions[f] = match.group(1)
        else:
            versions[f] = "NONE"

for f, v in sorted(versions.items()):
    print(f"{f:<20} {v}")
