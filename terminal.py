__version__ = "1.86.0"
__description__ = "Velora Terminal Core Application"
__author__ = "Souvik"
__website__ = "https://github.com/SouvikNandi1/Velora"

import sys
import os
import re
import signal
import glob
import runpy

# Explicitly import PTY modules so PyInstaller's static analyzer bundles them natively.
# This prevents new tabs from instantly crashing and closing in the compiled macOS/Linux executable.
if os.name != 'nt':
    import pty
    import select
    import fcntl
    import termios
    import struct

# Explicitly import standard libraries used by 'core' plugins so PyInstaller bundles them.
import math
import calendar
import datetime
import random
import hashlib
import uuid
import base64
import shutil
import platform
import string
import urllib.parse
import urllib.request
import json
import ssl
import vpm

# -- NATIVE COMPILED CORE EXECUTOR --
if len(sys.argv) > 2 and sys.argv[1] == '--run-core':
    core_name = sys.argv[2]
    sys.argv = [core_name] + sys.argv[3:]
    
    user_core = os.path.expanduser("~/.velora/core")
    target_path = os.path.join(user_core, f"{core_name}.py")
    if not os.path.exists(target_path):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        # Check root first for separated tools like vpm
        target_path = os.path.join(base_dir, f"{core_name}.py")
        if not os.path.exists(target_path):
            target_path = os.path.join(base_dir, 'core', f"{core_name}.py")
        
    if os.path.exists(target_path):
        import builtins
        
        def _velora_encrypt_data(text):
            key = b"velora_data_123"
            data = text.encode('utf-8')
            enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            return base64.b64encode(enc).decode('utf-8')

        def _velora_decrypt_data(b64_str):
            key = b"velora_data_123"
            try:
                enc = base64.b64decode(b64_str)
                dec = bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))
                return dec.decode('utf-8')
            except Exception:
                return b64_str
                
        builtins.encrypt_data = _velora_encrypt_data
        builtins.decrypt_data = _velora_decrypt_data
        
        import importlib.abc
        import importlib.machinery
        
        class VeloraImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
            def find_spec(self, fullname, path, target=None):
                search_paths = sys.path if path is None else path
                for p in search_paths:
                    if not p or not isinstance(p, str) or not os.path.isdir(p): continue
                    t_path = os.path.join(p, fullname.split('.')[-1] + ".py")
                    if os.path.exists(t_path):
                        try:
                            with open(t_path, 'r', encoding='utf-8') as f: header = f.read(100)
                            if "# Velora Encrypted Core Program" in header:
                                return importlib.machinery.ModuleSpec(fullname, self, origin=t_path)
                        except Exception: pass
                return None
            def create_module(self, spec): return None
            def exec_module(self, module):
                with open(module.__spec__.origin, 'r', encoding='utf-8') as f: code = f.read()
                m = re.search(r"__encrypted_payload__\s*=\s*['\"]([A-Za-z0-9+/=]+)['\"]", code)
                if m:
                    enc = base64.b64decode(m.group(1))
                    dec = bytes(b ^ b"velora_secure_123"[i % 17] for i, b in enumerate(enc)).decode('utf-8')
                    exec(dec, module.__dict__)
                else: raise ImportError(f"Corrupted encrypted payload in {module.__name__}")

        sys.meta_path.insert(0, VeloraImporter())
        
        def _velora_run_encrypted(file_path, run_name="__main__"):
            with open(file_path, 'r', encoding='utf-8') as f: code = f.read()
            if "# Velora Encrypted Core Program\n__encrypted_payload__" in code:
                m = re.search(r"__encrypted_payload__\s*=\s*['\"]([A-Za-z0-9+/=]+)['\"]", code)
                if m:
                    enc = base64.b64decode(m.group(1))
                    dec = bytes(b ^ b"velora_secure_123"[i % 17] for i, b in enumerate(enc)).decode('utf-8')
                    lib_dir = os.path.dirname(file_path)
                    if lib_dir not in sys.path: sys.path.insert(0, lib_dir)
                    exec(dec, {"__name__": run_name, "__file__": file_path, "sys": sys, "os": os})
                else: print(f"\x1b[31;1mError:\x1b[0m Corrupted encrypted payload in '{file_path}'.")
            else:
                runpy.run_path(file_path, run_name=run_name)
                
        builtins.run_encrypted = _velora_run_encrypted
        
        try:
            _velora_run_encrypted(target_path)
        except KeyboardInterrupt: pass
        except Exception as e: print(f"\x1b[31;1mExecution Error:\x1b[0m {e}")
    else:
        print(f"\x1b[31;1mError:\x1b[0m Core module '{core_name}' not found.")
    sys.exit(0)
elif len(sys.argv) > 2 and sys.argv[1] == '-c':
    exec(sys.argv[2])
    sys.exit(0)
# -----------------------------------

# Suppress benign Qt Wayland warnings on Linux
os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland*=false"

# Ignore background terminal signals to prevent the UI from freezing/suspending 
# when child shells attempt job control or TTY operations without a real PTY.
if hasattr(signal, 'SIGTTOU'):
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)
if hasattr(signal, 'SIGTTIN'):
    signal.signal(signal.SIGTTIN, signal.SIG_IGN)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPlainTextEdit, QLineEdit, QMenu, QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox, QLabel, QTabWidget, QToolButton, QInputDialog, QPushButton, QSlider, QHBoxLayout, QCompleter, QMessageBox, QSplitter, QTextEdit, QScrollArea, QFrame, QGridLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import QProcess, Qt, pyqtSignal, QSettings, QProcessEnvironment, QStringListModel, QUrl, QThread, QRegularExpression, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat, QFontDatabase, QKeySequence, QShortcut, QDesktopServices, QIcon, QTextDocument, QAction, QPainter, QLinearGradient
import urllib.request
import json
import ssl
import time

HISTORY_FILE = os.path.expanduser("~/.velora_history")

def encrypt_history_data(text):
    key = b"velora_history_123"
    data = text.encode('utf-8')
    enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.b64encode(enc).decode('utf-8')

def decrypt_history_data(b64_str):
    key = b"velora_history_123"
    try:
        enc = base64.b64decode(b64_str)
        dec = bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))
        return dec.decode('utf-8')
    except Exception:
        return b64_str

def get_rgba_from_hex(hex_color, opacity_percent):
    color = QColor(hex_color)
    alpha = int((opacity_percent / 100.0) * 255)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"

def _hex_to_rgb_str(hex_color):
    """Return 'r, g, b' string from a hex color — for use inside rgba() in Qt stylesheets."""
    c = QColor(hex_color)
    return f"{c.red()}, {c.green()}, {c.blue()}"


COLOR_MAP = {
    '30': '#44475a', '31': '#ff5555', '32': '#50fa7b', '33': '#f1fa8c',
    '34': '#bd93f9', '35': '#ff79c6', '36': '#8be9fd', '37': '#f8f8f2',
    '90': '#6272a4', '91': '#ff6e6e', '92': '#69ff94', '93': '#ffffa5',
    '94': '#d6acff', '95': '#ff92df', '96': '#a4ffff', '97': '#ffffff',
}

BG_COLOR_MAP = {
    '40': '#44475a', '41': '#ff5555', '42': '#50fa7b', '43': '#f1fa8c',
    '44': '#bd93f9', '45': '#ff79c6', '46': '#8be9fd', '47': '#f8f8f2',
    '100': '#6272a4', '101': '#ff6e6e', '102': '#69ff94', '103': '#ffffa5',
    '104': '#d6acff', '105': '#ff92df', '106': '#a4ffff', '107': '#ffffff',
}

THEMES = {
    "Dracula (Dark)": {"bg": "#282a36", "fg": "#f8f8f2", "sel": "#44475a", "border": "#6272a4"},
    "Solarized Light": {"bg": "#fdf6e3", "fg": "#657b83", "sel": "#eee8d5", "border": "#93a1a1"},
    "Hacker (Green)": {"bg": "#000000", "fg": "#00ff00", "sel": "#003300", "border": "#00ff00"},
    "Ayu Dark": {"bg": "#0a0e14", "fg": "#b3b1ad", "sel": "#273747", "border": "#3e4b59"},
    "Catppuccin Mocha": {"bg": "#1e1e2e", "fg": "#cdd6f4", "sel": "#45475a", "border": "#585b70"},
    "Cobalt2": {"bg": "#132738", "fg": "#ffffff", "sel": "#183c66", "border": "#1e5699"},
    "Cyberpunk": {"bg": "#000b1e", "fg": "#0abdc6", "sel": "#001a3a", "border": "#123e7c"},
    "Gruvbox Dark": {"bg": "#282828", "fg": "#ebdbb2", "sel": "#504945", "border": "#665c54"},
    "Material Dark": {"bg": "#263238", "fg": "#eeffff", "sel": "#314549", "border": "#546e7a"},
    "Monokai Pro": {"bg": "#2d2a2e", "fg": "#fcfcfa", "sel": "#403e41", "border": "#727072"},
    "Night Owl": {"bg": "#011627", "fg": "#d6deeb", "sel": "#1d3b53", "border": "#5f7e97"},
    "Nord": {"bg": "#2e3440", "fg": "#d8dee9", "sel": "#434c5e", "border": "#4c566a"},
    "One Dark": {"bg": "#282c34", "fg": "#abb2bf", "sel": "#3e4451", "border": "#5c6370"},
    "One Half Dark": {"bg": "#282c34", "fg": "#dcdfe4", "sel": "#313640", "border": "#5c6370"},
    "SynthWave '84": {"bg": "#262335", "fg": "#f0f0f0", "sel": "#433a59", "border": "#615582"},
    "Tokyo Night": {"bg": "#1a1b26", "fg": "#c0caf5", "sel": "#33467C", "border": "#565f89"},
    "Tomorrow Night": {"bg": "#1d1f21", "fg": "#c5c8c6", "sel": "#373b41", "border": "#969896"},
    "Ubuntu": {"bg": "#300a24", "fg": "#eeeeec", "sel": "#721f57", "border": "#802361"},
    "Zenburn": {"bg": "#3f3f3f", "fg": "#dcdccc", "sel": "#4f4f4f", "border": "#6f6f6f"}
}

class TerminalDisplay(QPlainTextEdit):
    command_entered = pyqtSignal(str)
    control_sequence = pyqtSignal(str)
    find_requested = pyqtSignal()
    zoom_changed = pyqtSignal(int)
    terminal_resized = pyqtSignal(int, int)
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_start_pos = 0
        self.history = self._load_history()
        self.in_raw_mode = False
        self.history_idx = len(self.history)
        self.setMouseTracking(True)
        
        self.completer = QCompleter(self._get_unique_history(), self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def _load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                # Read lines, strip newlines, filter out empty lines
                return [decrypt_history_data(line.strip()) for line in f.readlines() if line.strip()]
        except IOError:
            return []

    def clear_history(self):
        self.history = []
        self.history_idx = 0
        self.update_completer_model()

    def _get_unique_history(self):
        seen = set()
        unique_history = []
        for cmd in reversed(self.history):
            if cmd not in seen:
                seen.add(cmd)
                unique_history.append(cmd)
        return unique_history

    def update_completer_model(self):
        model = QStringListModel(self._get_unique_history(), self.completer)
        self.completer.setModel(model)

    def _save_command(self, command):
        try:
            with open(HISTORY_FILE, 'a') as f:
                f.write(encrypt_history_data(command) + '\n')
        except IOError:
            pass # Fail silently if history can't be saved
            
    def update_input_start(self):
        self.input_start_pos = self.document().characterCount() - 1

    def replace_input(self, text):
        cursor = self.textCursor()
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        self.setTextCursor(cursor)

    def resize_terminal(self):
        fm = self.fontMetrics()
        char_width = fm.horizontalAdvance('M')
        char_height = fm.height()
        if char_width > 0 and char_height > 0:
            self.setCursorWidth(char_width)
            cols = self.viewport().width() // char_width
            rows = self.viewport().height() // char_height
            self.terminal_resized.emit(rows, cols)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_terminal()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            return
        super().wheelEvent(event)

    def zoom_in(self):
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)
        self.zoom_changed.emit(font.pointSize())

    def zoom_out(self):
        font = self.font()
        font.setPointSize(max(1, font.pointSize() - 1))
        self.setFont(font)
        self.zoom_changed.emit(font.pointSize())

    def paste_to_input(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            if '\n' in text or '\r' in text:
                lines = len(text.splitlines())
                reply = QMessageBox.question(self, 'Confirm Paste', 
                                             f'You are about to paste {lines} lines. This may execute commands immediately.\n\nDo you want to continue?', 
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            cursor = self.textCursor()
            # Ensure we are pasting at the end of the input if cursor is in history
            if cursor.position() < self.input_start_pos:
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
            self.insertPlainText(text)

    def get_current_command(self):
        cursor = self.textCursor()
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        return cursor.selectedText()

    def get_url_at_pos(self, pos):
        cursor = self.cursorForPosition(pos)
        block = cursor.block()
        text = block.text()
        pos_in_block = cursor.positionInBlock()
        
        url_pattern = re.compile(r'https?://[^\s"\'<>\[\]{}]+')
        for match in url_pattern.finditer(text):
            if match.start() <= pos_in_block <= match.end():
                return match.group().rstrip('.,;:!?')
        return None

    def mouseMoveEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            url = self.get_url_at_pos(event.pos())
            if url:
                self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.button() == Qt.MouseButton.LeftButton:
            url = self.get_url_at_pos(event.pos())
            if url:
                QDesktopServices.openUrl(QUrl(url))
                return
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            if paths:
                safe_paths = [f"'{p}'" if ' ' in p else p for p in paths]
                text_to_insert = " ".join(safe_paths) + " "
                
                cursor = self.textCursor()
                if cursor.position() < self.input_start_pos:
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.setTextCursor(cursor)
                self.insertPlainText(text_to_insert)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def contextMenuEvent(self, event):
        settings = QSettings("Velora", "Settings")
        theme_name = settings.value("theme", "Dracula (Dark)")
        theme = THEMES.get(theme_name, THEMES["Dracula (Dark)"])

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 6px 4px;
            }}
            QMenu::item {{
                padding: 7px 28px 7px 16px;
                border-radius: 6px;
                margin: 2px 4px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {theme['sel']};
            }}
            QMenu::item:disabled {{
                color: {theme['border']};
                opacity: 0.5;
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme['border']};
                margin: 4px 10px;
                opacity: 0.4;
            }}
        """)
        copy_action = menu.addAction("Copy")
        copy_action.setEnabled(self.textCursor().hasSelection())
        paste_action = menu.addAction("Paste")
        paste_action.setEnabled(bool(QApplication.clipboard().text()))
        menu.addSeparator()
        clear_action = menu.addAction("Clear Terminal")
        menu.addSeparator()
        settings_action = menu.addAction("Settings...")

        action = menu.exec(event.globalPos())
        if action == copy_action:
            self.copy()
        elif action == paste_action:
            self.paste_to_input()
        elif action == clear_action:
            self.clear()
            self.update_input_start()
            self.control_sequence.emit("\x0c")
        elif action == settings_action:
            self.settings_requested.emit()

    def keyPressEvent(self, event):
        # Handle RAW MODE for fullscreen apps like 'nano' or 'vim'
        if self.in_raw_mode:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    if event.key() == Qt.Key.Key_V:
                        if not event.isAutoRepeat():
                            self.paste_to_input()
                        return
                    elif event.key() == Qt.Key.Key_C and self.textCursor().hasSelection():
                        self.copy()
                        return
                        
                if event.key() == Qt.Key.Key_C and self.textCursor().hasSelection():
                    self.copy()
                    return
                if Qt.Key.Key_A <= event.key() <= Qt.Key.Key_Z:
                    self.control_sequence.emit(chr(event.key() - Qt.Key.Key_A + 1))
                    return
                elif event.key() in (Qt.Key.Key_Space, Qt.Key.Key_At):
                    self.control_sequence.emit('\x00')
                    return
                elif event.key() == Qt.Key.Key_BracketLeft:
                    self.control_sequence.emit('\x1b')
                    return
                elif event.key() == Qt.Key.Key_Backslash:
                    self.control_sequence.emit('\x1c')
                    return
                elif event.key() == Qt.Key.Key_BracketRight:
                    self.control_sequence.emit('\x1d')
                    return
                elif event.key() in (Qt.Key.Key_AsciiCircum, Qt.Key.Key_6):
                    self.control_sequence.emit('\x1e')
                    return
                elif event.key() in (Qt.Key.Key_Underscore, Qt.Key.Key_Slash, Qt.Key.Key_Minus):
                    self.control_sequence.emit('\x1f')
                    return

            if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                if Qt.Key.Key_A <= event.key() <= Qt.Key.Key_Z:
                    self.control_sequence.emit('\x1b' + chr(event.key() - Qt.Key.Key_A + ord('a')))
                    return
            
            key = event.key()
            if key == Qt.Key.Key_Up: self.control_sequence.emit("\x1b[A")
            elif key == Qt.Key.Key_Down: self.control_sequence.emit("\x1b[B")
            elif key == Qt.Key.Key_Right: self.control_sequence.emit("\x1b[C")
            elif key == Qt.Key.Key_Left: self.control_sequence.emit("\x1b[D")
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.control_sequence.emit("\r")
            elif key == Qt.Key.Key_Backspace: self.control_sequence.emit("\x7f")
            elif key == Qt.Key.Key_Delete: self.control_sequence.emit("\x1b[3~")
            elif key == Qt.Key.Key_Tab: self.control_sequence.emit("\t")
            elif key == Qt.Key.Key_Escape: self.control_sequence.emit("\x1b")
            else:
                if event.text(): self.control_sequence.emit(event.text())
            return

        cursor = self.textCursor()
        
        # Accept inline completion with Tab or Right Arrow
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Right):
            if cursor.hasSelection() and cursor.selectionStart() >= self.input_start_pos:
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
                return
            elif event.key() == Qt.Key.Key_Tab:
                # File Path Autocomplete
                cmd = self.get_current_command()
                if cmd:
                    parts = cmd.split(' ')
                    last_part = parts[-1]
                    if last_part:
                        search_pattern = os.path.expanduser(last_part) + '*'
                        matches = glob.glob(search_pattern)
                        if len(matches) == 1:
                            match = matches[0]
                            if os.path.isdir(match):
                                match += '/'
                            if last_part.startswith('~'):
                                extra = match[len(os.path.expanduser(last_part)):]
                            else:
                                extra = match[len(search_pattern)-1:]
                            if extra:
                                cursor.movePosition(QTextCursor.MoveOperation.End)
                                cursor.insertText(extra)
                                self.setTextCursor(cursor)
                        elif len(matches) > 1:
                            common = os.path.commonprefix(matches)
                            extra = common[len(search_pattern)-1:]
                            if extra:
                                cursor.movePosition(QTextCursor.MoveOperation.End)
                                cursor.insertText(extra)
                                self.setTextCursor(cursor)
                return

        # Handle Control shortcuts (Ctrl+C, Ctrl+L, Zoom)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                if self.textCursor().hasSelection():
                    self.copy()
                else:
                    cursor = self.textCursor()
                    cursor.setPosition(self.input_start_pos)
                    cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                    unsubmitted_text = cursor.selectedText()
                    cursor.removeSelectedText()
                    if unsubmitted_text:
                        cursor.insertText(unsubmitted_text)
                        
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.setTextCursor(cursor)
                    self.update_input_start()
                    self.control_sequence.emit("\x03")
                return
            elif event.key() == Qt.Key.Key_V:
                if not event.isAutoRepeat():
                    self.paste_to_input()
                return
            elif event.key() == Qt.Key.Key_L:
                self.clear()
                self.update_input_start()
                self.control_sequence.emit("\x0c")
                return
            elif event.key() == Qt.Key.Key_D:
                # Only send EOF if input is empty, otherwise let it pass as a character
                if not self.get_current_command():
                    self.control_sequence.emit("\x04")
                    return
                self.control_sequence.emit("\x04")
                return
            elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                font = self.font()
                font.setPointSize(font.pointSize() + 1)
                self.setFont(font)
                self.zoom_changed.emit(font.pointSize())
                return
            elif event.key() == Qt.Key.Key_Minus:
                font = self.font()
                font.setPointSize(max(1, font.pointSize() - 1))
                self.setFont(font)
                self.zoom_changed.emit(font.pointSize())
                return
            elif event.key() == Qt.Key.Key_F:
                self.find_requested.emit()
                return
        
        # Prevent typing/deleting in the read-only area
        if cursor.hasSelection() and cursor.selectionStart() < self.input_start_pos:
            if event.text() or event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
                if not event.text():
                    return

        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Left):
            if cursor.position() <= self.input_start_pos:
                return

        elif event.key() == Qt.Key.Key_Home:
            # Jump to the beginning of the input area instead of top of terminal
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                cursor.setPosition(self.input_start_pos, QTextCursor.MoveMode.KeepAnchor)
            else:
                cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)
            return
        
        elif event.key() == Qt.Key.Key_Up:
            if self.history and self.history_idx > 0:
                self.history_idx -= 1
                self.replace_input(self.history[self.history_idx])
            return

        elif event.key() == Qt.Key.Key_Down:
            if self.history and self.history_idx < len(self.history):
                self.history_idx += 1
                if self.history_idx == len(self.history):
                    self.replace_input("")
                else:
                    self.replace_input(self.history[self.history_idx])
            return

        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Discard unaccepted inline autocomplete text before submitting
            if cursor.hasSelection() and cursor.selectionStart() >= self.input_start_pos:
                cursor.removeSelectedText()
            
            cursor.setPosition(self.input_start_pos)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            command = cursor.selectedText().strip()
            
            if command:
                if not self.history or self.history[-1] != command:
                    self.history.append(command)
                    self._save_command(command)
                    self.update_completer_model()
            self.history_idx = len(self.history)
            
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            self.insertPlainText('\n')
            self.update_input_start()
            
            self.command_entered.emit(command)
            return

        # Force cursor to end for normal typing if it's before input_start_pos
        if event.text() and cursor.position() < self.input_start_pos:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

        super().keyPressEvent(event)

        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            return

        is_shortcut = (event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier)) != Qt.KeyboardModifier.NoModifier
        if not is_shortcut and event.text():
            prefix = self.get_current_command()
            if len(prefix) < 1:
                return
            
            if prefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(prefix)
            
            completion = self.completer.currentCompletion()
            if completion and completion.lower().startswith(prefix.lower()) and len(completion) > len(prefix):
                extra = completion[len(prefix):]
                cursor = self.textCursor()
                if cursor.atEnd():
                    pos = cursor.position()
                    cursor.insertText(extra)
                    cursor.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
                    self.setTextCursor(cursor)

class VPMWorker(QThread):
    finished = pyqtSignal(dict, list)

    def run(self):
        cloud = vpm.get_cloud_packages()
        local = vpm.get_local_packages_info()
        self.finished.emit(cloud, local)

class VPMPackageCard(QFrame):
    action_triggered = pyqtSignal(str, str) # action, pkg_name

    def __init__(self, name, info, local_info, theme, parent=None):
        super().__init__(parent)
        self.name = name
        self.info = info
        self.theme = theme
        self.setObjectName("PackageCard")
        
        self.local_ver = next((p['version'] for p in local_info if p['name'] == name), None)
        self.cloud_ver = info.get('version', '1.0.0')
        self.is_official = "✅" in info.get('description', '')
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(8)
        
        # Header: Icon and Name
        header = QHBoxLayout()
        icon_lbl = QLabel("📦" if not self.is_official else "🛡️")
        icon_lbl.setStyleSheet("font-size: 24px;")
        header.addWidget(icon_lbl)
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {theme['fg']};")
        header.addWidget(name_lbl)
        header.addStretch()
        
        if self.is_official:
            badge = QLabel("OFFICIAL")
            badge.setStyleSheet(f"background-color: {theme['sel']}; color: {theme['fg']}; font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
            header.addWidget(badge)
            
        self.layout.addLayout(header)
        
        # Description
        desc = info.get('description', '').replace('✅', '').strip()
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: rgba({_hex_to_rgb_str(theme['fg'])}, 0.7); font-size: 12px;")
        self.layout.addWidget(desc_lbl)
        
        self.layout.addStretch()
        
        # Metadata
        meta = QHBoxLayout()
        author = info.get('author', 'Unknown')
        ver_str = f"v{self.cloud_ver}"
        if self.local_ver:
            if self.local_ver != self.cloud_ver:
                ver_str = f"v{self.local_ver} ➜ \x1b[32mv{self.cloud_ver}\x1b[0m" # Note: ANSI won't work in QLabel, use HTML
                ver_str = f"<span style='color: gray;'>v{self.local_ver}</span> <span style='color: {theme['border']};'>➜</span> <span style='color: #50fa7b;'>v{self.cloud_ver}</span>"
            else:
                ver_str = f"<span style='color: #50fa7b;'>v{self.local_ver} (Latest)</span>"
        
        meta_lbl = QLabel(f"By {author}  •  {ver_str}")
        meta_lbl.setStyleSheet(f"font-size: 10px; color: rgba({_hex_to_rgb_str(theme['fg'])}, 0.5);")
        meta.addWidget(meta_lbl)
        self.layout.addLayout(meta)
        
        # Buttons
        btn_box = QHBoxLayout()
        if not self.local_ver:
            self.main_btn = QPushButton("Install")
            self.main_btn.setObjectName("InstallBtn")
        elif self.local_ver != self.cloud_ver:
            self.main_btn = QPushButton("Update")
            self.main_btn.setObjectName("UpdateBtn")
        else:
            self.main_btn = QPushButton("Remove")
            self.main_btn.setObjectName("RemoveBtn")
            
        self.main_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_btn.clicked.connect(self.on_btn_clicked)
        btn_box.addWidget(self.main_btn)
        
        self.info_btn = QPushButton("ℹ")
        self.info_btn.setFixedWidth(30)
        self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_btn.clicked.connect(lambda: self.action_triggered.emit("info", self.name))
        btn_box.addWidget(self.info_btn)
        
        self.layout.addLayout(btn_box)
        
        self.apply_styles()

    def apply_styles(self):
        bg = f"rgba({_hex_to_rgb_str(self.theme['bg'])}, 0.4)"
        border = f"rgba({_hex_to_rgb_str(self.theme['border'])}, 0.3)"
        sel = self.theme['sel']
        fg = self.theme['fg']
        
        self.setStyleSheet(f"""
            #PackageCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            #PackageCard:hover {{
                border: 1px solid {self.theme['border']};
                background-color: rgba({_hex_to_rgb_str(self.theme['bg'])}, 0.6);
            }}
            QPushButton {{
                background-color: {sel};
                color: {fg};
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {fg};
                color: {self.theme['bg']};
            }}
            #RemoveBtn {{
                background-color: rgba(255, 85, 85, 0.2);
                color: #ff5555;
                border: 1px solid rgba(255, 85, 85, 0.4);
            }}
            #RemoveBtn:hover {{
                background-color: #ff5555;
                color: white;
            }}
        """)

    def on_btn_clicked(self):
        action = self.main_btn.text().lower()
        self.action_triggered.emit(action, self.name)

class VPMTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.parent_app = parent
        self.theme = THEMES.get(settings.value("theme", "Dracula (Dark)"), THEMES["Dracula (Dark)"])
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        title = QLabel("Package Manager")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.theme['fg']};")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search packages...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.textChanged.connect(self.filter_packages)
        toolbar.addWidget(self.search_bar)
        
        self.refresh_btn = QPushButton("Refresh Registry")
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(self.refresh_btn)
        
        self.layout.addLayout(toolbar)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(15)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)
        
        self.cards = []
        self.refresh_data()

    def refresh_data(self):
        # Clear existing
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
        self.cards = []
        
        loading = QLabel("Fetching latest packages from SNCloud...")
        loading.setStyleSheet(f"color: {self.theme['border']}; font-style: italic;")
        self.grid.addWidget(loading, 0, 0)
        
        self.worker = VPMWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.start()

    def on_data_loaded(self, cloud_data, local_data):
        # Clear loading
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
            
        if not cloud_data:
            err = QLabel("Failed to connect to SNCloud. Please check your internet connection.")
            err.setStyleSheet("color: #ff5555;")
            self.grid.addWidget(err, 0, 0)
            return

        # Sort: Official first, then name
        sorted_pkgs = sorted(cloud_data.items(), key=lambda x: ("✅" not in x[1].get('description', ''), x[0]))
        
        row, col = 0, 0
        cols_count = max(1, self.width() // 320)
        
        for name, info in sorted_pkgs:
            card = VPMPackageCard(name, info, local_data, self.theme)
            card.action_triggered.connect(self.handle_action)
            self.cards.append(card)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols_count:
                col = 0
                row += 1

    def filter_packages(self, text):
        text = text.lower()
        # Hide all
        for card in self.cards:
            card.hide()
            self.grid.removeWidget(card)
            
        # Filter and re-add
        filtered = [c for c in self.cards if text in c.name.lower() or text in c.info.get('description', '').lower()]
        
        row, col = 0, 0
        cols_count = max(1, self.width() // 320)
        for card in filtered:
            card.show()
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols_count:
                col = 0
                row += 1

    def handle_action(self, action, pkg_name):
        if action == "info":
            # Just run the CLI command in a hidden way or show a dialog
            # For now, let's just print to the active terminal if possible, 
            # but better to show a dialog.
            vpm.locate_package(pkg_name) # This prints, not ideal
            return

        # For install/update/remove, we'll run the command in the background
        # and refresh when done.
        confirm = QMessageBox.question(self, "Confirm Action", f"Are you sure you want to {action} '{pkg_name}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if action == "install" or action == "update":
                    vpm.install_package(pkg_name)
                elif action == "remove":
                    # Manually handle removal as vpm.py remove expects CLI args
                    target = os.path.join(vpm.USER_CORE_DIR, f"{pkg_name}.py")
                    lib_target = os.path.join(vpm.USER_CORE_DIR, f"{pkg_name}_lib")
                    if os.path.exists(target): os.remove(target)
                    if os.path.exists(lib_target): shutil.rmtree(lib_target)
                    vpm.remove_wrapper(pkg_name)
                
                QMessageBox.information(self, "Success", f"Successfully {action}ed '{pkg_name}'!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to {action} '{pkg_name}': {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.cards:
            self.filter_packages(self.search_bar.text())

class SettingsTab(QWidget):

    settings_applied = pyqtSignal()
    history_cleared = pyqtSignal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.settings = settings
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(30, 30, 30, 30)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(QFontDatabase.families())
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_label = QLabel()
        self.opacity_slider.valueChanged.connect(lambda value: self.opacity_label.setText(f" {value}%"))
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        self.form_layout.addRow(QLabel("Theme:"), self.theme_combo)
        self.form_layout.addRow(QLabel("Font Family:"), self.font_combo)
        self.form_layout.addRow(QLabel("Font Size:"), self.size_spin)
        self.form_layout.addRow(QLabel("Background Opacity:"), opacity_layout)
        
        self.save_btn = QPushButton("Save & Apply Settings")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.clear_history_btn = QPushButton("Clear Command History")
        self.clear_history_btn.clicked.connect(self.prompt_clear_history)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.clear_history_btn)
        self.layout.addLayout(btn_layout)
        
        default_font = "Menlo" if sys.platform == "darwin" else "Consolas" if os.name == 'nt' else "Monospace"
        self.font_combo.setCurrentText(self.settings.value("font_family", default_font))
        self.size_spin.setValue(int(self.settings.value("font_size", 11)))
        self.theme_combo.setCurrentText(self.settings.value("theme", "Dracula (Dark)"))
        
        opacity = int(self.settings.value("opacity", 85))
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f" {opacity}%")
        
        self.apply_theme()

    def apply_theme(self):
        theme_name = self.settings.value("theme", "Dracula (Dark)")
        theme = THEMES.get(theme_name, THEMES["Dracula (Dark)"])

        self.setStyleSheet(f"""
            SettingsTab {{ background-color: transparent; color: {theme['fg']}; }}
            QLabel {{
                color: {theme['fg']};
                font-size: 13px;
                font-weight: 600;
                margin-top: 10px;
                opacity: 0.85;
            }}
            QComboBox, QSpinBox {{
                background-color: rgba(0, 0, 0, 0.25);
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 9px 14px;
                font-size: 13px;
                margin-top: 4px;
                min-width: 180px;
            }}
            QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {theme['fg']};
                background-color: rgba(0, 0, 0, 0.4);
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                selection-background-color: {theme['sel']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QSlider::groove:horizontal {{
                background: rgba(255,255,255,0.1);
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {theme['fg']};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {theme['border']};
                border-radius: 2px;
            }}
            QPushButton {{
                background-color: {theme['sel']};
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                margin-top: 20px;
            }}
            QPushButton:hover {{
                background-color: {theme['border']};
                border: 1px solid {theme['fg']};
            }}
            QPushButton:pressed {{
                background-color: rgba(0,0,0,0.3);
            }}
        """)

    def apply_font(self):
        pass

    def save_settings(self):
        self.settings.setValue("font_family", self.font_combo.currentText())
        self.settings.setValue("font_size", self.size_spin.value())
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("opacity", self.opacity_slider.value())
        self.apply_theme()
        self.settings_applied.emit()

    def prompt_clear_history(self):
        reply = QMessageBox.question(self, 'Clear History', 
                                     'Are you sure you want to clear all command history? This cannot be undone.', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                open(HISTORY_FILE, 'w').close()
            except IOError:
                pass
            self.history_cleared.emit()

class TerminalSession(QWidget):
    zoom_changed = pyqtSignal(int)
    settings_requested = pyqtSignal()
    session_closed = pyqtSignal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.settings = settings
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.output_area = TerminalDisplay()
        self.apply_font()
        self.output_area.command_entered.connect(self.run_command)
        self.output_area.control_sequence.connect(self.run_control_sequence)
        self.output_area.settings_requested.connect(self.settings_requested.emit)
        self.output_area.zoom_changed.connect(self.zoom_changed.emit)
        self.output_area.terminal_resized.connect(self.on_terminal_resize)
        self.layout.addWidget(self.output_area)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search terminal... (Enter: next, Shift+Enter: previous, Ctrl+F: toggle)")
        self.search_bar.hide()
        self.search_bar.returnPressed.connect(self.perform_search)
        self.layout.insertWidget(0, self.search_bar)

        # Search options
        self.search_case_sensitive = False
        self.search_regex = False
        self.search_backwards = False
        
        # Search bar context menu
        self.search_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.search_bar.customContextMenuRequested.connect(self.show_search_context_menu)

        self.output_area.find_requested.connect(self.toggle_search)

        self.current_format = QTextCharFormat()
        self.last_command = ""
        self.expecting_echo = False

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.on_process_finished)

        env = QProcessEnvironment.systemEnvironment()
        env.insert("TERM", "xterm-256color")
        env.insert("COLORTERM", "truecolor")
        env.insert("VELORA_PYTHON", sys.executable)
        env.insert("VELORA_CORE", os.path.expanduser("~/.velora/core"))
        env.insert("VELORA_VERSION", __version__)
        env.insert("VELORA_TERMINAL_PATH", os.path.abspath(sys.argv[0]))
        
        # Inject native wrappers into PATH
        velora_bin = os.path.expanduser("~/.velora/bin")
        current_path = env.value("PATH", "")
        sep = ';' if os.name == 'nt' else ':'
        if velora_bin not in current_path.split(sep):
            env.insert("PATH", f"{velora_bin}{sep}{current_path}")
            
        self.process.setProcessEnvironment(env)
        
        if os.name == 'nt':
            self.process.start("cmd.exe")
        else:
            shell = os.environ.get("SHELL", "zsh" if sys.platform == "darwin" else "bash")
            shell_name = os.path.basename(shell)
            # Custom PTY Proxy Engine to natively intercept window resizing events
            pty_cmd = (
                "import pty, os, sys, select, fcntl, termios, struct, re\n"
                "pid, fd = pty.fork()\n"
                "if pid == 0:\n"
                f"    os.execvp('{shell}', ['{shell_name}', '-i'])\n"
                "while True:\n"
                "    r, _, _ = select.select([0, fd], [], [])\n"
                "    if 0 in r:\n"
                "        d = os.read(0, 4096)\n"
                "        if not d: break\n"
                "        m = re.search(b'\\\\x1b\\\\]999;(\\\\d+);(\\\\d+)\\\\x07', d)\n"
                "        if m:\n"
                "            try: fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', int(m.group(1)), int(m.group(2)), 0, 0))\n"
                "            except: pass\n"
                "            d = re.sub(b'\\\\x1b\\\\]999;\\\\d+;\\\\d+\\\\x07', b'', d)\n"
                "        if d: os.write(fd, d)\n"
                "    if fd in r:\n"
                "        try: d = os.read(fd, 4096)\n"
                "        except OSError: break\n"
                "        if not d: break\n"
                "        os.write(1, d)\n"
            )
            self.process.start(sys.executable, ["-c", pty_cmd])
            
        self.apply_theme()
        
        ascii_logo = (
            "\x1b[36;1m"
            " ██╗   ██╗███████╗██╗      ██████╗ ██████╗  █████╗ \r\n"
            " ██║   ██║██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗\r\n"
            " ██║   ██║█████╗  ██║     ██║   ██║██████╔╝███████║\r\n"
            " ╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║\r\n"
            "  ╚████╔╝ ███████╗███████╗╚██████╔╝██║  ██║██║  ██║\r\n"
            "   ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝\r\n"
            "                                                   \r\n"
            "      \x1b[35;1mE L E V A T E  Y O U R  W O R K F L O W\x1b[0m      \r\n"
            f"          \x1b[90mVelora Terminal Core v{__version__}\x1b[0m\r\n\r\n"
        )
        self.insert_ansi_text(ascii_logo)
        
        # Show startup information
        self.show_startup_info()

    def show_startup_info(self):
        """Display startup information only if updates are available"""
        info_msg = ""
        updates_found = False
        
        # Determine system-specific bootstrap command
        system = platform.system()
        if system == "Windows":
            bootstrap_cmd = 'powershell.exe -Command "cd $env:USERPROFILE; Invoke-WebRequest -Uri https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py -OutFile bootstrap.py; python bootstrap.py"'
        else:
            bootstrap_cmd = "curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3"
        
        # Check for bootstrap/terminal updates
        try:
            import vpm
            project_id, api_key = vpm.get_remote_credentials()
            if project_id and api_key:
                import ssl
                import urllib.request
                import json
                import time
                
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(f"https://sncloud.in/api/db/{project_id}/app/terminal.json?_t={int(time.time())}", 
                                           headers={'User-Agent': 'Velora/1.0', 'X-API-Key': api_key, 'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, context=ctx, timeout=3) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data and isinstance(data, dict):
                        cloud_app_ver = data.get('version', '1.0.0').strip()
                        if self.is_newer_version(cloud_app_ver, __version__):
                            updates_found = True
                            info_msg += "\x1b[36;1m═══ Bootstrap Update Available ═══\x1b[0m\r\n"
                            info_msg += f"\x1b[32;1m{bootstrap_cmd}\x1b[0m\r\n"
                            info_msg += "\x1b[90mRun this command to update Velora from the latest repository\x1b[0m\r\n\r\n"
        except:
            pass  # Silently fail if update check fails
        
        # Check for package updates
        pkg_updates = []
        try:
            import vpm
            project_id, api_key = vpm.get_remote_credentials()
            if project_id and api_key:
                import ssl
                import urllib.request
                import json
                import time
                
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(f"https://sncloud.in/api/db/{project_id}/packages.json?_t={int(time.time())}", 
                                           headers={'User-Agent': 'Velora/1.0', 'X-API-Key': api_key, 'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, context=ctx, timeout=3) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if isinstance(data, dict):
                        core_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
                        user_core_dir = os.path.expanduser("~/.velora/core")
                        
                        for pkg, info in data.items():
                            if isinstance(info, dict):
                                cloud_ver = info.get('version', '1.0.0').strip()
                                local_user = os.path.join(user_core_dir, f"{pkg}.py")
                                local_bundled = os.path.join(core_dir, f"{pkg}.py")
                                local_path = local_user if os.path.exists(local_user) else local_bundled
                                
                                if os.path.exists(local_path):
                                    try:
                                        with open(local_path, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                        m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                                        local_ver = m.group(1).strip() if m else "1.0.0"
                                        if self.is_newer_version(cloud_ver, local_ver):
                                            pkg_updates.append(pkg)
                                    except:
                                        pass
                        
                        if pkg_updates:
                            updates_found = True
                            info_msg += "\x1b[36;1m═══ Package Updates Available ═══\x1b[0m\r\n"
                            for pkg in pkg_updates:
                                info_msg += f"\x1b[32m• {pkg}\x1b[0m\r\n"
                            info_msg += "\r\n\x1b[36mRun \x1b[32;1mvpm update-all\x1b[36m to update all packages\x1b[0m\r\n\r\n"
        except:
            pass  # Silently fail if package check fails
        
        # Only show update commands if updates were found
        if updates_found:
            info_msg += "\x1b[36;1m═══ Update Commands ═══\x1b[0m\r\n"
            info_msg += "\x1b[32;1mvpm upgrade\x1b[0m         - Update the terminal application\r\n"
            info_msg += "\x1b[32;1mvpm update-all\x1b[0m     - Update all installed packages\r\n"
            info_msg += "\x1b[32;1mvpm list\x1b[0m            - Browse available packages\r\n"
            info_msg += "\x1b[32;1mvpm info <package>\x1b[0m  - Get package details\r\n"
            
            self.insert_ansi_text(info_msg)
    
    def is_newer_version(self, cloud_ver, local_ver):
        """Check if cloud version is newer than local version"""
        try:
            c_parts = [int(x) for x in cloud_ver.split('.')]
            l_parts = [int(x) for x in local_ver.split('.')]
            return c_parts > l_parts
        except:
            return cloud_ver != local_ver

    def on_terminal_resize(self, rows, cols):
        if self.process.state() == QProcess.ProcessState.Running and os.name != 'nt':
            resize_seq = f"\x1b]999;{rows};{cols}\x07"
            self.process.write(resize_seq.encode())

    def on_process_finished(self, exit_code, exit_status):
        self.session_closed.emit()

    def clear_history(self):
        self.output_area.clear_history()

    def apply_font(self):
        default_font = "Menlo" if sys.platform == "darwin" else "Consolas" if os.name == 'nt' else "Monospace"
        font_family = self.settings.value("font_family", default_font)
        font_size = int(self.settings.value("font_size", 11))
        font = QFont(font_family, font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output_area.setFont(font)
        self.output_area.resize_terminal()

    def apply_theme(self):
        theme_name = self.settings.value("theme", "Dracula (Dark)")
        theme = THEMES.get(theme_name, THEMES["Dracula (Dark)"])
        self.current_theme = theme

        border_rgba = get_rgba_from_hex(theme['border'], 50)
        self.setStyleSheet(f"""
            TerminalSession {{ background-color: transparent; color: {theme['fg']}; }}
            QPlainTextEdit {{
                background-color: transparent;
                color: {theme['fg']};
                border: none;
                selection-background-color: {theme['sel']};
                padding: 10px 14px;
                line-height: 1.4;
            }}
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.45);
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 20px;
                padding: 7px 18px;
                margin: 6px 10px;
                font-size: 13px;
                selection-background-color: {theme['sel']};
            }}
            QLineEdit:focus {{
                border: 1px solid {theme['fg']};
                background-color: rgba(0, 0, 0, 0.6);
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border_rgba};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['border']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                border: none; background: none; height: 0px;
            }}
        """)

    def run_command(self, command):
        self.last_command = command
        self.expecting_echo = True
        
        # Mirror directory changes locally for accurate path autocomplete
        cmd_strip = command.strip()
        if cmd_strip == "cd":
            try: os.chdir(os.path.expanduser("~"))
            except Exception: pass
        elif cmd_strip.startswith("cd "):
            target_dir = os.path.expanduser(cmd_strip[3:].strip())
            try: os.chdir(target_dir)
            except Exception: pass

        # Suggest installation for missing core-style commands
        parts = cmd_strip.split()
        if parts:
            cmd_name = parts[0]
            velora_bin = os.path.expanduser("~/.velora/bin")
            # If command is not in path and not a shell builtin
            if not shutil.which(cmd_name) and not shutil.which(cmd_name, path=velora_bin) and cmd_name not in ('cd', 'exit', 'ls', 'vpm'):
                cache_path = os.path.expanduser("~/.velora/vpm_cache.json")
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r') as f:
                            cache = json.load(f)
                        if cmd_name in cache:
                            self.insert_ansi_text(f"\n\x1b[33;1m⚠️  Command '{cmd_name}' is not installed.\x1b[0m\r\n")
                            self.insert_ansi_text(f"\x1b[36mIt is available in the Velora Cloud Registry.\x1b[0m\r\n")
                            self.insert_ansi_text(f"\x1b[36mRun: \x1b[32;1mvpm install {cmd_name}\x1b[36m to install it.\x1b[0m\r\n\n")
                    except: pass

        # High-Power Interceptor: Modern VPM Listing
        if cmd_strip == "vpm list":
            self.render_vpm_list()
            self.run_control_sequence("\r")
            return

        # Power-Up: Detailed Package Info Interceptor
        if cmd_strip.startswith("vpm info "):
            pkg_name = cmd_strip[9:].strip()
            self.render_vpm_info(pkg_name)
            self.run_control_sequence("\r")
            return

        # Power-Up: Handle vpm upgrade for compiled binaries
        if cmd_strip == "vpm upgrade" and getattr(sys, 'frozen', False):
            self.insert_ansi_text("\n\x1b[33;1m⚠️  Direct OTA source upgrades are disabled for compiled binaries.\x1b[0m\r\n")
            self.insert_ansi_text("\x1b[36mTo update this standalone executable:\x1b[0m\r\n")
            self.insert_ansi_text(f"\x1b[36m1. Run \x1b[32;1mvpm build\x1b[36m if you have the source code.\x1b[0m\r\n")
            self.insert_ansi_text(f"\x1b[36m2. Download the latest release from: \x1b[32;1m{__website__}/releases\x1b[0m\r\n\n")
            
            # Trigger the standard prompt so the user isn't stuck
            self.run_control_sequence("\r")
            return

        self.process.write((command + "\n").encode())

    def run_control_sequence(self, seq):
        self.process.write(seq.encode())

    def sync_registry(self):
        try:
            self.insert_ansi_text("\r\n\x1b[33;1m⏳ Synchronizing Velora Cloud Registry...\x1b[0m\r\n")
            QApplication.processEvents()
            
            import ssl, urllib.request, json, time
            project_id, api_key = vpm.get_remote_credentials()
            ctx = ssl._create_unverified_context()
            
            req = urllib.request.Request(f"https://sncloud.in/api/db/{project_id}/packages.json?_t={int(time.time())}", headers={'User-Agent': 'Velora/1.0', 'X-API-Key': api_key, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if isinstance(data, dict):
                    cache_path = os.path.expanduser("~/.velora/vpm_cache.json")
                    with open(cache_path, 'w') as f: json.dump(data, f)
            return True
        except Exception as e:
            self.insert_ansi_text(f"\x1b[31;1mError:\x1b[0m Could not sync registry: {e}\r\n")
            return False

    def render_vpm_list(self):
        cache_path = os.path.expanduser("~/.velora/vpm_cache.json")
        if not os.path.exists(cache_path):
            if not self.sync_registry():
                return

        try:
            with open(cache_path, 'r') as f:
                cloud_data = json.load(f)
        except:
            self.insert_ansi_text("\r\n\x1b[31;1mError:\x1b[0m Could not parse the package registry cache.\r\n")
            return

        user_core_dir = os.path.expanduser("~/.velora/core")
        official = []
        community = []

        for pkg, info in cloud_data.items():
            if not isinstance(info, dict): continue
            if "✅" in info.get('description', ''):
                official.append((pkg, info))
            else:
                community.append((pkg, info))

        official.sort()
        community.sort()

        self.insert_ansi_text("\r\n\x1b[38;5;51m\x1b[1m⚡ VELORA CLOUD REGISTRY \x1b[0m\x1b[90m(Package Manager)\x1b[0m\r\n\n")

        def render_section(title, items, pkg_color, icon=""):
            self.insert_ansi_text(f" \x1b[1m{icon} {title}\x1b[0m\r\n")
            self.insert_ansi_text(f" \x1b[90m" + "─" * 75 + "\x1b[0m\r\n")
            for pkg, info in items:
                version = info.get('version', '1.0.0')
                author = info.get('author', 'Unknown')
                desc = info.get('description', '').replace('✅', '').strip()
                desc = (desc[:60] + '..') if len(desc) > 60 else desc
                is_installed = os.path.exists(os.path.join(user_core_dir, f"{pkg}.py"))
                
                status_badge = "\x1b[42;30m INSTALLED \x1b[0m" if is_installed else "\x1b[100;37m AVAILABLE \x1b[0m"
                
                self.insert_ansi_text(f" {pkg_color}◆ {pkg:<15}\x1b[0m \x1b[90mv{version:<8}\x1b[0m {status_badge} \x1b[90mby\x1b[0m \x1b[33m{author[:18]:<18}\x1b[0m\r\n")
                self.insert_ansi_text(f"   \x1b[97m{desc}\x1b[0m\r\n\n")

        if official:
            render_section("Verified Official Suite", official, "\x1b[36;1m", "🛡️")
        
        if community:
            render_section("Community Registry", community, "\x1b[32;1m", "🌍")

        self.insert_ansi_text(f"\x1b[90m Total: {len(cloud_data)} packages  │  Use 'vpm info <pkg>' for details\x1b[0m\r\n")

    def render_vpm_info(self, pkg_name):
        cache_path = os.path.expanduser("~/.velora/vpm_cache.json")
        if not os.path.exists(cache_path):
            if not self.sync_registry():
                return

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
        except: return

        if pkg_name not in data:
            self.insert_ansi_text(f"\r\n\x1b[31;1mError:\x1b[0m Package '{pkg_name}' not found in registry.\r\n")
            return

        info = data[pkg_name]
        self.insert_ansi_text(f"\r\n\x1b[38;5;51m\x1b[1m📦 {pkg_name.upper()} \x1b[0m\x1b[90mv{info.get('version', '1.0.0')}\x1b[0m\r\n")
        self.insert_ansi_text(f" \x1b[90m" + "═" * 60 + "\x1b[0m\r\n")
        
        self.insert_ansi_text(f" \x1b[36mAuthor:\x1b[0m      \x1b[97m{info.get('author', 'Anonymous')}\x1b[0m\r\n")
        
        if info.get('website'):
            self.insert_ansi_text(f" \x1b[36mWebsite:\x1b[0m     \x1b[34;4m{info.get('website')}\x1b[0m\r\n")
            
        desc = info.get('description', 'No description provided.').replace('✅', '').strip()
        self.insert_ansi_text(f" \x1b[36mDescription:\x1b[0m \x1b[97m{desc}\x1b[0m\r\n")
        
        self.insert_ansi_text(f" \x1b[90m" + "─" * 60 + "\x1b[0m\r\n")
        is_installed = os.path.exists(os.path.join(os.path.expanduser("~/.velora/core"), f"{pkg_name}.py"))
        if is_installed:
            self.insert_ansi_text(f" \x1b[42;30m\x1b[1m INSTALLED \x1b[0m  \x1b[32mReady to use\x1b[0m\r\n\n")
        else:
            self.insert_ansi_text(f" \x1b[100;37m AVAILABLE \x1b[0m  \x1b[90mInstall with: \x1b[33mvpm install {pkg_name}\x1b[0m\r\n\n")

    def toggle_search(self):
        if self.search_bar.isVisible():
            self.search_bar.hide()
            self.output_area.setExtraSelections([])  # Clear highlights
            self.output_area.setFocus()
        else:
            self.search_bar.show()
            self.search_bar.setFocus()
            self.search_bar.selectAll()

    def perform_search(self):
        query = self.search_bar.text()
        if not query:
            return
            
        # Check for modifier keys
        modifiers = QApplication.keyboardModifiers()
        self.search_backwards = modifiers & Qt.KeyboardModifier.ShiftModifier
        
        if self.search_regex:
            found = self.perform_regex_search(query)
        else:
            found = self.perform_text_search(query)
            
        if found:
            # Highlight the found text
            self.highlight_search_results(query)
        else:
            # Flash the search bar to indicate no results
            self.search_bar.setStyleSheet("QLineEdit { background-color: rgba(255, 100, 100, 0.3); }")
            QTimer.singleShot(200, lambda: self.search_bar.setStyleSheet(""))

    def perform_text_search(self, query):
        """Perform regular text search"""
        flags = QTextDocument.FindFlags()
        if self.search_case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.search_backwards:
            flags |= QTextDocument.FindFlag.FindBackward
            
        found = self.output_area.find(query, flags)
        if not found:
            # Wrap around
            cursor = self.output_area.textCursor()
            if self.search_backwards:
                cursor.movePosition(QTextCursor.MoveOperation.End)
            else:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.output_area.setTextCursor(cursor)
            found = self.output_area.find(query, flags)
        return found

    def perform_regex_search(self, query):
        """Perform regex search"""
        try:
            pattern = QRegularExpression(query)
            if not self.search_case_sensitive:
                pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
                
            cursor = self.output_area.textCursor()
            if self.search_backwards:
                found = self.output_area.find(pattern, cursor, QTextDocument.FindFlag.FindBackward)
                if not found:
                    # Wrap to end
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.output_area.setTextCursor(cursor)
                    found = self.output_area.find(pattern, cursor, QTextDocument.FindFlag.FindBackward)
            else:
                found = self.output_area.find(pattern, cursor)
                if not found:
                    # Wrap to start
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    self.output_area.setTextCursor(cursor)
                    found = self.output_area.find(pattern, cursor)
            return found
        except:
            return False

    def highlight_search_results(self, query):
        """Highlight all occurrences of the search query"""
        if not query:
            return
            
        # Clear previous highlights
        self.output_area.setExtraSelections([])
        
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.output_area.setTextCursor(cursor)
        
        selections = []
        
        if self.search_regex:
            try:
                pattern = QRegularExpression(query)
                if not self.search_case_sensitive:
                    pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
                    
                while self.output_area.find(pattern):
                    selection = QTextEdit.ExtraSelection()
                    selection.cursor = self.output_area.textCursor()
                    selection.format.setBackground(QColor(255, 255, 0, 100))  # Light yellow highlight
                    selections.append(selection)
            except:
                pass  # Invalid regex, don't highlight
        else:
            flags = QTextDocument.FindFlags()
            if self.search_case_sensitive:
                flags |= QTextDocument.FindFlag.FindCaseSensitively
                
            while self.output_area.find(query, flags):
                selection = QTextEdit.ExtraSelection()
                selection.cursor = self.output_area.textCursor()
                selection.format.setBackground(QColor(255, 255, 0, 100))  # Light yellow highlight
                selections.append(selection)
            
        self.output_area.setExtraSelections(selections)

    def show_search_context_menu(self, position):
        """Show context menu for search options"""
        menu = QMenu(self.search_bar)
        
        case_action = QAction("Case Sensitive", self.search_bar)
        case_action.setCheckable(True)
        case_action.setChecked(self.search_case_sensitive)
        case_action.triggered.connect(lambda: self.set_search_option('case_sensitive', case_action.isChecked()))
        menu.addAction(case_action)
        
        regex_action = QAction("Regex Search", self.search_bar)
        regex_action.setCheckable(True)
        regex_action.setChecked(self.search_regex)
        regex_action.triggered.connect(lambda: self.set_search_option('regex', regex_action.isChecked()))
        menu.addAction(regex_action)
        
        menu.exec(self.search_bar.mapToGlobal(position))

    def set_search_option(self, option, value):
        """Set search option and update search if needed"""
        if option == 'case_sensitive':
            self.search_case_sensitive = value
        elif option == 'regex':
            self.search_regex = value
            
        # Re-run search with new options if there's a query
        if self.search_bar.text():
            self.perform_search()

    def filter_echo(self, data):
        if self.expecting_echo and self.last_command and data:
            escaped_cmd = re.escape(self.last_command)
            pattern = r'^(?:\x1b\[[0-9;?]*[a-zA-Z]|\r|\n)*' + escaped_cmd + r'(?:\r\n|\n)?'
            match = re.search(pattern, data)
            if match and match.start() == 0:
                data = data[match.end():]
                self.expecting_echo = False
            elif re.search(r'[a-zA-Z0-9]', data):
                self.expecting_echo = False
        return data

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        data = self.filter_echo(data)
        self.insert_ansi_text(data)

    def insert_text_with_cr(self, cursor, text):
        if not text:
            return
            
        if hasattr(self.output_area, 'in_raw_mode') and self.output_area.in_raw_mode:
            for char in text:
                if char == '\r':
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                elif char == '\n':
                    col = cursor.positionInBlock()
                    if cursor.blockNumber() == self.output_area.document().blockCount() - 1:
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                        cursor.insertText('\n', self.current_format)
                        if col > 0:
                            cursor.insertText(' ' * col)
                    else:
                        cursor.movePosition(QTextCursor.MoveOperation.Down)
                        block_len = cursor.block().length() - 1
                        if block_len < col:
                            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                            cursor.insertText(' ' * (col - block_len), self.current_format)
                        else:
                            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                            if col > 0: cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
                elif char == '\b':
                    if cursor.positionInBlock() > 0:
                        cursor.movePosition(QTextCursor.MoveOperation.Left)
                else:
                    if cursor.positionInBlock() < cursor.block().length() - 1:
                        cursor.deleteChar()
                    cursor.insertText(char, self.current_format)
            return

        def _overwrite(text_to_insert):
            if not text_to_insert:
                return
            lines = text_to_insert.split('\n')
            for idx, line in enumerate(lines):
                if idx > 0:
                    col = cursor.positionInBlock()
                    if cursor.blockNumber() == self.output_area.document().blockCount() - 1:
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                        cursor.insertText('\n', self.current_format)
                        if col > 0:
                            cursor.insertText(' ' * col, self.current_format)
                    else:
                        cursor.movePosition(QTextCursor.MoveOperation.Down)
                        block_len = cursor.block().length() - 1
                        if block_len < col:
                            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                            cursor.insertText(' ' * (col - block_len), self.current_format)
                        else:
                            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                            if col > 0: cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
                if line:
                    chars_avail = cursor.block().length() - 1 - cursor.positionInBlock()
                    if chars_avail > 0:
                        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, min(len(line), chars_avail))
                        cursor.removeSelectedText()
                    cursor.insertText(line, self.current_format)

        parts_b = text.split('\b')
        for i, part in enumerate(parts_b):
            if i > 0:
                if cursor.positionInBlock() > 0:
                    cursor.deletePreviousChar()

            if '\r' in part:
                sub_parts = part.split('\r')
                _overwrite(sub_parts[0])

                for sub_part in sub_parts[1:]:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    _overwrite(sub_part)
            else:
                _overwrite(part)


    def insert_ansi_text(self, text):
        # Strip OSC sequences (e.g. window title, hyperlinks) — both BEL and ST terminated
        text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', '', text)

        # Strip DCS / PM / APC / SOS sequences
        text = re.sub(r'\x1b[PX^_][^\x1b]*(?:\x1b\\|$)', '', text)

        # Strip non-CSI two-char ESC sequences:
        #   \x1b7 / \x1b8  — DECSC/DECRC save/restore cursor  → produce literal 7/8 if not stripped
        #   \x1b[()][...] — G0/G1 charset designations  e.g. \x1b(B
        #   \x1bM          — reverse index (scroll up one line)
        #   \x1b[=><]      — keypad modes
        #   \x1bN/O        — single-shift SS2/SS3
        text = re.sub(r'\x1b[78NOMEHcl]', '', text)
        text = re.sub(r'\x1b[()][a-zA-Z0-9]', '', text)
        text = re.sub(r'\x1b[=><]', '', text)

        # Strip CSI sequences we intentionally ignore (cursor visibility, mouse tracking, etc.)
        # These are the ?NNNh / ?NNNl forms not handled in the main loop
        text = re.sub(r'\x1b\[\?(?!1049|1047|47)\d+[hl]', '', text)

        cursor = self.output_area.textCursor()
        
        cursor.setPosition(self.output_area.input_start_pos)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        user_input = cursor.selectedText()
        if user_input:
            cursor.removeSelectedText()
            
        if '\x1bc' in text:
            self.output_area.clear()
            text = text.replace('\x1bc', '')
            
        parts = re.split(r'\x1b\[([0-9;?]*[a-zA-Z`])', text)
        
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.insert_text_with_cr(cursor, parts[0])
        
        for i in range(1, len(parts), 2):
            seq = parts[i]
            text_part = parts[i+1]
            
            if seq.endswith('m'):
                code_str = seq[:-1]
                codes = code_str.split(';') if code_str else ['0']
                    
                idx = 0
                while idx < len(codes):
                    code = codes[idx]
                    
                    if code in ('38', '48') and idx + 4 < len(codes) and codes[idx+1] == '2':
                        try:
                            r, g, b = int(codes[idx+2]), int(codes[idx+3]), int(codes[idx+4])
                            if code == '38':
                                self.current_format.setForeground(QColor(r, g, b))
                            else:
                                self.current_format.setBackground(QColor(r, g, b))
                        except ValueError:
                            pass
                        idx += 5
                        continue
                        
                    if code == '0' or code == '00':
                        self.current_format = QTextCharFormat()
                    elif code in COLOR_MAP:
                        self.current_format.setForeground(QColor(COLOR_MAP[code]))
                    elif code in BG_COLOR_MAP:
                        self.current_format.setBackground(QColor(BG_COLOR_MAP[code]))
                    elif code == '1' or code == '01':
                        self.current_format.setFontWeight(QFont.Weight.Bold)
                    elif code == '39':
                        if hasattr(self, 'current_theme'):
                            self.current_format.setForeground(QColor(self.current_theme['fg']))
                    elif code == '49':
                        self.current_format.clearBackground()
                    elif code == '7':
                        if hasattr(self, 'current_theme'):
                            self.current_format.setBackground(QColor(self.current_theme['fg']))
                            self.current_format.setForeground(QColor(self.current_theme['bg']))
                    elif code == '27':
                        self.current_format.clearBackground()
                        self.current_format.clearForeground()
                        
                    idx += 1
            elif seq.endswith('K'):
                if seq == 'K' or seq == '0K':
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                    cursor.removeSelectedText()
                elif seq == '2K':
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                    cursor.removeSelectedText()
            elif seq.endswith('X'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                col = cursor.positionInBlock()
                chars_avail = cursor.block().length() - 1 - col
                if chars_avail > 0:
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, min(n, chars_avail))
                    cursor.removeSelectedText()
                    cursor.insertText(' ' * min(n, chars_avail), self.current_format)
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, min(n, chars_avail))
            elif seq.endswith('L'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                col = cursor.positionInBlock()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.insertText('\n' * n)
                cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, n)
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
            elif seq.endswith('M'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                col = cursor.positionInBlock()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                for _ in range(n):
                    cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
            elif seq.endswith('A'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                cursor.movePosition(QTextCursor.MoveOperation.Up, n=n)
            elif seq.endswith('B'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                cursor.movePosition(QTextCursor.MoveOperation.Down, n=n)
            elif seq.endswith('C'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                cursor.movePosition(QTextCursor.MoveOperation.Right, n=n)
            elif seq.endswith('D'):
                n = int(seq[:-1]) if seq[:-1].isdigit() else 1
                cursor.movePosition(QTextCursor.MoveOperation.Left, n=n)
            elif seq.endswith('G') or seq.endswith('`'):
                col = int(seq[:-1]) if seq[:-1].isdigit() else 1
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                block_len = cursor.block().length() - 1
                if block_len < col - 1:
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    cursor.insertText(' ' * (col - 1 - block_len))
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col - 1)
            elif seq.endswith('d'):
                row = int(seq[:-1]) if seq[:-1].isdigit() else 1
                col = cursor.positionInBlock()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                while self.output_area.document().blockCount() < row:
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    cursor.insertText('\n')
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                if row > 1: cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.MoveAnchor, row - 1)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                block_len = cursor.block().length() - 1
                if block_len < col:
                    cursor.insertText(' ' * (col - block_len))
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                if col > 0: cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
            elif seq.endswith('H') or seq.endswith('f'):
                m = re.match(r'^([0-9]*);?([0-9]*)[Hf]$', seq)
                if m:
                    row = int(m.group(1)) if m.group(1) else 1
                    col = int(m.group(2)) if m.group(2) else 1
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    while self.output_area.document().blockCount() < row:
                        cursor.insertText('\n')
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    if row > 1: cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.MoveAnchor, row - 1)
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    block_len = cursor.block().length() - 1
                    if block_len < col - 1:
                        cursor.insertText(' ' * (col - 1 - block_len))
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    if col > 1: cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col - 1)
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
            elif seq.endswith('J'):
                if seq in ('2J', '3J'):
                    self.output_area.clear()
                    cursor = self.output_area.textCursor()
                elif seq in ('J', '0J'):
                    cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                    cursor.removeSelectedText()
                elif seq == '1J':
                    cursor.movePosition(QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.KeepAnchor)
                    cursor.removeSelectedText()
            elif seq in ('?1049h', '?1047h', '?47h'):
                self.output_area.in_raw_mode = True
                self.output_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            elif seq in ('?1049l', '?1047l', '?47l'):
                self.output_area.in_raw_mode = False
                self.output_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            
            self.insert_text_with_cr(cursor, text_part)
            
        self.output_area.setTextCursor(cursor)
        self.output_area.ensureCursorVisible()
        self.output_area.update_input_start()
        
        if user_input:
            self.output_area.insertPlainText(user_input)

class TerminalSplitter(QSplitter):
    def __init__(self, settings, parent_app):
        super().__init__(Qt.Orientation.Horizontal)
        self.settings = settings
        self.parent_app = parent_app
        self.add_session()

    def add_session(self):
        session = TerminalSession(self.settings, self)
        session.zoom_changed.connect(self.parent_app.handle_zoom)
        session.settings_requested.connect(self.parent_app.open_settings)
        session.session_closed.connect(lambda s=session: self.close_session(s))
        self.addWidget(session)
        session.output_area.setFocus()
        return session

    def close_session(self, session):
        session.setParent(None)
        if hasattr(session, 'process') and session.process.state() == QProcess.ProcessState.Running:
            try: session.process.finished.disconnect()
            except TypeError: pass
            session.process.terminate()
            if not session.process.waitForFinished(100):
                session.process.kill()
        session.deleteLater()
        
        if self.count() == 0:
            self.parent_app.close_tab_by_widget(self)

class UpdateChecker(QThread):
    update_notif = pyqtSignal(list, bool)

    def run(self):
        app_update = False
        pkg_updates = []
        try:
            project_id, api_key = vpm.get_remote_credentials()
        except Exception:
            return

        try:
            ctx = ssl._create_unverified_context()
            
            # Check Terminal App
            req = urllib.request.Request(f"https://sncloud.in/api/db/{project_id}/app/terminal.json?_t={int(time.time())}", headers={'User-Agent': 'Velora/1.0', 'X-API-Key': api_key, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and data != 'null':
                    cloud_app_ver = data.get('version', '1.0.0').strip() if isinstance(data, dict) else '1.0.0'
                    if self.is_newer(cloud_app_ver, __version__):
                        app_update = True
                        
            # Check Packages
            req = urllib.request.Request(f"https://sncloud.in/api/db/{project_id}/packages.json?_t={int(time.time())}", headers={'User-Agent': 'Velora/1.0', 'X-API-Key': api_key, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if isinstance(data, dict):
                    # Refresh the local cache for the 'vpm list' command
                    cache_path = os.path.expanduser("~/.velora/vpm_cache.json")
                    try:
                        with open(cache_path, 'w') as f: json.dump(data, f)
                    except: pass

                    core_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
                    user_core_dir = os.path.expanduser("~/.velora/core")
                    for pkg, info in data.items():
                        if isinstance(info, dict):
                            cloud_ver = info.get('version', '1.0.0').strip()
                            local_user = os.path.join(user_core_dir, f"{pkg}.py")
                            local_bundled = os.path.join(core_dir, f"{pkg}.py")
                            local_path = local_user if os.path.exists(local_user) else local_bundled
                            
                            if os.path.exists(local_path):
                                try:
                                    with open(local_path, 'r', encoding='utf-8') as f: content = f.read()
                                    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                                    local_ver = m.group(1).strip() if m else "1.0.0"
                                except Exception: local_ver = "1.0.0"
                                
                                if self.is_newer(cloud_ver, local_ver):
                                    pkg_updates.append(pkg)
        except Exception: pass
            
        if app_update or pkg_updates:
            self.update_notif.emit(pkg_updates, app_update)

    def is_newer(self, cloud_ver, local_ver):
        cloud_ver = cloud_ver.strip()
        local_ver = local_ver.strip()
        try:
            c_parts, l_parts = [int(x) for x in cloud_ver.split('.')], [int(x) for x in local_ver.split('.')]
            return c_parts > l_parts
        except Exception: return cloud_ver != local_ver

class TerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Velora")
        
        self.setup_core_wrappers()
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'velora.png')
        self.setWindowIcon(QIcon(icon_path))
        self.resize(900, 600)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        self.settings = QSettings("Velora", "Settings")

        self.central_container = QWidget()
        self.central_container.setObjectName("MainContainer")
        self.central_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.central_layout = QVBoxLayout(self.central_container)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)           # drag-to-reorder tabs
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)  # elide long names
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.central_layout.addWidget(self.tabs)
        self.setCentralWidget(self.central_container)
        
        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setToolTip("Open New Tab (Ctrl+T)")
        self.add_tab_btn.clicked.connect(self.new_tab)
        
        self.vpm_btn = QToolButton()
        self.vpm_btn.setText("📦")
        self.vpm_btn.setToolTip("Package Manager (Ctrl+Shift+P)")
        self.vpm_btn.clicked.connect(self.open_vpm)
        
        self.corner_widget = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget)
        self.corner_layout.setContentsMargins(0, 0, 0, 0)
        self.corner_layout.setSpacing(0)
        self.corner_layout.addWidget(self.vpm_btn)
        self.corner_layout.addWidget(self.add_tab_btn)
        self.tabs.setCornerWidget(self.corner_widget, Qt.Corner.TopRightCorner)

        self.status_bar = self.statusBar()
        self.update_btn = QPushButton("  🔔 Updates Available  ")
        self.update_btn.setVisible(False)
        self.update_btn.clicked.connect(self.show_detailed_updates)
        self.status_bar.addPermanentWidget(self.update_btn)
        
        self.update_status_bar(int(self.settings.value("font_size", 11)))
        
        # Shortcuts
        self.shortcut_new_tab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_new_tab.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_new_tab.activated.connect(self.handle_shortcut_ctrl_t)

        self.shortcut_close_tab = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_close_tab.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_close_tab.activated.connect(self.handle_shortcut_ctrl_w)
        
        self.shortcut_next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self.shortcut_next_tab.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_next_tab.activated.connect(self.next_tab)

        self.shortcut_prev_tab = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        self.shortcut_prev_tab.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_prev_tab.activated.connect(self.prev_tab)

        self.shortcut_fullscreen = QShortcut(QKeySequence("F11"), self)
        self.shortcut_fullscreen.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_fullscreen.activated.connect(self.toggle_fullscreen)

        self.shortcut_vpm = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        self.shortcut_vpm.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_vpm.activated.connect(self.open_vpm)

        self.tab_counter = 0

        self.new_tab()
        self.apply_theme()
        
        self.update_checker = UpdateChecker()
        self.update_checker.update_notif.connect(self.show_update_notification)
        self.update_checker.start()

    def setup_core_wrappers(self):
        import shutil
        velora_bin = os.path.expanduser("~/.velora/bin")
        user_core = os.path.expanduser("~/.velora/core")
        os.makedirs(user_core, exist_ok=True)
        
        try:
            if os.path.exists(velora_bin):
                shutil.rmtree(velora_bin)
            os.makedirs(velora_bin, exist_ok=True)
            
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            bundled_core = os.path.join(base_dir, 'core')
            
            core_files = set()
            if os.path.exists(bundled_core): core_files.update(f for f in os.listdir(bundled_core) if f.endswith('.py') and f != '__init__.py')
            if os.path.exists(user_core): core_files.update(f for f in os.listdir(user_core) if f.endswith('.py') and f != '__init__.py')
                
            # Add vpm explicitly if separated from core folder
            if os.path.exists(os.path.join(base_dir, "vpm.py")):
                core_files.add("vpm.py")

            is_frozen = getattr(sys, 'frozen', False)
            
            for file in core_files:
                cmd_name = file[:-3]
                wrapper_path = os.path.join(velora_bin, cmd_name)
                
                if is_frozen: command_prefix = f'"{sys.executable}" --run-core {cmd_name}'
                else:
                    term_path = os.path.join(base_dir, "terminal.py")
                    command_prefix = f'"{sys.executable}" "{term_path}" --run-core {cmd_name}'
                
                if os.name == 'nt':
                    wrapper_path += '.cmd'
                    with open(wrapper_path, 'w') as f: f.write(f'@echo off\n{command_prefix} %*\n')
                else:
                    with open(wrapper_path, 'w') as f: f.write(f'#!/bin/sh\nexec {command_prefix} "$@"\n')
                    os.chmod(wrapper_path, 0o755)
        except Exception:
            pass

    def get_active_session(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, TerminalSplitter):
            for i in range(widget.count()):
                session = widget.widget(i)
                if hasattr(session, 'output_area') and (session.output_area.hasFocus() or session.search_bar.hasFocus()):
                    return session
            if widget.count() > 0:
                return widget.widget(0)
        elif isinstance(widget, TerminalSession):
            return widget
        return None
        
    def show_detailed_updates(self):
        """Show detailed update information in a new terminal session"""
        session = self.get_active_session()
        if session:
            detailed_msg = "\r\n\x1b[38;5;51m\x1b[1m⚡ VELORA SYSTEM REFERENCE \x1b[0m\x1b[90m(Help & Documentation)\x1b[0m\r\n\n"
            
            detailed_msg += " \x1b[1m📦 Package Management\x1b[0m\r\n"
            detailed_msg += " \x1b[90m" + "─" * 75 + "\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm list\x1b[0m           \x1b[97mBrowse all available packages\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm info <pkg>\x1b[0m     \x1b[97mGet detailed info about a package\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm install <pkg>\x1b[0m  \x1b[97mInstall a new package\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm update <pkg>\x1b[0m   \x1b[97mUpdate a specific package\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm update-all\x1b[0m     \x1b[97mUpdate all installed packages\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm remove <pkg>\x1b[0m   \x1b[97mRemove a package\x1b[0m\r\n\n"
            
            detailed_msg += " \x1b[1m🚀 System Updates\x1b[0m\r\n"
            detailed_msg += " \x1b[90m" + "─" * 75 + "\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ vpm upgrade\x1b[0m        \x1b[97mUpgrade the terminal application\x1b[0m\r\n"
            
            # Show bootstrap command
            system = platform.system()
            if system == "Windows":
                bootstrap_cmd = 'powershell.exe -Command "cd $env:USERPROFILE; Invoke-WebRequest -Uri https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py -OutFile bootstrap.py; python bootstrap.py"'
            else:
                bootstrap_cmd = "curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3"
            
            detailed_msg += f" \x1b[32m◆ {bootstrap_cmd}\x1b[0m\r\n"
            detailed_msg += "   \x1b[90mFull system bootstrap/update from repository\x1b[0m\r\n\n"
            
            detailed_msg += " \x1b[1m🔧 System Information\x1b[0m\r\n"
            detailed_msg += " \x1b[90m" + "─" * 75 + "\x1b[0m\r\n"
            detailed_msg += f" \x1b[36mPlatform:\x1b[0m     \x1b[97m{platform.system()} {platform.release()}\x1b[0m\r\n"
            detailed_msg += f" \x1b[36mPython:\x1b[0m       \x1b[97m{sys.version.split()[0]}\x1b[0m\r\n"
            detailed_msg += f" \x1b[36mArchitecture:\x1b[0m \x1b[97m{platform.machine()}\x1b[0m\r\n"
            detailed_msg += f" \x1b[36mVersion:\x1b[0m      \x1b[97mv{__version__}\x1b[0m\r\n\n"
            
            detailed_msg += " \x1b[1m⚡ Quick Start Commands\x1b[0m\r\n"
            detailed_msg += " \x1b[90m" + "─" * 75 + "\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ help\x1b[0m               \x1b[97mShow this help information\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ sysinfo\x1b[0m            \x1b[97mDisplay system hardware information\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ weather\x1b[0m            \x1b[97mCheck local weather forecasts\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ calc\x1b[0m               \x1b[97mOpen the calculator tool\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ notes\x1b[0m              \x1b[97mLaunch note-taking application\x1b[0m\r\n"
            detailed_msg += " \x1b[32m◆ todo\x1b[0m               \x1b[97mManage your tasks\x1b[0m\r\n\n"
            
            session.insert_ansi_text(detailed_msg)

    def show_update_notification(self, pkg_updates, app_update):
        self.update_btn.setVisible(True)
        self.update_btn.setStyleSheet("background: transparent; border: 1px solid #50fa7b; color: #50fa7b; border-radius: 4px; font-weight: bold; margin-right: 10px;")
        
        session = self.get_active_session()
        if session and hasattr(session, 'insert_ansi_text'):
            msg = "\r\n\x1b[32;1m🚀 Updates Available!\x1b[0m\r\n"
            msg += "\x1b[36;1m═══ Update Details ═══\x1b[0m\r\n"
            
            if app_update:
                msg += "\x1b[33;1m• Terminal App Update Available\x1b[0m\r\n"
                msg += "  \x1b[36mRun: \x1b[32;1mvpm upgrade\x1b[36m to update the terminal\x1b[0m\r\n"
                
                # Show bootstrap command for major updates
                system = platform.system()
                if system == "Windows":
                    bootstrap_cmd = 'powershell.exe -Command "cd $env:USERPROFILE; Invoke-WebRequest -Uri https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py -OutFile bootstrap.py; python bootstrap.py"'
                else:
                    bootstrap_cmd = "curl -sSL https://raw.githubusercontent.com/SouvikNandi1/Velora/main/bootstrap.py | python3"
                
                msg += f"  \x1b[36mOr run: \x1b[32;1m{bootstrap_cmd}\x1b[36m for full reinstall\x1b[0m\r\n"
            
            if pkg_updates:
                msg += f"\x1b[33;1m• Package Updates Available ({len(pkg_updates)}):\x1b[0m\r\n"
                for pkg in pkg_updates[:5]:  # Show first 5, truncate if more
                    msg += f"  \x1b[32m• {pkg}\x1b[0m\r\n"
                if len(pkg_updates) > 5:
                    msg += f"  \x1b[90m... and {len(pkg_updates) - 5} more\x1b[0m\r\n"
                msg += "  \x1b[36mRun: \x1b[32;1mvpm update-all\x1b[36m to update all packages\x1b[0m\r\n"
            
            msg += "\r\n\x1b[90m💡 Tip: Use 'vpm list' to browse all available packages\x1b[0m\r\n"
            user_input = session.output_area.get_current_command()
            session.insert_ansi_text(msg)
            if not user_input:  # Drop a fresh prompt if the user hasn't typed anything yet
                session.run_control_sequence("\r")

    def handle_shortcut_ctrl_t(self):
        session = self.get_active_session()
        if session and hasattr(session.output_area, 'in_raw_mode') and session.output_area.in_raw_mode:
            session.run_control_sequence('\x14')
        else:
            self.new_tab()

    def handle_shortcut_ctrl_w(self):
        session = self.get_active_session()
        if session and hasattr(session.output_area, 'in_raw_mode') and session.output_area.in_raw_mode:
            session.run_control_sequence('\x17')
        else:
            self.close_current_tab()

    def show_tab_context_menu(self, point):
        tab_bar = self.tabs.tabBar()
        # Convert point from QTabWidget coords to QTabBar coords
        bar_point = tab_bar.mapFromParent(point)
        index = tab_bar.tabAt(bar_point)
        if index == -1:
            return

        theme_name = self.settings.value("theme", "Dracula (Dark)")
        theme = THEMES.get(theme_name, THEMES["Dracula (Dark)"])

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 6px 4px;
            }}
            QMenu::item {{
                padding: 7px 28px 7px 16px;
                border-radius: 6px;
                margin: 2px 4px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {theme['sel']};
            }}
            QMenu::item:disabled {{
                color: {theme['border']};
                opacity: 0.5;
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme['border']};
                margin: 4px 10px;
            }}
        """)

        split_h_action = menu.addAction("Split Side-by-Side")
        split_v_action = menu.addAction("Split Top-to-Bottom")
        split_h_action.setEnabled(isinstance(self.tabs.widget(index), TerminalSplitter))
        split_v_action.setEnabled(isinstance(self.tabs.widget(index), TerminalSplitter))
        menu.addSeparator()

        duplicate_action = menu.addAction("Duplicate Tab")
        menu.addSeparator()
        rename_action = menu.addAction("Rename Tab...")
        menu.addSeparator()
        close_action = menu.addAction("Close Tab")
        close_others_action = menu.addAction("Close Other Tabs")
        close_others_action.setEnabled(self.tabs.count() > 1)

        action = menu.exec(self.tabs.mapToGlobal(point))

        if action == split_h_action:
            widget = self.tabs.widget(index)
            if isinstance(widget, TerminalSplitter):
                widget.setOrientation(Qt.Orientation.Horizontal)
                widget.add_session()
        elif action == split_v_action:
            widget = self.tabs.widget(index)
            if isinstance(widget, TerminalSplitter):
                widget.setOrientation(Qt.Orientation.Vertical)
                widget.add_session()
        elif action == duplicate_action:
            self.duplicate_tab(index)
        elif action == rename_action:
            raw_name = self.tabs.tabText(index)
            # Strip the icon prefix (everything up to and including the two spaces after it)
            # Icon prefixes look like " ❯_  " or " ⚙  "
            import re as _re
            clean_name = _re.sub(r'^\s*\S+\s+', '', raw_name).strip()
            dialog = QInputDialog(self)
            dialog.setStyleSheet(f"""
                QDialog {{ background-color: {theme['bg']}; color: {theme['fg']}; }}
                QLabel {{ color: {theme['fg']}; }}
                QLineEdit {{
                    background-color: {theme['sel']};
                    color: {theme['fg']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 6px 10px;
                }}
                QPushButton {{
                    background-color: {theme['sel']};
                    color: {theme['fg']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 6px 16px;
                }}
                QPushButton:hover {{ background-color: {theme['border']}; }}
            """)
            dialog.setWindowTitle("Rename Tab")
            dialog.setLabelText("New tab name:")
            dialog.setTextValue(clean_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_name = dialog.textValue().strip()
                if new_name:
                    # Re-apply the ❯_ icon prefix for terminal tabs
                    self.tabs.setTabText(index, f" ❯_  {new_name}")
        elif action == close_action:
            self.close_tab(index)
        elif action == close_others_action:
            # Collect indices to close BEFORE removing any (indices shift after each removal)
            to_close = [i for i in range(self.tabs.count()) if i != index]
            # Remove from right-to-left so earlier indices stay stable
            for i in sorted(to_close, reverse=True):
                self.close_tab(i)

    def duplicate_tab(self, index):
        self.tab_counter += 1
        name = self.tabs.tabText(index)
        new_splitter = TerminalSplitter(self.settings, self)
        idx = self.tabs.addTab(new_splitter, name)
        self.tabs.setCurrentIndex(idx)

    def new_tab(self, *args):
        self.tab_counter += 1
        splitter = TerminalSplitter(self.settings, self)
        idx = self.tabs.addTab(splitter, f" ❯_  Terminal {self.tab_counter}")
        self.tabs.setCurrentIndex(idx)
        # Focus is handled in TerminalSplitter.add_session()

    def close_tab_by_widget(self, widget):
        """Called by a TerminalSplitter when its last session exits.
        We force-remove the tab without quitting even if it's the last one
        (the user's shell exited; we keep the window open with an empty state)."""
        idx = self.tabs.indexOf(widget)
        if idx != -1:
            self.close_tab(idx, force=True)

    def close_tab(self, index, force=False):
        """Close the tab at *index*.
        If it is the last tab and *force* is False the whole window closes.
        If *force* is True (called when a shell exits) we open a fresh tab instead.
        """
        widget = self.tabs.widget(index)
        # Terminate any running processes inside the widget
        if isinstance(widget, TerminalSplitter):
            sessions = [widget.widget(i) for i in range(widget.count())]
            for session in sessions:
                if isinstance(session, TerminalSession) and hasattr(session, 'process') and session.process.state() == QProcess.ProcessState.Running:
                    try: session.process.finished.disconnect()
                    except TypeError: pass
                    session.process.terminate()
                    if not session.process.waitForFinished(100):
                        session.process.kill()
        elif widget is not None and hasattr(widget, 'process') and widget.process.state() == QProcess.ProcessState.Running:
            try: widget.process.finished.disconnect()
            except TypeError: pass
            widget.process.terminate()
            if not widget.process.waitForFinished(100):
                widget.process.kill()

        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            if widget is not None:
                widget.deleteLater()
        elif force:
            # Last tab but shell exited — open a fresh tab so window stays open
            self.tabs.removeTab(index)
            if widget is not None:
                widget.deleteLater()
            self.new_tab()
        else:
            # User explicitly closed the last tab — quit
            self.close()

    def close_current_tab(self, *args):
        self.close_tab(self.tabs.currentIndex())
        
    def next_tab(self, *args):
        if self.tabs.count() > 1:
            next_idx = (self.tabs.currentIndex() + 1) % self.tabs.count()
            self.tabs.setCurrentIndex(next_idx)
            
    def prev_tab(self, *args):
        if self.tabs.count() > 1:
            prev_idx = (self.tabs.currentIndex() - 1) % self.tabs.count()
            self.tabs.setCurrentIndex(prev_idx)

    def toggle_fullscreen(self, *args):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalSplitter):
                sessions = [widget.widget(j) for j in range(widget.count())]
                for session in sessions:
                    if isinstance(session, TerminalSession) and hasattr(session, 'process') and session.process.state() == QProcess.ProcessState.Running:
                        try: session.process.finished.disconnect()
                        except TypeError: pass
                        session.process.terminate()
                        if not session.process.waitForFinished(100):
                            session.process.kill()
            elif widget is not None and hasattr(widget, 'process') and widget.process.state() == QProcess.ProcessState.Running:
                try: widget.process.finished.disconnect()
                except TypeError: pass
                widget.process.terminate()
                if not widget.process.waitForFinished(100):
                    widget.process.kill()
        event.accept()

    def apply_settings_to_all(self):
        for i in range(self.tabs.count()):
            session = self.tabs.widget(i)
            if isinstance(session, TerminalSplitter):
                for j in range(session.count()):
                    pane = session.widget(j)
                    if hasattr(pane, 'apply_font'):
                        pane.apply_font()
                    if hasattr(pane, 'apply_theme'):
                        pane.apply_theme()
            else:
                if hasattr(session, 'apply_font'):
                    session.apply_font()
                if hasattr(session, 'apply_theme'):
                    session.apply_theme()
        self.apply_theme()

    def clear_all_history(self):
        for i in range(self.tabs.count()):
            session = self.tabs.widget(i)
            if isinstance(session, TerminalSplitter):
                for j in range(session.count()):
                    pane = session.widget(j)
                    if hasattr(pane, 'clear_history'):
                        pane.clear_history()
            elif isinstance(session, TerminalSession) and hasattr(session, 'clear_history'):
                session.clear_history()

    def apply_theme(self):
        theme_name = self.settings.value("theme", "Dracula (Dark)")
        theme = THEMES.get(theme_name, THEMES["Dracula (Dark)"])
        opacity = int(self.settings.value("opacity", 85))
        bg_rgba = get_rgba_from_hex(theme['bg'], opacity)
        border_rgba = get_rgba_from_hex(theme['border'], 60)
        sel_rgba = get_rgba_from_hex(theme['sel'], 90)

        img_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'velora.png')
        img_url = QUrl.fromLocalFile(img_file).toString()

        self.setStyleSheet(f"""
            #MainWindow {{
                background: transparent;
                border-image: url('{img_url}') 0 0 0 0 stretch stretch;
            }}
            #MainContainer {{
                background-color: {bg_rgba};
                border-radius: 12px;
            }}
            TerminalSplitter {{ background-color: transparent; }}
            QSplitter::handle {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent, stop:0.5 {border_rgba}, stop:1 transparent);
            }}
            QSplitter::handle:horizontal {{ width: 3px; margin: 8px 0; }}
            QSplitter::handle:vertical {{ height: 3px; margin: 0 8px; }}
            QTabWidget {{ background: transparent; }}
            QTabWidget::pane {{
                background-color: transparent;
                border: none;
                border-top: 1px solid {border_rgba};
                margin-top: -1px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar {{
                background: transparent;
                qproperty-drawBase: 0;
            }}
            QTabBar::tab {{
                background: transparent;
                color: rgba({_hex_to_rgb_str(theme['fg'])}, 0.45);
                padding: 9px 20px 8px 16px;
                border: none;
                border-bottom: 2px solid transparent;
                border-radius: 0px;
                margin: 0px 1px;
                font-size: 13px;
                font-weight: 500;
                min-width: 110px;
                letter-spacing: 0.3px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({_hex_to_rgb_str(theme['sel'])}, 0.95),
                    stop:1 rgba({_hex_to_rgb_str(theme['bg'])}, 0.0));
                color: {theme['fg']};
                font-weight: 700;
                border-bottom: 2px solid {theme['border']};
            }}
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.06),
                    stop:1 rgba(255, 255, 255, 0.0));
                color: rgba({_hex_to_rgb_str(theme['fg'])}, 0.75);
                border-bottom: 2px solid {border_rgba};
            }}
            QTabBar::close-button {{
                subcontrol-position: right;
                padding: 2px 3px;
                margin-left: 4px;
                border-radius: 6px;
            }}
            QTabBar::close-button:hover {{
                background-color: rgba(255, 80, 80, 0.40);
            }}
            QToolButton {{
                background-color: transparent;
                color: {theme['fg']};
                border: 1px solid {border_rgba};
                font-weight: bold;
                font-size: 16px;
                padding: 4px 12px;
                margin: 5px 6px;
                border-radius: 20px;
            }}
            QToolButton:hover {{
                background-color: {sel_rgba};
                border: 1px solid {theme['border']};
            }}
            QStatusBar {{
                background-color: transparent;
                color: {theme['border']};
                border-top: 1px solid {border_rgba};
                padding: 3px 14px;
                font-size: 12px;
            }}
        """)

    def open_vpm(self):
        # Jump to the VPM tab if it is already open
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), VPMTab):
                self.tabs.setCurrentIndex(i)
                return
                
        vpm_tab = VPMTab(self.settings, self)
        idx = self.tabs.addTab(vpm_tab, " 📦  Packages")
        self.tabs.setCurrentIndex(idx)

    def open_settings(self):
        # Jump to the settings tab if it is already open
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), SettingsTab):
                self.tabs.setCurrentIndex(i)
                return
                
        settings_tab = SettingsTab(self.settings, self)
        settings_tab.settings_applied.connect(self.apply_settings_to_all)
        settings_tab.history_cleared.connect(self.clear_all_history)
        idx = self.tabs.addTab(settings_tab, " ⚙  Settings")
        self.tabs.setCurrentIndex(idx)

    def handle_zoom(self, size):
        self.settings.setValue("font_size", size)
        self.update_status_bar(size)
        self.apply_settings_to_all()

    def update_status_bar(self, size):
        self.status_bar.showMessage(
            f"  ⚡ Velora Terminal   │  🔤 Font: {size}pt   │  ✦ Ctrl+T New Tab   │  ✦ Ctrl+W Close   │  ✦ F11 Fullscreen  "
        )

if __name__ == '__main__':
    # Fix for Windows Taskbar Icon: Ensure the custom PNG icon shows up in the taskbar
    if os.name == 'nt':
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("qelaro.velora.terminal")
        except Exception:
            pass

    app = QApplication(sys.argv)
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'velora.png')
    app.setWindowIcon(QIcon(icon_path))
    
    window = TerminalApp()
    window.show()
    sys.exit(app.exec())