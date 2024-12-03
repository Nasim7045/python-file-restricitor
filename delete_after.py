import os  #required for OS operations
import pyperclip  #required for clipboard operations monitoring
import time #inside python already may not require installation
from watchdog.observers import Observer    # required for monitoring folders and show the output
from watchdog.events import FileSystemEventHandler

# Define the root directory to monitor
ROOT_DIR = r"D:\Projects" #change according to your root directory
MONITORED_DRIVE = r"D:\\"  # Entire your drive to monitor , in this case its D:

class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.handle_file_operation(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.handle_file_operation(event.src_path)

    def handle_file_operation(self, src_path):
        """Monitor file operations."""
        print(f"File operation detected: {src_path}")
        
        # Check if the file operation is within ROOT_DIR
        if os.path.commonpath([src_path, ROOT_DIR]) == ROOT_DIR:
            print(f"File operation within root directory: {src_path}")
        else:
            print(f"File operation outside root directory: {src_path}")
            self.check_pasted_file(src_path)

    def check_pasted_file(self, src_path):
        """Check if the pasted file is from ROOT_DIR and delete it if necessary."""
        # Check if the file is pasted outside ROOT_DIR
        if os.path.commonpath([src_path, ROOT_DIR]) != ROOT_DIR:
            # Check if the file exists within ROOT_DIR (i.e., it was copied from ROOT_DIR)
            if self.is_file_from_root(src_path):
                print(f"File pasted outside ROOT_DIR: {src_path}")
                print(f"Deleting the pasted file: {src_path}")
                try:
                    os.remove(src_path)  # Delete the file
                    print(f"File deleted successfully: {src_path}")
                except Exception as e:
                    print(f"Error deleting file {src_path}: {e}")
            else:
                print(f"File is not from ROOT_DIR, skipping delete: {src_path}")

    def is_file_from_root(self, file_path):
        """Check if the file is from ROOT_DIR."""
        try:
            # Check if the file exists in ROOT_DIR by matching the filename
            for root, dirs, files in os.walk(ROOT_DIR):
                if os.path.basename(file_path) in files:
                    return True
            return False
        except Exception as e:
            print(f"Error checking if file is from ROOT_DIR: {e}")
            return False

def monitor_clipboard():
    """Monitor clipboard content for copy-paste operations."""
    previous_clipboard = ""
    while True:
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard != previous_clipboard:
                previous_clipboard = current_clipboard
                # Check if the clipboard content is a valid file path
                if os.path.exists(current_clipboard):
                    # Check if the path is from ROOT_DIR
                    if os.path.commonpath([current_clipboard, ROOT_DIR]) == ROOT_DIR:
                        print("Clipboard contains a path from the root directory!")
                    else:
                        # If pasting outside ROOT_DIR, warn and clear clipboard
                        print("Warning: You are attempting to paste a file path from ROOT_DIR to an external location.")
                        print("Clearing clipboard to prevent pasting outside ROOT_DIR.")
                        pyperclip.copy("")  # Clear clipboard content
                else:
                    print("Clipboard does not contain a valid file path.")
        except Exception as e:
            print(f"Error accessing clipboard: {e}")
        time.sleep(1)

def monitor_directory():
    """Monitor directory for file modifications or creations."""
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=MONITORED_DRIVE, recursive=True)  # Monitor entire D drive
    observer.start()

    try:
        # Run clipboard monitoring alongside directory monitoring
        monitor_clipboard()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    print("Monitoring file operations and clipboard...")
    monitor_directory()

if __name__ == "__main__":
    main()
