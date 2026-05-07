import os

CORE_DIR = "/Users/souvik/Documents/velora/core"

for filename in os.listdir(CORE_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(CORE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "import terminal_utils" in content:
            new_content = content.replace("import terminal_utils", "import velora_utils as terminal_utils")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")

# Also update the root terminal.py and vpm.py if not already done
# (I already did them, but good to check)
