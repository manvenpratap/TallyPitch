// server/api.js
// Node.js REST API & Cricket Rules State Machine Server for TallyPitch

const http = require('http');
const { parse } = require('url');
const { supabaseAdmin } = require('./db');
const { sendPhoneOTP, verifyPhoneOTP } = require('./auth');
const { setupRealtimeServer, broadcastMatchEvent } = require('./realtime');
const { createProCheckoutSession, handleStripeWebhook } = require('./stripe');

const PORT = process.env.PORT || 4000;

/**
 * Standard JSON response helper
 */
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  });
  res.end(JSON.stringify(data));
}

/**
 * Reads and parses JSON request body
 */
function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

/**
 * Main HTTP Request Router
 */
async function requestHandler(req, res) {
  const parsedUrl = parse(req.url, true);
  const { pathname, query } = parsedUrl;

  // Handle CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    });
    res.end();
    return;
  }

  try {
    // 1. Health Check
    if (req.method === 'GET' && pathname === '/api/health') {
      return sendJSON(res, 200, {
        status: 'ok',
        version: '1.0.0',
        uptime: process.uptime(),
        database: 'PostgreSQL (Supabase Ready)',
        realtime: 'Active',
      });
    }

    // 2. Auth: Send Phone OTP
    if (req.method === 'POST' && pathname === '/api/auth/otp/send') {
      const { phone } = await readBody(req);
      if (!phone) return sendJSON(res, 400, { error: 'Phone number is required' });
      await sendPhoneOTP(phone);
      return sendJSON(res, 200, { success: true, message: 'OTP sent to mobile' });
    }

    // 3. Auth: Verify Phone OTP
    if (req.method === 'POST' && pathname === '/api/auth/otp/verify') {
      const { phone, token } = await readBody(req);
      if (!phone || !token) return sendJSON(res, 400, { error: 'Phone and OTP token are required' });
      const session = await verifyPhoneOTP(phone, token);
      return sendJSON(res, 200, { success: true, session });
    }

    // 4. Matches: Create New Match (S03)
    if (req.method === 'POST' && pathname === '/api/matches') {
      const body = await readBody(req);
      const { team_a_id, team_b_id, total_overs, ball_type, ground_name } = body;

      const { data: match, error } = await supabaseAdmin
        .from('matches')
        .insert({
          team_a_id,
          team_b_id,
          total_overs: total_overs || 20,
          ball_type: ball_type || 'tennis',
          ground_name: ground_name || 'Oval Ground',
          match_date: new Date().toISOString(),
          status: 'scheduled',
        })
        .select()
        .single();

      if (error) throw error;
      return sendJSON(res, 201, { success: true, match });
    }

    // 5. Matches: Record Toss (S05)
    if (req.method === 'POST' && pathname.match(/^\/api\/matches\/([^/]+)\/toss$/)) {
      const matchId = pathname.split('/')[3];
      const { toss_winner_team_id, toss_decision } = await readBody(req);

      const { data: match, error } = await supabaseAdmin
        .from('matches')
        .update({
          toss_winner_team_id,
          toss_decision,
          status: 'live',
          updated_at: new Date().toISOString(),
        })
        .eq('id', matchId)
        .select()
        .single();

      if (error) throw error;
      return sendJSON(res, 200, { success: true, match });
    }

    // 6. Scoring: Record Delivery & Rotate Strike (S07)
    if (req.method === 'POST' && pathname.match(/^\/api\/matches\/([^/]+)\/deliveries$/)) {
      const matchId = pathname.split('/')[3];
      const body = await readBody(req);
      const {
        over_id,
        ball_number,
        delivery_seq,
        striker_player_id,
        non_striker_player_id,
        bowler_player_id,
        runs_scored,
        is_extra,
        extra_type,
        is_wicket,
        shot_zone,
      } = body;

      // Insert delivery into database
      const { data: delivery, error } = await supabaseAdmin
        .from('deliveries')
        .insert({
          over_id,
          ball_number,
          delivery_seq,
          striker_player_id,
          non_striker_player_id,
          bowler_player_id,
          runs_scored: runs_scored || 0,
          is_extra: Boolean(is_extra),
          extra_type: extra_type || null,
          extra_runs: is_extra ? 1 : 0,
          is_legal_ball: !(extra_type === 'wide' || extra_type === 'no_ball'),
          is_wicket: Boolean(is_wicket),
          shot_zone: shot_zone || null,
        })
        .select()
        .single();

      if (error) throw error;

      // Broadcast live delivery update via WebSockets to scorecards and OBS tickers
      broadcastMatchEvent(matchId, {
        type: 'DELIVERY_RECORDED',
        delivery,
        runs: runs_scored || 0,
        isWicket: Boolean(is_wicket),
        isExtra: Boolean(is_extra),
      });

      return sendJSON(res, 201, { success: true, delivery });
    }

    // 7. Scoring: Undo Last Delivery
    if (req.method === 'POST' && pathname.match(/^\/api\/matches\/([^/]+)\/deliveries\/undo$/)) {
      const matchId = pathname.split('/')[3];
      const { over_id } = await readBody(req);

      // Find the latest delivery in this over
      const { data: lastDelivery } = await supabaseAdmin
        .from('deliveries')
        .select('id, delivery_seq')
        .eq('over_id', over_id)
        .order('delivery_seq', { ascending: false })
        .limit(1)
        .maybeSingle();

      if (lastDelivery) {
        await supabaseAdmin.from('deliveries').delete().eq('id', lastDelivery.id);
        broadcastMatchEvent(matchId, { type: 'DELIVERY_UNDONE', deliveryId: lastDelivery.id });
      }

      return sendJSON(res, 200, { success: true, message: 'Last delivery rolled back' });
    }

    // 8. Public Scorecard (S13)
    if (req.method === 'GET' && pathname.match(/^\/api\/matches\/([^/]+)\/scorecard$/)) {
      const matchId = pathname.split('/')[3];

      const { data: match, error } = await supabaseAdmin
        .from('matches')
        .select(`
          id, status, match_type, total_overs, ground_name, match_date,
          team_a:teams!team_a_id (id, name, short_name),
          team_b:teams!team_b_id (id, name, short_name),
          innings (*)
        `)
        .eq('id', matchId)
        .single();

      if (error) throw error;
      return sendJSON(res, 200, { match });
    }

    // 8b. Match Live Stream OBS Overlay Metadata & MQTT Topics
    if (req.method === 'GET' && pathname.match(/^\/api\/matches\/([^/]+)\/overlay$/)) {
      const matchId = pathname.split('/')[3];
      return sendJSON(res, 200, {
        matchId,
        overlayUrl: `/index.html?overlay=true&matchId=${matchId}`,
        mqttEndpoint: `ws://${req.headers.host || 'localhost:4000'}/mqtt`,
        topics: {
          score: `cricheroes/matches/${matchId}/score`,
          ball: `cricheroes/matches/${matchId}/ball`,
          overlay: `cricheroes/matches/${matchId}/overlay`,
        },
      });
    }

    // 8c. Live Stream Broadcast Event Push (custom overlay triggers)
    if (req.method === 'POST' && pathname.match(/^\/api\/matches\/([^/]+)\/broadcast$/)) {
      const matchId = pathname.split('/')[3];
      const payload = await readBody(req);
      broadcastMatchEvent(matchId, payload);
      return sendJSON(res, 200, { success: true, message: 'Broadcast event dispatched' });
    }

    // 9. Tournament Dynamic Points Table with Automated NRR (S18)
    if (req.method === 'GET' && pathname.match(/^\/api\/tournaments\/([^/]+)\/standings$/)) {
      const tournamentId = pathname.split('/')[3];

      const { data: standings, error } = await supabaseAdmin
        .from('tournament_standings')
        .select(`
          id, played, won, lost, tied, no_result, points, runs_scored,
          overs_faced, runs_conceded, overs_bowled, net_run_rate,
          team:teams (id, name, short_name)
        `)
        .order('points', { ascending: false })
        .order('net_run_rate', { ascending: false });

      if (error) throw error;
      return sendJSON(res, 200, { tournamentId, standings });
    }

    // 10. Stripe Pro Checkout Session
    if (req.method === 'POST' && pathname === '/api/stripe/checkout') {
      const { user_id, email, plan, success_url, cancel_url } = await readBody(req);
      const session = await createProCheckoutSession({
        userId: user_id,
        userEmail: email,
        plan: plan || 'pro_monthly',
        successUrl: success_url || 'https://tallypitch.app/pro/success',
        cancelUrl: cancel_url || 'https://tallypitch.app/pro/cancel',
      });
      return sendJSON(res, 200, { sessionUrl: session.url, sessionId: session.id });
    }

    // 404 Route Not Found
    sendJSON(res, 404, { error: 'Route not found' });
  } catch (err) {
    console.error('API Error:', err);
    sendJSON(res, 500, { error: err.message || 'Internal Server Error' });
  }
}

// Instantiate HTTP & WebSocket server
const server = http.createServer(requestHandler);
setupRealtimeServer(server);

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`🏏 TallyPitch Backend API running on port ${PORT}`);
    console.log(`⚡ WebSocket Live Score feed: ws://localhost:${PORT}/ws/live?matchId=<ID>`);
  });
}

module.exports = { server, requestHandler };
