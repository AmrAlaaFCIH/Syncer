import asyncio
import websockets
import json
from config_loader import load_config
from vlc_client import VLCClient

class SyncEngine:
    def __init__(self):
        self.config = load_config()
        self.vlc = VLCClient(
            self.config['vlc_path'], 
            self.config.get('vlc_http_port', 8080), 
            self.config.get('vlc_http_password', 'secret_password')
        )
        self.role = self.config['role'].lower()
        self.server_url = self.config['server_url']
        self.ws = None
        self.last_state = None
        
        # Margin of error in seconds before forcing a seek
        self.sync_threshold = 2
        
    async def connect_websocket(self):
        """Maintains a persistent connection to the WebSocket server."""
        while True:
            try:
                print(f"Connecting to Relay Server: {self.server_url} as {self.role.upper()}...")
                async with websockets.connect(self.server_url) as ws:
                    self.ws = ws
                    print("Connected to server successfully.")
                    
                    # Register role with the relay
                    await ws.send(json.dumps({"type": "register", "role": self.role}))
                    
                    # Resilience: If Master reconnects after dropping out, immediately broadcast current state
                    if self.role == 'master' and self.last_state:
                        await self.broadcast_sync()

                    # Listen for incoming sync messages (Follower)
                    async for message in ws:
                        await self.handle_message(message)
                        
            except Exception as e:
                print(f"WebSocket disconnected. Retrying in 3 seconds... ({e})")
                self.ws = None
                await asyncio.sleep(3)

    async def handle_message(self, message):
        """Processes sync events received from the Master."""
        if self.role != 'follower':
            return
            
        try:
            # We assume messages coming from relay are the raw payload from the Master
            payload = json.loads(message)
            master_state = payload.get('state')
            master_time = payload.get('time')
            
            print(f"Received sync event -> Master is {master_state} at {master_time}s")
            
            current_status = self.vlc.get_status()
            if current_status:
                # Seek if time has drifted too far apart
                if abs(current_status['time'] - master_time) > self.sync_threshold:
                    print(f"Drift detected. Seeking to {master_time}s")
                    self.vlc.seek(master_time)
                    
                # Match Play/Pause
                if master_state == 'playing' and current_status['state'] != 'playing':
                    print("Master started playing. Resuming local playback.")
                    self.vlc.play()
                elif master_state == 'paused' and current_status['state'] != 'paused':
                    print("Master paused. Pausing local playback.")
                    self.vlc.pause()
                    # Resync time exactly on pause for accuracy
                    self.vlc.seek(master_time) 
        except Exception as e:
            print(f"Error applying sync event: {e}")

    async def broadcast_sync(self):
        """Sends the current VLC state to the Follower via the Relay."""
        if not self.ws or self.role != 'master' or not self.last_state:
            return
            
        payload = {
            "type": "sync",
            "payload": {
                "state": self.last_state['state'],
                "time": self.last_state['time']
            }
        }
        try:
            await self.ws.send(json.dumps(payload))
            print(f"Broadcasted: {self.last_state['state']} at {self.last_state['time']}s")
        except Exception as e:
            print(f"Failed to broadcast update: {e}")

    async def poll_vlc(self):
        """Constantly checks local VLC to detect Play/Pause/Seek actions."""
        while True:
            try:
                status = self.vlc.get_status()
                
                if status and self.role == 'master':
                    if not self.last_state:
                        # First time getting status
                        self.last_state = status
                        await self.broadcast_sync()
                    else:
                        state_changed = status['state'] != self.last_state['state']
                        
                        # Calculate time drift to detect a manual seek
                        # Polling every 0.5s, time shouldn't move more than 1-2 seconds.
                        time_diff = status['time'] - self.last_state['time']
                        seek_detected = time_diff > 2 or time_diff < 0
                        
                        # Update our last known state
                        self.last_state = status
                        
                        if state_changed or seek_detected:
                            await self.broadcast_sync()

            except Exception as e:
                pass # Silently handle VLC polling errors
                
            # Check every half second
            await asyncio.sleep(0.5)

    async def run(self):
        """Bootstraps the client application."""
        if not self.vlc.launch():
            return
            
        print(f"--- Starting Sync Engine as {self.role.upper()} ---")
        
        # Explicitly force a pause at startup just to be absolutely sure
        self.vlc.pause()
        
        # Run WebSocket listener and VLC poller concurrently
        await asyncio.gather(
            self.connect_websocket(),
            self.poll_vlc()
        )

if __name__ == "__main__":
    engine = SyncEngine()
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        print("Movie Syncer exited.")