# Movie Syncer - Python Client

This is the standalone Python client for **Movie Syncer**. It communicates with the local VLC Media Player via its hidden HTTP interface and connects to the WebSocket Relay Server to synchronize playback state with other clients.

## Features
- **Zero Configuration Setup**: Automatically discovers VLC installed on standard Windows paths or prompts the user.
- **Background VLC Execution**: Launches VLC silently in the background with the correct configuration flags.
- **Event-Driven Sync**: Monitors VLC playback and only broadcasts changes (Play, Pause, Seek).
- **Standalone Executable**: Can be compiled into a single `.exe` file for easy distribution.

## Setup & Compilation

### Requirements
- Python 3.10+
- `websockets`
- `requests`
- `pyinstaller` (for building the `.exe`)

### Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the client:
   ```bash
   python sync_engine.py
   ```

### Building the Executable
To build a standalone `.exe` that can be shared without requiring Python to be installed:
```bash
python -m PyInstaller --onefile --name movie-syncer sync_engine.py
```
The resulting executable will be placed in the `dist/` directory.

## Configuration
The client requires a `config.json` file in the same directory as the executable (or script). 

**Example `config.json` (Master)**:
```json
{
    "role": "master",
    "server_url": "ws://localhost:8080",
    "vlc_path": "",
    "vlc_http_port": 8081,
    "vlc_http_password": "secret_password"
}
```

**Example `config.json` (Follower)**:
```json
{
    "role": "follower",
    "server_url": "ws://localhost:8080",
    "vlc_path": "",
    "vlc_http_port": 8082,
    "vlc_http_password": "secret_password"
}
```