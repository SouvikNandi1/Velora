__version__ = "1.4.1"
__description__ = "A quick text note-taking tool to jot down references or ideas. Saves persistently to ~/.velora_notes."
__author__ = "Souvik"
__website__ = ""

import os
import sys

# Safely resolve dynamic builtins injected by Velora Terminal, with plaintext fallbacks
try:
    _encrypt = encrypt_data # type: ignore
    _decrypt = decrypt_data # type: ignore
except NameError:
    _encrypt = lambda x: x # Fallback for non-Velora execution
    _decrypt = lambda x: x # Fallback for non-Velora execution

NOTES_FILE = os.path.expanduser("~/.velora_notes") # Encrypted notes file

def load_notes():
    if not os.path.exists(NOTES_FILE): return []
    with open(NOTES_FILE, "r") as f:
        return [_decrypt(line.strip()) for line in f.readlines() if line.strip()]

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        for n in notes: f.write(_encrypt(n) + "\n")

def main():
    args = sys.argv[1:]
    notes = load_notes()

    if not args or args[0] in ('list', 'ls'):
        print("\x1b[36;1m=== Velora Notes ===\x1b[0m")
        if not notes:
            print("  \x1b[90mNo notes found. Use 'notes add <text>' to create one.\x1b[0m")
        else:
            for i, n in enumerate(notes, 1):
                print(f"  \x1b[33m{i}.\x1b[0m {n}")
    elif args[0] in ('add', 'a') and len(args) > 1:
        note = " ".join(args[1:])
        notes.append(note)
        save_notes(notes)
        print(f"\x1b[32;1mNote saved:\x1b[0m {note}")
    elif args[0] in ('rm', 'remove', 'del') and len(args) > 1:
        try:
            idx = int(args[1]) - 1
            if 0 <= idx < len(notes):
                removed = notes.pop(idx)
                save_notes(notes)
                print(f"\x1b[31;1mDeleted:\x1b[0m {removed}")
            else:
                print(f"\x1b[31;1mError:\x1b[0m Note number out of range.")
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Please provide a valid note number.")
    elif args[0] in ('edit', 'e') and len(args) > 2:
        try:
            idx = int(args[1]) - 1
            if 0 <= idx < len(notes):
                new_note = " ".join(args[2:])
                notes[idx] = new_note
                save_notes(notes)
                print(f"\x1b[32;1mUpdated note {idx + 1}:\x1b[0m {new_note}")
            else:
                print(f"\x1b[31;1mError:\x1b[0m Note number out of range.")
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Please provide a valid note number.")
    elif args[0] == 'clear':
        save_notes([])
        print("\x1b[31;1mAll notes cleared.\x1b[0m")
    elif args[0] in ('search', 'find') and len(args) > 1:
        query = " ".join(args[1:]).lower()
        found = False
        for i, n in enumerate(notes, 1):
            if query in n.lower():
                if not found:
                    print("\x1b[36;1m=== Search Results ===\x1b[0m")
                    found = True
                print(f"  \x1b[33m{i}.\x1b[0m {n}")
        if not found:
            print("  \x1b[90mNo notes matching your query.\x1b[0m")
    else:
        print("\x1b[33mUsage:\x1b[0m notes [add <text> | edit <num> <text> | rm <num> | list | search <query> | clear]")

if __name__ == "__main__":
    main()