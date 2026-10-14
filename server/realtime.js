// server/realtime.js
// WebSocket Live Score Broadcasting & OBS Overlay Sync for CricHeroes Replica

const http = require('http');
const { WebSocketServer, WebSocket } = require('ws');

// In-memory match subscription registry: matchId -> Set of WebSockets
const matchSubscribers = new Map();

/**
 * Initializes the WebSocket server attached to the HTTP server
 * @param {http.Server} server - Node.js HTTP server instance
 */
function setupRealtimeServer(server) {
  const wss = new WebSocketServer({ server, path: '/ws/live' });

  wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const matchId = url.searchParams.get('matchId');

    if (!matchId) {
      ws.close(1008, 'Missing matchId query parameter');
      return;
    }

    if (!matchSubscribers.has(matchId)) {
      matchSubscribers.set(matchId, new Set());
    }
    matchSubscribers.get(matchId).add(ws);

    // Send connection ACK
    ws.send(JSON.stringify({
      type: 'CONNECTED',
      matchId,
      timestamp: new Date().toISOString(),
      message: `Subscribed to live match updates for ${matchId}`,
    }));

    ws.on('close', () => {
      const subscribers = matchSubscribers.get(matchId);
      if (subscribers) {
        subscribers.delete(ws);
        if (subscribers.size === 0) {
          matchSubscribers.delete(matchId);
        }
      }
    });

    ws.on('error', (err) => {
      console.error(`WebSocket error for match ${matchId}:`, err);
    });
  });

  return wss;
}

/**
 * Broadcasts a live match event (ball bowled, wicket, boundary, over complete)
 * to all connected browser scorecards and OBS lower-third overlays
 * @param {string} matchId - UUID of the match
 * @param {object} payload - Event data (runs, totalScore, delivery, wickets, overs)
 */
function broadcastMatchEvent(matchId, payload) {
  const subscribers = matchSubscribers.get(matchId);
  if (!subscribers || subscribers.size === 0) return;

  const message = JSON.stringify({
    matchId,
    timestamp: new Date().toISOString(),
    ...payload,
  });

  for (const client of subscribers) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

module.exports = {
  setupRealtimeServer,
  broadcastMatchEvent,
};
