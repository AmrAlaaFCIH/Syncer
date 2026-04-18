# Movie Syncer - WebSocket Relay Server

This is the lightweight Node.js WebSocket relay server for **Movie Syncer**, an app that synchronizes local VLC media players across different computers.

## How it works
This server acts as a "dumb relay". It does no video processing. 
1. The **Master** client connects and broadcasts its local VLC state (Play, Pause, Seek, Time).
2. The **Follower** client connects and listens.
3. The server forwards the exact state from the Master to the Follower, allowing the Follower to adjust its local VLC player to perfectly match the Master.

## Local Development
1. Install dependencies: `npm install`
2. Start the server: `npm start`
3. The server will run on `ws://localhost:8080` by default.

## Deployment (Docker / AWS EC2)
This server includes a `Dockerfile` for easy 24/7 deployment on any VPS, such as an AWS EC2 instance.

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/AmrAlaaFCIH/Syncer.git
   cd Syncer/server
   ```
2. **Build the Docker image:**
   ```bash
   docker build -t movie-syncer-server .
   ```
3. **Run the container (in the background):**
   ```bash
   docker run -d -p 8080:8080 --name movie-syncer-server movie-syncer-server
   ```
4. **Firewall (AWS EC2):** Ensure that port `8080` is open in your EC2 Security Group inbound rules.

Once deployed, update your Client App's `config.json` with your server's public IP address or domain:
`"server_url": "ws://YOUR_SERVER_IP:8080"`