// server/auth.js
// Supabase Authentication & Session Management for CricHeroes Replica

const { supabase, supabaseAdmin } = require('./db');

/**
 * Sends a 6-digit OTP code to the user's mobile number via Supabase SMS
 * @param {string} phone - e.g. "+919876543210"
 */
async function sendPhoneOTP(phone) {
  const { data, error } = await supabase.auth.signInWithOtp({
    phone,
    options: {
      channel: 'sms',
    },
  });
  if (error) throw error;
  return data;
}

/**
 * Verifies the 6-digit OTP code and returns an access session
 * @param {string} phone - e.g. "+919876543210"
 * @param {string} token - 6-digit OTP string
 */
async function verifyPhoneOTP(phone, token) {
  const { data, error } = await supabase.auth.verifyOtp({
    phone,
    token,
    type: 'sms',
  });
  if (error) throw error;

  // Ensure player profile exists in 'players' table
  if (data.user) {
    const { data: existingPlayer } = await supabaseAdmin
      .from('players')
      .select('id')
      .eq('user_id', data.user.id)
      .maybeSingle();

    if (!existingPlayer) {
      await supabaseAdmin.from('players').insert({
        user_id: data.user.id,
        display_name: data.user.user_metadata?.full_name || `Player ${phone.slice(-4)}`,
        primary_role: 'all_rounder',
        batting_style: 'rhb',
        bowling_style: 'medium',
      });
    }
  }

  return data;
}

/**
 * Express/Connect middleware to enforce authentication
 */
async function requireAuth(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header' });
  }

  const token = authHeader.split(' ')[1];
  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) {
    return res.status(401).json({ error: 'Invalid or expired session token' });
  }

  req.user = user;
  req.token = token;
  next();
}

module.exports = {
  sendPhoneOTP,
  verifyPhoneOTP,
  requireAuth,
};
