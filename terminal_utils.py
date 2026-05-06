__version__ = "1.0.0"
__description__ = "Centralized styling and UI utility for Velora Terminal."
__author__ = "Souvik"
__website__ = ""

import sys
import os
import shutil

# Premium Color Palette (Truecolor / RGB)
PURPLE = "\x1b[38;2;189;147;249m"
CYAN   = "\x1b[38;2;139;233;253m"
GREEN  = "\x1b[38;2;80;250;123m"
PINK   = "\x1b[38;2;255;121;198m"
ORANGE = "\x1b[38;2;255;184;108m"
RED    = "\x1b[38;2;255;85;85m"
YELLOW = "\x1b[38;2;241;250;140m"
GREY   = "\x1b[38;2;98;114;164m"
RESET  = "\x1b[0m"
BOLD   = "\x1b[1m"

def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns

def print_header(title, color=PURPLE):
    width = min(get_terminal_width(), 80)
    print(f"\n{color}{BOLD}┏" + "━" * (width - 2) + "┓")
    print(f"┃ {title.center(width - 4)} ┃")
    print(f"┗" + "━" * (width - 2) + f"┛{RESET}")

def print_section(title, color=CYAN):
    width = min(get_terminal_width(), 80)
    print(f"\n{color}{BOLD}─── {title} " + "─" * (width - len(title) - 5) + f"{RESET}")

def print_status(message, type="info"):
    if type == "success":
        print(f"  {GREEN}✅ {message}{RESET}")
    elif type == "error":
        print(f"  {RED}❌ {BOLD}Error:{RESET} {RED}{message}{RESET}")
    elif type == "warning":
        print(f"  {ORANGE}⚠️  {message}{RESET}")
    else:
        print(f"  {CYAN}ℹ️  {message}{RESET}")

def print_labeled(label, value, label_color=GREY, value_color=RESET):
    print(f"  {label_color}{label:<15}{RESET} {value_color}{value}{RESET}")

class Table:
    def __init__(self, headers, colors=None, width=None):
        self.headers = headers
        self.rows = []
        self.colors = colors or [CYAN] * len(headers)
        self.width = width or min(get_terminal_width(), 80)
        
    def add_row(self, row):
        self.rows.append(row)
        
    def print(self):
        # Calculate column widths
        col_widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val)))
        
        # Adjust last column to fit terminal width if needed
        total_fixed = sum(col_widths[:-1]) + (len(self.headers) * 3)
        col_widths[-1] = max(col_widths[-1], self.width - total_fixed - 2)

        # Print Headers
        header_str = "  "
        for i, h in enumerate(self.headers):
            header_str += f"{BOLD}{GREY}{h:<{col_widths[i]}}{RESET}   "
        print(header_str)
        print("  " + GREY + "─" * (sum(col_widths) + len(self.headers) * 3) + RESET)

        # Print Rows
        for row in self.rows:
            row_str = "  "
            for i, val in enumerate(row):
                color = self.colors[i] if i < len(self.colors) else RESET
                row_str += f"{color}{str(val):<{col_widths[i]}}{RESET}   "
            print(row_str)
        print()

def progress_bar(current, total, prefix="", suffix="", length=40):
    percent = float(current) * 100 / total
    filled_length = int(length * current // total)
    bar = "█" * filled_length + "░" * (length - filled_length)
    sys.stdout.write(f"\r  {prefix} {CYAN}[{GREEN}{bar}{CYAN}] {BOLD}{percent:>3.0f}%{RESET} {suffix}")
    sys.stdout.flush()
    if current == total:
        print()
