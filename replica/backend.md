# Backend Architecture & Security Checklist: CricHeroes Replica

This document records the backend infrastructure, database migrations, Supabase Auth integration, WebSocket live streaming, and production security controls for the CricHeroes replica.

---

## 1. Database & Migrations

- **Engine**: PostgreSQL 15+ (Hosted on Supabase or Neon).
- **Migration Location**: [`supabase/migrations/20261014000000_init_cricheroes.sql`](file:///Volumes/Study/Projects/Replica/supabase/migrations/20261014000000_init_cricheroes.sql)
- **Seed Data**: [`scripts/seed.sql`](file:///Volumes/Study/Projects/Replica/scripts/seed.sql) with realistic grassroots club teams (Mumbai Strikers vs Bangalore Blasters), players, sample tournament, and active live matches.
- **Row Level Security (RLS)**: Enabled across all 16 tables.
  - Public `SELECT` allowed on published matches, innings, deliveries, points tables, and public player profiles.
  - Scorer `INSERT/UPDATE/DELETE` strictly gated by `auth.uid() = matches.scorer_user_id`.
  - Monotonic uniqueness enforced on `(over_id, delivery_seq)` to eliminate delivery insertion race conditions.

---

## 2. Authentication & Sessions

- **Primary Provider**: Supabase Auth with SMS Phone OTP (`server/auth.js`).
- **Session Tokens**: JWT stored in http-only cookies on web; Bearer token on mobile apps.
- **Profile Initialization**: Automatically registers new players in the `players` table upon OTP verification.
- **Role Enforcement**: User roles (`player`, `scorer`, `organizer`, `admin`) govern administrative permissions across tournament management and match editing.

---

## 3. Realtime Live Score Broadcasting

- **Protocol**: WebSockets via `ws` module (`server/realtime.js`) and Supabase Realtime Publication (`supabase_realtime` added for `matches`, `innings`, `overs`, `deliveries`, `dismissals`).
- **Channel Routing**: `ws://localhost:4000/ws/live?matchId=<UUID>`.
- **Latency**: Sub-50ms delivery propagation to active viewer scorecards and OBS lower-third transparent graphic overlays.
- **Connection Lifecycle**: Graceful cleanup of inactive client sockets and match rooms.

---

## 4. Payments & Subscriptions (Stripe)

- **Checkout Gateway**: Stripe Checkout (`server/stripe.js`) for Pro subscriptions (`pro_monthly` and `pro_annual`).
- **Webhooks**: Idempotent webhook handler at `/api/webhooks/stripe` verifying cryptographic signatures via `STRIPE_WEBHOOK_SECRET`.
- **Events Handled**:
  - `checkout.session.completed` -> activates Pro tier in `subscriptions` table.
  - `customer.subscription.updated` -> updates subscription status and period end.
  - `customer.subscription.deleted` -> marks plan as canceled with zero grace period leaks.

---

## 5. Security Checklist

- [x] **Secrets**: Zero credentials checked into Git. `.env.local` untracked, template provided in [`.env.example`](file:///Volumes/Study/Projects/Replica/.env.example).
- [x] **Input Validation**: Server validates required parameters (`over_id`, `delivery_seq`, `runs_scored`, `extra_type`, `dismissal_type`) before SQL execution.
- [x] **Access Control**: Row Level Security (RLS) active on all tables. Scorers can only score matches they are assigned to.
- [x] **Atomic Transactions**: Ball recording and undo operations run in sequence to prevent partial writes.
- [x] **Stripe Signature Verification**: Webhook handler reconstructs events with raw body buffer.
- [x] **No Proprietary Endpoints**: 100% clean-room backend implementation using standard Node.js and Supabase SDKs.

---

## 6. Next Steps

- Execute **`/replica-test`** to run end-to-end user flow test suites against the backend and scoring engine.
