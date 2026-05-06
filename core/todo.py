__version__ = "1.4.2"
__description__ = "A built-in terminal task manager that saves tasks persistently to ~/.velora_todos."
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

TODO_FILE = os.path.expanduser("~/.velora_todos") # Encrypted todos file

def load_todos():
    if not os.path.exists(TODO_FILE): return []
    with open(TODO_FILE, "r") as f:
        return [_decrypt(line.strip()) for line in f.readlines() if line.strip()]

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        for t in todos: f.write(_encrypt(t) + "\n")

def main():
    args = sys.argv[1:]
    todos = load_todos()

    if not args or args[0] in ('list', 'ls'):
        print("\x1b[36;1m=== Velora To-Do List ===\x1b[0m")
        if not todos:
            print("  \x1b[90mNo pending tasks. You're all caught up!\x1b[0m")
        else:
            for i, t in enumerate(todos, 1):
                print(f"  \x1b[33m{i}.\x1b[0m {t}")
    elif args[0] in ('add', 'a') and len(args) > 1:
        task = " ".join(args[1:])
        todos.append(task)
        save_todos(todos)
        print(f"\x1b[32;1mAdded:\x1b[0m {task}")
    elif args[0] in ('done', 'd', 'rm', 'remove') and len(args) > 1:
        try:
            idx = int(args[1]) - 1
            if 0 <= idx < len(todos):
                removed = todos.pop(idx)
                save_todos(todos)
                print(f"\x1b[32;1mCompleted:\x1b[0m {removed}")
            else:
                print(f"\x1b[31;1mError:\x1b[0m Task number out of range.")
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Please provide a valid task number.")
    elif args[0] in ('edit', 'e') and len(args) > 2:
        try:
            idx = int(args[1]) - 1
            if 0 <= idx < len(todos):
                new_task = " ".join(args[2:])
                todos[idx] = new_task
                save_todos(todos)
                print(f"\x1b[32;1mUpdated task {idx + 1}:\x1b[0m {new_task}")
            else:
                print(f"\x1b[31;1mError:\x1b[0m Task number out of range.")
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Please provide a valid task number.")
    elif args[0] == 'clear':
        save_todos([])
        print("\x1b[31;1mAll tasks cleared.\x1b[0m")
    else:
        print("\x1b[33mUsage:\x1b[0m todo [add <task> | edit <num> <task> | done <num> | list | clear]")

if __name__ == "__main__":
    main()