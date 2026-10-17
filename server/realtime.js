// server/realtime.js
// CricHeroes-Compatible MQTT & WebSocket Realtime Bridge for TallyPitch
// Supports Paho MQTT 3.1.1 over WebSockets (ports 1884/8884/4000), JSON pub/sub,
// and OBS lower-third live broadcasting.

let WebSocketServer, WebSocket;
try {
  const wsPkg = require('ws');
  WebSocketServer = wsPkg.WebSocketServer;
  WebSocket = wsPkg.WebSocket;
} catch (_) {
  // Graceful fallback when node_modules is not yet installed
  WebSocket = { OPEN: 1, CLOSED: 3 };
  WebSocketServer = class FallbackWebSocketServer {
    constructor() { this.clients = new Set(); }
    on() { return this; }
    close() {}
  };
}

// All active WebSocket clients
const allClients = new Set();

// In-memory match subscription registry (legacy /ws/live?matchId=... compatibility)
const matchSubscribers = new Map();

// Helper: variable length remaining length encoding (MQTT 3.1.1 spec)
function encodeRemainingLength(length) {
  const bytes = [];
  do {
    let digit = length % 128;
    length = Math.floor(length / 128);
    if (length > 0) digit |= 128;
    bytes.push(digit);
  } while (length > 0);
  return Buffer.from(bytes);
}

// Helper: variable length remaining length decoding
function decodeRemainingLength(buf, offset = 1) {
  let multiplier = 1;
  let value = 0;
  let bytesRead = 0;
  let digit;
  do {
    if (offset + bytesRead >= buf.length) {
      throw new Error('Malformed Remaining Length');
    }
    digit = buf[offset + bytesRead];
    value += (digit & 127) * multiplier;
    multiplier *= 128;
    bytesRead++;
    if (bytesRead > 4) throw new Error('Remaining Length exceeded 4 bytes');
  } while ((digit & 128) !== 0);
  return { length: value, bytesRead };
}

// Helper: MQTT topic filter matching with '+' and '#' wildcards
function matchesTopic(filter, topic) {
  if (filter === topic || filter === '#' || filter === '+') return true;
  const regexStr = '^' + filter
    .split('/')
    .map(part => {
      if (part === '+') return '[^/]+';
      if (part === '#') return '.*';
      return part.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
    })
    .join('/') + '$';
  return new RegExp(regexStr).test(topic);
}

/**
 * Encodes an MQTT 3.1.1 PUBLISH frame (QoS 0)
 * @param {string} topic
 * @param {string|Buffer|object} payload
 * @returns {Buffer}
 */
function encodeMqttPublish(topic, payload) {
  const topicBuf = Buffer.from(topic, 'utf8');
  let payloadBuf;
  if (Buffer.isBuffer(payload)) {
    payloadBuf = payload;
  } else if (typeof payload === 'string') {
    payloadBuf = Buffer.from(payload, 'utf8');
  } else {
    payloadBuf = Buffer.from(JSON.stringify(payload), 'utf8');
  }

  const remainingLength = 2 + topicBuf.length + payloadBuf.length;
  const remLenBuf = encodeRemainingLength(remainingLength);
  const headerBuf = Buffer.from([0x30]); // PUBLISH QoS 0
  const topicLenBuf = Buffer.alloc(2);
  topicLenBuf.writeUInt16BE(topicBuf.length, 0);

  return Buffer.concat([headerBuf, remLenBuf, topicLenBuf, topicBuf, payloadBuf]);
}

/**
 * Decodes an MQTT packet from a binary buffer
 * @param {Buffer} buf
 * @returns {object|null}
 */
function decodeMqttPacket(buf) {
  if (!buf || buf.length < 2) return null;
  const firstByte = buf[0];
  const packetType = (firstByte >> 4) & 0x0f;

  try {
    const { length: remainingLength, bytesRead } = decodeRemainingLength(buf, 1);
    const variableHeaderOffset = 1 + bytesRead;

    switch (packetType) {
      case 0x01: { // 1 = CONNECT (0x10)
        let offset = variableHeaderOffset;
        const protoLen = buf.readUInt16BE(offset);
        offset += 2;
        const protoName = buf.toString('utf8', offset, offset + protoLen);
        offset += protoLen;
        const protoLevel = buf[offset++];
        const connectFlags = buf[offset++];
        const keepAlive = buf.readUInt16BE(offset);
        offset += 2;
        let clientId = '';
        if (offset < buf.length) {
          const clientLen = buf.readUInt16BE(offset);
          offset += 2;
          clientId = buf.toString('utf8', offset, offset + clientLen);
        }
        return {
          type: 'CONNECT',
          protoName,
          protoLevel,
          connectFlags,
          keepAlive,
          clientId,
        };
      }
      case 0x03: { // 3 = PUBLISH (0x30 / 0x32)
        const qos = (firstByte >> 1) & 0x03;
        let offset = variableHeaderOffset;
        const topicLen = buf.readUInt16BE(offset);
        offset += 2;
        const topic = buf.toString('utf8', offset, offset + topicLen);
        offset += topicLen;
        let packetId = null;
        if (qos > 0) {
          packetId = buf.readUInt16BE(offset);
          offset += 2;
        }
        const payloadBuf = buf.slice(offset, variableHeaderOffset + remainingLength);
        let payload = payloadBuf.toString('utf8');
        try {
          payload = JSON.parse(payload);
        } catch (_) {}
        return {
          type: 'PUBLISH',
          qos,
          topic,
          packetId,
          payload,
        };
      }
      case 0x08: { // 8 = SUBSCRIBE (0x82)
        let offset = variableHeaderOffset;
        const packetId = buf.readUInt16BE(offset);
        offset += 2;
        const subscriptions = [];
        while (offset < variableHeaderOffset + remainingLength) {
          const topicLen = buf.readUInt16BE(offset);
          offset += 2;
          const topic = buf.toString('utf8', offset, offset + topicLen);
          offset += topicLen;
          const qos = buf[offset++];
          subscriptions.push({ topic, qos });
        }
        return {
          type: 'SUBSCRIBE',
          packetId,
          subscriptions,
        };
      }
      case 0x0C: { // 12 = PINGREQ (0xC0)
        return { type: 'PINGREQ' };
      }
      case 0x0E: { // 14 = DISCONNECT (0xE0)
        return { type: 'DISCONNECT' };
      }
      default:
        return { type: 'UNKNOWN', packetType };
    }
  } catch (err) {
    return { type: 'ERROR', error: err.message };
  }
}

/**
 * Publishes a message to a specific topic across all subscribed MQTT & JSON clients
 * @param {string} topic
 * @param {object|string} payload
 */
function publishToTopic(topic, payload) {
  const jsonPayload = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const jsonMessage = JSON.stringify({
    topic,
    payload: typeof payload === 'string' ? payload : payload,
    timestamp: new Date().toISOString(),
  });

  let mqttPublishBuffer = null;

  for (const client of allClients) {
    if (client.readyState !== WebSocket.OPEN) continue;

    // Check if client is subscribed to this topic
    let isSubscribed = false;
    if (client.subscriptions) {
      for (const filter of client.subscriptions) {
        if (matchesTopic(filter, topic)) {
          isSubscribed = true;
          break;
        }
      }
    }

    if (isSubscribed) {
      if (client.isMqtt) {
        if (!mqttPublishBuffer) {
          mqttPublishBuffer = encodeMqttPublish(topic, jsonPayload);
        }
        client.send(mqttPublishBuffer);
      } else {
        client.send(jsonMessage);
      }
    }
  }
}

/**
 * Broadcasts CricHeroes-compatible match events across score, ball, and overlay topics
 * @param {string|number} matchId
 * @param {object} eventData
 */
function broadcastCricHeroesMatch(matchId, eventData) {
  const idStr = String(matchId);

  // 1. Ball event topic (cricheroes/matches/{match_id}/ball)
  if (eventData.ball) {
    publishToTopic(`cricheroes/matches/${idStr}/ball`, eventData.ball);
    publishToTopic(`tallypitch/matches/${idStr}/ball`, eventData.ball);
  }

  // 2. Live score summary topic (cricheroes/matches/{match_id}/score)
  if (eventData.score) {
    publishToTopic(`cricheroes/matches/${idStr}/score`, eventData.score);
    publishToTopic(`tallypitch/matches/${idStr}/score`, eventData.score);
  }

  // 3. OBS lower-third overlay topic (cricheroes/matches/{match_id}/overlay)
  if (eventData.overlay) {
    publishToTopic(`cricheroes/matches/${idStr}/overlay`, eventData.overlay);
    publishToTopic(`tallypitch/matches/${idStr}/overlay`, eventData.overlay);
  }
}

/**
 * Legacy broadcast helper for existing API routes
 * @param {string} matchId
 * @param {object} payload
 */
function broadcastMatchEvent(matchId, payload) {
  const idStr = String(matchId);

  // 1. Send to legacy matchSubscribers
  const legacySubscribers = matchSubscribers.get(idStr);
  if (legacySubscribers && legacySubscribers.size > 0) {
    const message = JSON.stringify({
      matchId: idStr,
      timestamp: new Date().toISOString(),
      ...payload,
    });
    for (const client of legacySubscribers) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    }
  }

  // 2. Synthesize CricHeroes topics if payload contains cricket details
  const ballData = payload.delivery ? {
    match_id: idStr,
    inning: payload.delivery.inning || 1,
    over: payload.delivery.over_id || payload.delivery.overNum || 0,
    ball: payload.delivery.ball_number || payload.delivery.ballInOver || 0,
    legal_ball_number: payload.delivery.delivery_seq || payload.delivery.legalBallCount || 0,
    striker_id: payload.delivery.striker_player_id || payload.delivery.strikerId || null,
    non_striker_id: payload.delivery.non_striker_player_id || payload.delivery.nonStrikerId || null,
    bowler_id: payload.delivery.bowler_player_id || payload.delivery.bowlerId || null,
    runs_scored: payload.runs !== undefined ? payload.runs : (payload.delivery.runs_scored || 0),
    extra_type: payload.delivery.extra_type || (payload.isExtra ? 'extra' : 'none'),
    extra_runs: payload.delivery.extra_runs || 0,
    is_boundary: (payload.runs === 4 || payload.runs === 6),
    boundary_type: (payload.runs === 4 || payload.runs === 6) ? payload.runs : 0,
    is_wicket: Boolean(payload.isWicket),
    total_score: payload.totalScore || 0,
    total_wickets: payload.totalWickets || 0,
    run_rate: payload.runRate || '0.00',
    wagon_wheel: payload.wagonWheel || {
      zone: payload.delivery.shot_zone || 4,
      angle_degrees: 154,
      distance_pct: 100,
    },
  } : null;

  const scoreData = {
    match_id: idStr,
    type: payload.type || 'SCORE_UPDATE',
    runs: payload.runs || 0,
    total_score: payload.totalScore || 0,
    total_wickets: payload.totalWickets || 0,
    overs: payload.overs || '0.0',
    run_rate: payload.runRate || '0.00',
  };

  const overlayData = {
    match_id: idStr,
    headline: payload.headline || `Match ${idStr} Live Update`,
    runs: payload.totalScore || 0,
    wickets: payload.totalWickets || 0,
    overs: payload.overs || '0.0',
    last_event: payload.type === 'DELIVERY_RECORDED'
      ? `${payload.runs || 0} runs${payload.isWicket ? ' • WICKET!' : ''}`
      : (payload.type || 'LIVE'),
  };

  broadcastCricHeroesMatch(idStr, {
    ball: ballData,
    score: scoreData,
    overlay: overlayData,
  });
}

/**
 * Initializes the WebSocket server attached to the HTTP server
 * @param {http.Server} server - Node.js HTTP server instance
 */
function setupRealtimeServer(server) {
  const wss = new WebSocketServer({
    server,
    handleProtocols: (protocols) => {
      // Support Paho MQTT over WebSocket subprotocols ('mqtt', 'mqttv3.1')
      if (protocols.has('mqtt') || protocols.has('mqttv3.1')) {
        return 'mqtt';
      }
      return false;
    },
  });

  wss.on('connection', (ws, req) => {
    allClients.add(ws);
    ws.subscriptions = new Set();
    ws.isMqtt = false;

    // Check negotiated subprotocol
    if (ws.protocol === 'mqtt' || ws.protocol === 'mqttv3.1') {
      ws.isMqtt = true;
    }

    const host = req.headers.host || 'localhost';
    const parsedUrl = new URL(req.url, `http://${host}`);
    const matchId = parsedUrl.searchParams.get('matchId');

    // If connected with ?matchId=..., subscribe to match topics automatically
    if (matchId) {
      if (!matchSubscribers.has(matchId)) {
        matchSubscribers.set(matchId, new Set());
      }
      matchSubscribers.get(matchId).add(ws);

      ws.subscriptions.add(`cricheroes/matches/${matchId}/#`);
      ws.subscriptions.add(`tallypitch/matches/${matchId}/#`);

      // Connection ACK for legacy JSON clients
      if (!ws.isMqtt) {
        ws.send(JSON.stringify({
          type: 'CONNECTED',
          matchId,
          timestamp: new Date().toISOString(),
          message: `Subscribed to live match updates for ${matchId}`,
          supportedTopics: [
            `cricheroes/matches/${matchId}/score`,
            `cricheroes/matches/${matchId}/ball`,
            `cricheroes/matches/${matchId}/overlay`,
          ],
        }));
      }
    }

    ws.on('message', (message, isBinary) => {
      // 1. Binary Packet (MQTT 3.1.1 protocol)
      if (isBinary || Buffer.isBuffer(message)) {
        const buf = Buffer.isBuffer(message) ? message : Buffer.from(message);
        const packet = decodeMqttPacket(buf);
        if (!packet) return;

        switch (packet.type) {
          case 'CONNECT': {
            ws.isMqtt = true;
            // Send CONNACK: [0x20, 0x02, sessionPresent=0, returnCode=0 (Accepted)]
            ws.send(Buffer.from([0x20, 0x02, 0x00, 0x00]));
            break;
          }
          case 'SUBSCRIBE': {
            const grantedQos = [];
            for (const sub of packet.subscriptions) {
              ws.subscriptions.add(sub.topic);
              grantedQos.push(sub.qos || 0);
            }
            // Send SUBACK: [0x90, len, packetIdMSB, packetIdLSB, ...grantedQos]
            const pktId = packet.packetId || 1;
            const suback = Buffer.from([
              0x90,
              2 + grantedQos.length,
              (pktId >> 8) & 0xff,
              pktId & 0xff,
              ...grantedQos,
            ]);
            ws.send(suback);
            break;
          }
          case 'PUBLISH': {
            if (packet.topic) {
              publishToTopic(packet.topic, packet.payload);
            }
            // Send PUBACK if QoS 1
            if (packet.qos === 1 && packet.packetId) {
              ws.send(Buffer.from([0x40, 0x02, (packet.packetId >> 8) & 0xff, packet.packetId & 0xff]));
            }
            break;
          }
          case 'PINGREQ': {
            // Send PINGRESP: [0xD0, 0x00]
            ws.send(Buffer.from([0xD0, 0x00]));
            break;
          }
          case 'DISCONNECT': {
            ws.close();
            break;
          }
        }
        return;
      }

      // 2. Text Message (JSON Pub/Sub or commands)
      try {
        const text = message.toString();
        const data = JSON.parse(text);

        // Subscribe action
        if (data.type === 'SUBSCRIBE' || data.action === 'subscribe') {
          const topic = data.topic;
          if (topic) {
            ws.subscriptions.add(topic);
            ws.send(JSON.stringify({ type: 'SUBACK', topic, status: 'ok' }));
          }
        }
        // Unsubscribe action
        else if (data.type === 'UNSUBSCRIBE' || data.action === 'unsubscribe') {
          const topic = data.topic;
          if (topic) {
            ws.subscriptions.delete(topic);
            ws.send(JSON.stringify({ type: 'UNSUBACK', topic, status: 'ok' }));
          }
        }
        // Publish action
        else if (data.type === 'PUBLISH' || data.action === 'publish') {
          if (data.topic && data.payload) {
            publishToTopic(data.topic, data.payload);
          }
        }
        // Match subscription
        else if (data.matchId) {
          const mId = String(data.matchId);
          if (!matchSubscribers.has(mId)) {
            matchSubscribers.set(mId, new Set());
          }
          matchSubscribers.get(mId).add(ws);
          ws.subscriptions.add(`cricheroes/matches/${mId}/#`);
          ws.send(JSON.stringify({ type: 'SUBSCRIBED', matchId: mId }));
        }
      } catch (err) {
        // Non-JSON plain text ping
        if (message.toString().trim().toLowerCase() === 'ping') {
          ws.send('pong');
        }
      }
    });

    ws.on('close', () => {
      allClients.delete(ws);
      if (matchId && matchSubscribers.has(matchId)) {
        const subs = matchSubscribers.get(matchId);
        subs.delete(ws);
        if (subs.size === 0) {
          matchSubscribers.delete(matchId);
        }
      }
    });

    ws.on('error', (err) => {
      console.error('WebSocket client error:', err);
    });
  });

  return wss;
}

module.exports = {
  setupRealtimeServer,
  broadcastMatchEvent,
  broadcastCricHeroesMatch,
  publishToTopic,
  encodeMqttPublish,
  decodeMqttPacket,
  matchesTopic,
};
