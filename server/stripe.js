// server/stripe.js
// Stripe Checkout & Webhook Integration for CricHeroes Pro Subscriptions

const stripe = process.env.STRIPE_SECRET_KEY ? require('stripe')(process.env.STRIPE_SECRET_KEY) : null;
const { supabaseAdmin } = require('./db');

const PRO_MONTHLY_PRICE_ID = process.env.STRIPE_PRO_MONTHLY_PRICE_ID || 'price_pro_monthly_test';
const PRO_ANNUAL_PRICE_ID = process.env.STRIPE_PRO_ANNUAL_PRICE_ID || 'price_pro_annual_test';

/**
 * Creates a Stripe Checkout session for a user upgrading to CricHeroes Pro
 * @param {string} userId - User ID
 * @param {string} userEmail - User's email
 * @param {string} plan - 'pro_monthly' | 'pro_annual'
 * @param {string} successUrl - Redirect after payment
 * @param {string} cancelUrl - Redirect if cancelled
 */
async function createProCheckoutSession({ userId, userEmail, plan, successUrl, cancelUrl }) {
  if (!stripe) {
    throw new Error('STRIPE_SECRET_KEY not configured. Running in demo mode.');
  }

  const priceId = plan === 'pro_annual' ? PRO_ANNUAL_PRICE_ID : PRO_MONTHLY_PRICE_ID;

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    customer_email: userEmail,
    client_reference_id: userId,
    metadata: {
      userId,
      plan,
    },
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    success_url: `${successUrl}?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: cancelUrl,
  });

  return session;
}

/**
 * Handles Stripe webhook events idempotently
 * @param {Buffer} rawBody - Raw unparsed request body buffer for signature verification
 * @param {string} signature - Stripe-Signature header
 */
async function handleStripeWebhook(rawBody, signature) {
  if (!stripe) throw new Error('Stripe not initialized');

  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  let event;

  try {
    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (err) {
    throw new Error(`Webhook signature verification failed: ${err.message}`);
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object;
      const userId = session.client_reference_id || session.metadata?.userId;
      const plan = session.metadata?.plan || 'pro_monthly';

      if (userId) {
        await supabaseAdmin.from('subscriptions').upsert({
          user_id: userId,
          plan,
          status: 'active',
          stripe_customer_id: session.customer,
          stripe_subscription_id: session.subscription,
          current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date().toISOString(),
        });
      }
      break;
    }

    case 'customer.subscription.updated':
    case 'customer.subscription.deleted': {
      const sub = event.data.object;
      const status = sub.status === 'active' ? 'active' : 'canceled';

      await supabaseAdmin
        .from('subscriptions')
        .update({
          status,
          current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
          updated_at: new Date().toISOString(),
        })
        .eq('stripe_subscription_id', sub.id);
      break;
    }

    default:
      break;
  }

  return { received: true, type: event.type };
}

module.exports = {
  createProCheckoutSession,
  handleStripeWebhook,
};
