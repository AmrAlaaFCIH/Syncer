# Movie Syncer

Movie Syncer is a resilient, event-driven media synchronizer designed for long-distance movie nights. It uses a Master/Follower architecture to control local VLC Media Players across different computers, ensuring perfectly synchronized playback even on slow or unstable connections.

## Features
- **Zero Configuration**: A standalone executable that automatically discovers VLC and configures it via a hidden HTTP interface.
- **Resilient to Drops**: If a connection drops, playback continues locally. Upon reconnection, the Follower instantly syncs to the Master's exact state.
- **Event-Driven**: Uses minimal bandwidth. Network messages are only sent when an action (Play, Pause, Seek) occurs.
- **Flexible Server Hosting**: A lightweight Node.js WebSocket relay server that can be easily hosted 24/7 via Docker on AWS EC2, or other VPS providers.

## Architecture
The project is split into two main components:
- [**Client App (Python)**](./client/): A standalone executable that runs on the user's PC, connects to the WebSocket relay, and commands the local VLC player.
- [**Relay Server (Node.js)**](./server/): A lightweight WebSocket relay server that routes state changes from the Master client to the Follower client.

## Getting Started

### 1. Server Deployment
Please refer to the [Server README](./server/README.md) for detailed instructions on how to deploy the WebSocket relay server using Docker (ideal for AWS EC2).

### 2. Client Setup
You will need to configure and distribute the client to both users (Master and Follower).

1. Ensure the `config.json` file in the client folder is properly set up:
   - **Master's `config.json`**: `"role": "master"`
   - **Follower's `config.json`**: `"role": "follower"`
   - Set `"server_url"` to your live server's WebSocket address (e.g., `"ws://YOUR_SERVER_IP:8080"`).
2. Run the `movie-syncer.exe` application.
3. Select your local video file when prompted. VLC will open automatically and pause.
4. When the Master hits "Play" in VLC, the Follower's VLC will instantly synchronize and begin playback!
