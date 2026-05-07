import os
import re

CORE_DIR = "/Users/souvik/Documents/velora/core"

MAPPING = {
    # Tools
    "calc.py": "🛠️ Tools",
    "unitconv.py": "🛠️ Tools",
    "baseconv.py": "🛠️ Tools",
    "hash.py": "🛠️ Tools",
    "hashfile.py": "🛠️ Tools",
    "textstat.py": "🛠️ Tools",
    "todo.py": "🛠️ Tools",
    "notes.py": "🛠️ Tools",
    "passgen.py": "🛠️ Tools",
    "uuidgen.py": "🛠️ Tools",
    "url.py": "🛠️ Tools",
    "b32.py": "🛠️ Tools",
    "b64.py": "🛠️ Tools",
    "jsonfmt.py": "🛠️ Tools",
    "currency.py": "🛠️ Tools",
    "translator.py": "🛠️ Tools",
    "timer.py": "🛠️ Tools",
    "stopwatch.py": "🛠️ Tools",
    "cal.py": "🛠️ Tools",
    # System
    "fetch.py": "🖥️ System",
    "ipinfo.py": "🖥️ System",
    "sysinfo.py": "🖥️ System",
    "weather.py": "🖥️ System",
    "worldclock.py": "🖥️ System",
    "install_tor.py": "🖥️ System",
    # Fun
    "quote.py": "✨ Fun",
    "matrix.py": "✨ Fun",
    "roll.py": "✨ Fun",
    "chat.py": "✨ Fun",
    # Games
    "snake.py": "🎮 Games"
}

for filename, category in MAPPING.items():
    filepath = os.path.join(CORE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if already has category
        has_cat = False
        for line in lines:
            if line.startswith("__category__"):
                has_cat = True
                break
        
        if not has_cat:
            # Insert after __author__ or at top
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("__author__") or line.startswith("__description__"):
                    insert_idx = i + 1
            
            lines.insert(insert_idx, f'__category__ = "{category}"\n')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Updated {filename} with category {category}")
        else:
            print(f"{filename} already has category.")
