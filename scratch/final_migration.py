import os

CORE_DIR = "/Users/souvik/Documents/velora/core"
ROOT_DIR = "/Users/souvik/Documents/velora"

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    if "import terminal_utils" in content:
        content = content.replace("import terminal_utils", "import velora_utils")
        changed = True
    if "import velora_utils as terminal_utils" in content:
        content = content.replace("import velora_utils as terminal_utils", "import velora_utils")
        changed = True
    if "terminal_utils." in content:
        content = content.replace("terminal_utils.", "velora_utils.")
        changed = True
        
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

# Update core programs
for filename in os.listdir(CORE_DIR):
    if filename.endswith(".py"):
        update_file(os.path.join(CORE_DIR, filename))

# Update root files
update_file(os.path.join(ROOT_DIR, "terminal.py"))
update_file(os.path.join(ROOT_DIR, "vpm.py"))
