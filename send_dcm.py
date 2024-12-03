import os
from scp import SCPClient
import paramiko
from tkinter import Tk, filedialog

def select_folder():
    """
    Opens a folder selection dialog and returns the selected folder path.
    """
    Tk().withdraw()  # Hide the main tkinter window
    folder_path = filedialog.askdirectory()  # Open folder dialog
    if folder_path:
        print(f"Selected folder: {folder_path}")
        return folder_path
    else:
        print("No folder selected. Exiting.")
        exit()

def send_folder_via_scp(folder_path, hostname, username, remote_base_path):
    """
    Sends all files in a folder (including subdirectories) to a remote server via SCP.

    :param folder_path: Path to the folder to be sent.
    :param hostname: Remote server IP or hostname.
    :param username: Username for the remote server.
    :param remote_base_path: Base destination path on the remote server.
    """
    try:
        # SSH client setup
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        print(f"Connecting to {hostname} as {username}...")
        ssh.connect(hostname=hostname, username=username)

        # SCP client setup
        with SCPClient(ssh.get_transport()) as scp:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    
                    # Calculate the relative path from the selected folder, including the base folder (e.g., 30002456)
                    relative_path = os.path.relpath(local_file_path, os.path.dirname(folder_path))
                    remote_file_path = os.path.join(remote_base_path, relative_path).replace("\\", "/")
                    remote_dir = os.path.dirname(remote_file_path)
                    
                    # Create remote directory if it doesn't exist
                    ssh.exec_command(f"mkdir -p {remote_dir}")
                    
                    # Send file
                    print(f"Sending file: {local_file_path} -> {remote_file_path}")
                    scp.put(local_file_path, remote_file_path)
                    
            print("All files have been successfully sent!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    # Remote server details
    SERVER_IP = "125.132.155.155"  # Remote server IP address
    USERNAME = "user"  # Remote server username
    REMOTE_BASE_PATH = "/home/user/DHKIM/Materials_DICOM/dcm"  # Remote server base target path

    # Step 1: Select a folder to send
    local_folder = select_folder()

    # Step 2: Send the selected folder
    send_folder_via_scp(local_folder, SERVER_IP, USERNAME, REMOTE_BASE_PATH)
