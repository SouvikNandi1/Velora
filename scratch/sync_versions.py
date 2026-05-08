import os
import re

core_dir = "/Users/souvik/Documents/velora/core"
files = [f for f in os.listdir(core_dir) if f.endswith('.py')]

for f in files:
    if f == 'chat.py': continue
    path = os.path.join(core_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if '__version__ =' in content:
        new_content = re.sub(r'__version__ = "[^"]+"', '__version__ = "2.2.0"', content)
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Updated {f} to 2.2.0")
    else:
        # For files like progressbar.py that might not have it
        new_content = '__version__ = "2.2.0"\n' + content
        with open(path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Added version to {f}")
