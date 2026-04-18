import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "role": "follower",
    "server_url": "ws://localhost:8080",
    "vlc_path": "",
    "vlc_http_port": 8081,
    "vlc_http_password": "secret_password"
}

def discover_vlc():
    """Tries to find VLC in standard Windows paths."""
    standard_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    ]
    for path in standard_paths:
        if os.path.exists(path):
            return path
    return None

def prompt_for_vlc():
    """Prompts the user to locate vlc.exe using a file dialog."""
    root = tk.Tk()
    root.withdraw() # Hide the main window
    
    messagebox.showinfo(
        "VLC Not Found", 
        "Could not automatically find VLC Media Player. Please locate your 'vlc.exe' file in the next dialog."
    )
    
    file_path = filedialog.askopenfilename(
        title="Select vlc.exe",
        filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
    )
    
    if file_path and os.path.basename(file_path).lower() == 'vlc.exe':
        return file_path
        
    messagebox.showerror("Error", "A valid vlc.exe was not selected. The app will now exit.")
    return None

def load_config():
    """Loads config.json, auto-discovers VLC if needed, and ensures it is valid."""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            print(f"Error reading config: {e}")
            
    # Check if VLC path is valid
    if not config.get('vlc_path') or not os.path.exists(config['vlc_path']):
        print("VLC path is empty or invalid. Attempting auto-discovery...")
        vlc_path = discover_vlc()
        
        if not vlc_path:
            vlc_path = prompt_for_vlc()
            
        if not vlc_path:
            # Cannot proceed without VLC
            raise RuntimeError("VLC Media Player is required to run this app.")
            
        config['vlc_path'] = vlc_path
        
        # Save updated config back to file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
            print(f"Config updated and saved with VLC path: {vlc_path}")
            
    return config

if __name__ == "__main__":
    c = load_config()
    print("Loaded Config:", c)
