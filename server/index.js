const WebSocket = require('ws');

const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

let masterWs = null;
let followerWs = null;

wss.on('connection', (ws) => {
    console.log('A client connected.');

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);

            // Handle client registration
            if (data.type === 'register') {
                if (data.role === 'master') {
                    console.log('Master client registered.');
                    masterWs = ws;
                    ws.role = 'master';
                } else if (data.role === 'follower') {
                    console.log('Follower client registered.');
                    followerWs = ws;
                    ws.role = 'follower';
                }
                return;
            }

            // Handle sync events (only broadcast if they come from the master)
            if (ws.role === 'master' && data.type === 'sync') {
                if (followerWs && followerWs.readyState === WebSocket.OPEN) {
                    followerWs.send(JSON.stringify(data.payload));
                }
            }
            
            // Keep-alive ping from client
            if (data.type === 'ping') {
                ws.send(JSON.stringify({ type: 'pong' }));
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });

    ws.on('close', () => {
        if (ws.role === 'master') {
            masterWs = null;
            console.log('Master disconnected.');
        } else if (ws.role === 'follower') {
            followerWs = null;
            console.log('Follower disconnected.');
        } else {
            console.log('Unregistered client disconnected.');
        }
    });
});

console.log(`WebSocket Relay Server running on port ${port}`);
