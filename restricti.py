import os
import pyperclip
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import ctypes

# Define the root directory to monitor
ROOT_DIR = r"D:\FlaskApp"  # Replace with your actual root directory
MONITORED_DRIVES = ["C:\\", "D:\\", "E:\\"]  # Drives to monitor

class FileHandler(FileSystemEventHandler):
    def on_moved(self, event):
        """Handle file and folder moves."""
        src_path = event.src_path
        dest_path = event.dest_path

        print(f"Move operation detected: {src_path} -> {dest_path}")

        # Restrict moves out of ROOT_DIR
        if self.is_moving_out_of_root(src_path, dest_path):
            print(f"WARNING: Moving files or folders out of {ROOT_DIR} is not allowed!")
            self.undo_move_operation(dest_path)
            self.show_warning_popup("Move operation not allowed!")

    def is_moving_out_of_root(self, src_path, dest_path):
        """Check if the move is from ROOT_DIR to outside."""
        if os.path.splitdrive(src_path)[0] != os.path.splitdrive(ROOT_DIR)[0]:
            return False  # Not on the same drive, so not moving out of ROOT_DIR
        return (
            os.path.commonpath([src_path, ROOT_DIR]) == ROOT_DIR
            and os.path.commonpath([dest_path, ROOT_DIR]) != ROOT_DIR
        )

    def undo_move_operation(self, path):
        """Undo a move operation by deleting the moved content."""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)  # Delete the entire directory
                print(f"Moved directory deleted: {path}")
            elif os.path.isfile(path):
                os.remove(path)  # Delete the file
                print(f"Moved file deleted: {path}")
        except Exception as e:
            print(f"Error undoing move operation {path}: {e}")

    def show_warning_popup(self, message):
        """Show a warning popup to the user."""
        ctypes.windll.user32.MessageBoxW(
            None,
            f"{message}\nFiles or folders from {ROOT_DIR} and its subdirectories cannot be moved outside the root directory.",
            "Operation Not Allowed",
            0x30  # MB_ICONWARNING
        )

    def on_created(self, event):
        if not event.is_directory:
            self.handle_file_operation(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.handle_file_operation(event.src_path)

    def handle_file_operation(self, src_path):
        """Monitor file operations."""
        print(f"File operation detected: {src_path}")
        
        # Check if the drive of src_path matches ROOT_DIR
        if os.path.splitdrive(src_path)[0] == os.path.splitdrive(ROOT_DIR)[0]:
            if os.path.commonpath([src_path, ROOT_DIR]) == ROOT_DIR:
                print(f"File operation within root directory: {src_path}")
            else:
                print(f"File operation outside root directory: {src_path}")
                self.check_pasted_file(src_path)
        else:
            print(f"File operation on a different drive: {src_path}")

    def check_pasted_file(self, src_path):
        """Check if the pasted file is from ROOT_DIR and delete it if necessary."""
        if (
            os.path.splitdrive(src_path)[0] == os.path.splitdrive(ROOT_DIR)[0]
            and os.path.commonpath([src_path, ROOT_DIR]) != ROOT_DIR
            and self.is_file_from_root(src_path)
        ):
            print(f"File pasted outside ROOT_DIR: {src_path}")
            print(f"Deleting the pasted file: {src_path}")
            try:
                os.remove(src_path)  # Delete the file
                print(f"File deleted successfully: {src_path}")
            except Exception as e:
                print(f"Error deleting file {src_path}: {e}")

    def is_file_from_root(self, file_path):
        """Check if the file is from ROOT_DIR."""
        try:
            # Check if the file exists in ROOT_DIR by matching the filename
            for root, dirs, files in os.walk(ROOT_DIR):
                if os.path.basename(file_path) in files or os.path.basename(file_path) in dirs:
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
                    if os.path.splitdrive(current_clipboard)[0] == os.path.splitdrive(ROOT_DIR)[0]:
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
    """Monitor directories for file modifications or creations."""
    event_handler = FileHandler()
    observer = Observer()
    
    for drive in MONITORED_DRIVES:
        observer.schedule(event_handler, path=drive, recursive=True)
    
    observer.start()

    try:
        # Run clipboard monitoring alongside directory monitoring
        monitor_clipboard()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    print("Monitoring file operations and clipboard across multiple drives...")
    monitor_directory()

if __name__ == "__main__":
    main()
