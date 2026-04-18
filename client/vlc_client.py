import subprocess
import requests
import xml.etree.ElementTree as ET
import time
import tkinter as tk
from tkinter import filedialog
import os

class VLCClient:
    def __init__(self, vlc_path, port=8080, password="secret_password"):
        self.vlc_path = vlc_path
        self.port = port
        self.password = password
        self.process = None
        self.base_url = f"http://localhost:{self.port}/requests/status.xml"

    def select_movie(self):
        """Prompts the user to select a movie file."""
        root = tk.Tk()
        root.withdraw() # Hide the main window
        
        from tkinter import messagebox
        messagebox.showinfo(
            "Select Movie", 
            "Please select the video file you want to watch. VLC will open it automatically."
        )
        
        file_path = filedialog.askopenfilename(
            title="Select the Movie File to Sync",
            filetypes=[("Video Files", "*.mkv *.mp4 *.avi *.mov *.wmv *.webm"), ("All Files", "*.*")]
        )
        return file_path

    def launch(self):
        """Launches VLC with the selected movie and HTTP interface enabled."""
        movie_path = self.select_movie()
        if not movie_path:
            print("No movie selected.")
            return False

        # Normalize the path for Windows (change / to \) to ensure VLC reads it correctly
        movie_path = os.path.normpath(movie_path)

        # The core logic to force VLC to open the web interface
        cmd = [
            self.vlc_path,
            "--extraintf=http",
            f"--http-port={self.port}",
            f"--http-password={self.password}",
            "--start-paused", # Always start paused for safety
            f"file:///{movie_path.replace(chr(92), '/')}" # Ensure it is passed as a valid URI to avoid parsing bugs
        ]

        print(f"Launching VLC for '{os.path.basename(movie_path)}'...")
        # Use Popen to launch VLC as an independent background process
        self.process = subprocess.Popen(cmd)
        
        # Give VLC a couple of seconds to bind to the HTTP port
        time.sleep(2)
        return True

    def get_status(self):
        """Polls VLC for current playback state and time."""
        try:
            # VLC HTTP interface expects Basic Auth with an empty username and the config password
            response = requests.get(self.base_url, auth=('', self.password), timeout=1)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            state = root.find('state').text if root.find('state') is not None else 'unknown'
            time_val = int(root.find('time').text) if root.find('time') is not None else 0
            
            return {
                "state": state, # typically 'playing' or 'paused'
                "time": time_val
            }
        except requests.exceptions.RequestException:
            # Connection failed, VLC is likely closed or still starting up
            return None
        except Exception as e:
            print(f"Error parsing VLC status: {e}")
            return None

    def command(self, action, val=None):
        """Sends a command to the VLC HTTP interface."""
        params = {"command": action}
        if val is not None:
            params["val"] = val
            
        try:
            requests.get(self.base_url, params=params, auth=('', self.password), timeout=1)
        except Exception as e:
            print(f"Failed to send command {action} to VLC: {e}")

    def play(self):
        self.command("pl_forceresume")
        
    def pause(self):
        self.command("pl_forcepause")
        
    def seek(self, seconds):
        # VLC accepts seek time in integer seconds
        self.command("seek", str(int(seconds)))
