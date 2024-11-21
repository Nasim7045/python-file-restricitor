
from __future__ import annotations

import os
import sys  # Used for sys.exit() in main()
import time
import logging
import threading
import pythoncom
import win32clipboard
import win32con
import win32gui
import pyperclip
import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win32com.shell import shell
from typing import List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
ROOT_DIR: str = os.path.abspath(r"C:\Users\ASUS")
CLIPBOARD_CHECK_INTERVAL: float = 0.1
FILE_OPERATION_TIMEOUT: float = 0.5

class ClipboardMonitor:
    """Monitors clipboard activity for file operations."""
    
    def __init__(self) -> None:
        self.last_content: str = ""
        self.last_blocked_time: float = 0
        self.blocking_active: bool = True
        self.is_running: bool = True

    def is_file_content(self, content: str) -> bool:
        try:
            return os.path.exists(content) or '\r\n' in content
        except Exception:
            return False

    def is_protected_path(self, path: str) -> bool:
        try:
            return os.path.abspath(path).lower().startswith(ROOT_DIR.lower())
        except Exception:
            return False

    def get_clipboard_files(self) -> List[str]:
        try:
            pythoncom.CoInitialize()
            win32clipboard.OpenClipboard()
            
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                file_list = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                return [file for file in file_list]
            
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                if self.is_file_content(text):
                    return [text]
                    
        except Exception as e:
            logger.error("Error reading clipboard: %s", str(e))
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            pythoncom.CoUninitialize()
            
        return []

    def clear_clipboard(self) -> None:
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            pyperclip.copy('')
        except Exception as e:
            logger.error("Error clearing clipboard: %s", str(e))

    def stop_monitoring(self) -> None:
        self.is_running = False

    def monitor(self) -> None:
        while self.is_running:
            try:
                if not self.blocking_active:
                    time.sleep(CLIPBOARD_CHECK_INTERVAL)
                    continue

                files = self.get_clipboard_files()
                
                if files:
                    protected_files = [f for f in files if self.is_protected_path(f)]
                    
                    if protected_files:
                        active_window = win32gui.GetWindowText(
                            win32gui.GetForegroundWindow()
                        ).lower()
                        
                        if not any(safe_app in active_window 
                                 for safe_app in ['explorer', 'root directory']):
                            logger.info("Blocking copy of protected files: %s", 
                                      ", ".join(protected_files))
                            self.clear_clipboard()
                            self.last_blocked_time = time.time()
                
            except Exception as e:
                logger.error("Clipboard monitor error: %s", str(e))
            
            time.sleep(CLIPBOARD_CHECK_INTERVAL)


class FileSystemProtector(FileSystemEventHandler):
    """Monitors filesystem events to prevent unauthorized file operations."""
    
    def __init__(self) -> None:
        super().__init__()
        self.clipboard_monitor = ClipboardMonitor()
        self.last_event_time: float = 0
        self.processed_events: Set[str] = set()
        self.is_running: bool = True

    def is_within_root(self, path: str) -> bool:
        try:
            return os.path.abspath(path).lower().startswith(ROOT_DIR.lower())
        except Exception:
            return False

    def on_moved(self, event) -> None:
        if event.is_directory:
            return

        try:
            src_protected = self.is_within_root(event.src_path)
            dest_protected = self.is_within_root(event.dest_path)

            if src_protected and not dest_protected:
                try:
                    os.rename(event.dest_path, event.src_path)
                except Exception:
                    try:
                        os.remove(event.dest_path)
                    except Exception:
                        pass
                logger.info("Blocked move: %s -> %s", 
                           event.src_path, event.dest_path)
        except Exception as e:
            logger.error("Error handling move event: %s", str(e))

    def on_created(self, event) -> None:
        if event.is_directory:
            return

        try:
            current_time = time.time()
            event_key = f"{event.src_path}_{current_time}"
            
            if event_key in self.processed_events:
                return
                
            self.processed_events.add(event_key)
            self.processed_events = {
                k for k in self.processed_events 
                if current_time - float(k.split('_')[1]) < 5
            }

            if not self.is_within_root(event.src_path):
                clipboard_files = self.clipboard_monitor.get_clipboard_files()
                
                for clip_file in clipboard_files:
                    if self.is_within_root(clip_file):
                        try:
                            os.remove(event.src_path)
                            self.clipboard_monitor.clear_clipboard()
                            logger.info("Blocked file creation outside root: %s", 
                                      event.src_path)
                        except Exception as e:
                            logger.error("Error removing blocked file: %s", str(e))
                        break

        except Exception as e:
            logger.error("Error handling creation event: %s", str(e))

    def stop_monitoring(self) -> None:
        self.is_running = False


class KeyboardMonitor:
    """Monitors keyboard shortcuts to prevent unauthorized copy operations."""
    
    def __init__(self) -> None:
        self.clipboard_monitor = ClipboardMonitor()
        self.is_running: bool = True

    def stop_monitoring(self) -> None:
        self.is_running = False

    def monitor(self) -> None:
        while self.is_running:
            try:
                active_window = win32gui.GetWindowText(
                    win32gui.GetForegroundWindow()
                ).lower()
                
                if keyboard.is_pressed('ctrl+c') or keyboard.is_pressed('ctrl+x'):
                    time.sleep(0.1)
                    
                    clipboard_files = self.clipboard_monitor.get_clipboard_files()
                    protected_files = [
                        f for f in clipboard_files 
                        if os.path.abspath(f).lower().startswith(ROOT_DIR.lower())
                    ]
                    
                    if protected_files and not any(
                        safe_app in active_window 
                        for safe_app in ['explorer', 'root directory']
                    ):
                        self.clipboard_monitor.clear_clipboard()
                        logger.info("Blocked keyboard copy of protected files")
                        time.sleep(0.5)
                        
            except Exception as e:
                logger.error("Error in keyboard monitoring: %s", str(e))
                
            time.sleep(0.1)


def main() -> None:
    # Check for admin privileges
    if not shell.IsUserAnAdmin():
        logger.error("Please run this script with administrator privileges")
        sys.exit(1)

    logger.info("Starting enhanced file protection for %s", ROOT_DIR)
    logger.info("Press Ctrl+Q to exit")

    # Initialize protection systems
    file_protector = FileSystemProtector()
    observer = Observer()
    observer.schedule(file_protector, ROOT_DIR, recursive=True)
    observer.start()

    # Initialize monitors
    clipboard_monitor = ClipboardMonitor()
    keyboard_monitor = KeyboardMonitor()

    # Start monitoring threads
    clipboard_thread = threading.Thread(
        target=clipboard_monitor.monitor, 
        daemon=True
    )
    keyboard_thread = threading.Thread(
        target=keyboard_monitor.monitor, 
        daemon=True
    )
    
    clipboard_thread.start()
    keyboard_thread.start()

    try:
        while True:
            if keyboard.is_pressed('ctrl+q'):
                logger.info("Exiting...")
                clipboard_monitor.stop_monitoring()
                keyboard_monitor.stop_monitoring()
                file_protector.stop_monitoring()
                observer.stop()
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        clipboard_monitor.stop_monitoring()
        keyboard_monitor.stop_monitoring()
        file_protector.stop_monitoring()
        observer.stop()
    
    observer.join()
    logger.info("Protection system stopped.")


if __name__ == "__main__":
    main()
