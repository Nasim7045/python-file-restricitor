READ BOTH THE PARTS OF THIS FILE IN ORDER TO UNDERSTAND THE WORKING OF THESE PROJECTS



File Operations Monitoring and Clipboard Handling
This Python script monitors file operations (copy-paste actions) and the clipboard in real time. It ensures that files copied from the ROOT_DIR (specified directory) and pasted outside this directory are automatically deleted. The script also allows copy-paste operations within the ROOT_DIR and its subdirectories, as well as from external locations into the ROOT_DIR.

Features:
Monitor Clipboard: Detects copy-paste actions involving file paths and prevents pasting of files copied from the ROOT_DIR to external locations.
Monitor File Operations: Tracks file modifications and creations within the ROOT_DIR and subdirectories.
Automatic Deletion: If a file copied from ROOT_DIR is pasted outside of it, the script automatically deletes the pasted file to enforce the restriction.
Requirements
Libraries to Install
Before running the script, you need to install the required libraries using pip. You can install them using the following commands:

bash
Copy code
pip install watchdog pyperclip
watchdog: To monitor file system changes in real-time.
pyperclip: To monitor clipboard content for copy-paste operations.
Python Version
This script is compatible with Python 3.6 and above.

Configuration
Setting the Root Directory:

The directory you want to monitor and enforce restrictions on is set in the ROOT_DIR variable.
In the script, you’ll see this line:
python
Copy code
ROOT_DIR = r"D:\Projects"
Change this path to the directory you want to monitor. For example, if your project directory is on another drive, update the path accordingly:
python
Copy code
ROOT_DIR = r"C:\Users\YourUsername\Documents\MyProjects"
Monitoring the Entire Drive:

The script is designed to monitor the entire drive (e.g., D:\) to detect whether files are pasted outside the ROOT_DIR.
If you want to monitor a different drive or partition, simply change the ROOT_DIR path.
How to Run the Script
Step 1: Setup the Environment
Ensure Python is installed: Make sure you have Python installed on your machine (Python 3.6 or above).
Create a virtual environment (optional but recommended):
bash
Copy code
python -m venv venv
Activate the environment:
Windows:
bash
Copy code
venv\Scripts\activate
Step 2: Install Dependencies
After setting up your environment, install the required libraries:

bash
Copy code
pip install watchdog pyperclip
Step 3: Run the Script
To start monitoring the ROOT_DIR, run the script by executing the following command:

bash
Copy code
python mainpy.py
The script will begin monitoring the clipboard for file paths and track any file operations inside or outside the ROOT_DIR.

How It Works
Clipboard Monitoring:

The script continuously checks the clipboard for file paths. If the clipboard contains a valid file path, it verifies whether the path belongs to the ROOT_DIR.
If the file path is from the ROOT_DIR and is being pasted outside it, the script deletes the pasted file and clears the clipboard to prevent pasting.
If the file is from an external location and being pasted into the ROOT_DIR, the operation is allowed.
File Operation Monitoring:

The script uses watchdog to monitor file operations within the ROOT_DIR and subdirectories.
It logs file operations inside the ROOT_DIR and checks if files are pasted outside the directory. If so, the file is deleted.
Notes
Permissions: Ensure the script has the required permissions to monitor files and delete them. It needs access to the directories you’re monitoring and the permissions to delete files.
Clipboard Access: The script uses pyperclip to access the clipboard. Ensure that the clipboard contains valid paths (e.g., copied from a file explorer).
Deleting Files: The script deletes pasted files from external locations that originated from the ROOT_DIR. This operation is irreversible, so be cautious when running the script in production environments.
Troubleshooting
Error Deleting Files: If you see an error like File not found when attempting to delete a file, it may have been moved or already deleted by another process.
Permissions Issues: If the script can't access or delete files, ensure the script is running with sufficient permissions. You may need to run it as an administrator or modify the file/folder permissions.
Future Improvements
Logging: The script currently prints logs to the console. You could add logging functionality to store detailed logs for file operations and clipboard actions.
Custom Restrictions: Implement additional checks such as specific file types, file sizes, or user roles to allow/deny certain operations.
License
This project is open-source and free to use. Feel free to modify or contribute to it.

Conclusion
This script is a simple solution for monitoring file operations and enforcing restrictions on files copied from a specific directory. By checking the clipboard and monitoring file system events, it can ensure that files copied from the ROOT_DIR aren't inadvertently pasted outside the designated directory.
