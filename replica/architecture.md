# Architecture: CricHeroes Replica (a rebuild of CricHeroes's core features)

## Stack

| layer | choice | why |
| --- | --- | --- |
| web | Next.js (App Router) + TypeScript | Server Components for instant public scorecards and SEO; client state for high-frequency scoring console |
| styling | Vanilla CSS / Tailored CSS Tokens | Lightweight, zero-runtime tokens matched to replica design specs for clean desktop & mobile web |
| mobile | Progressive Web App (PWA) / Expo React Native | Instant access from mobile browsers on the cricket ground without mandatory app store gating |
| database | PostgreSQL on Supabase or Neon | ACID transactions for ball-by-ball delivery sequences, jsonb for extras/rules, and native Realtime WebSockets |
| ORM | Drizzle ORM | Type-safe SQL queries, zero overhead, fast schema migrations, and clean relational joins |
| auth | Supabase Auth (Phone OTP & Google OAuth) | Matches CricHeroes's mobile-first phone number signup and seamless social login |
| payments | Stripe Checkout + Billing | Reliable recurring billing for Pro subscriptions (monthly/annual) and per-match streaming passes |
| email | Resend | Transactional emails for tournament fixture invites, match result summaries, and team invites |
| realtime | Supabase Realtime / WebSockets | Low-latency broadcast pushing live delivery updates to spectators and OBS stream overlays |
| storage | Supabase Storage or Cloudflare R2 | Storage for player avatars, team logos, and tournament banner images |
| hosting | Vercel | Global edge network for low latency, serverless API execution, and zero-config deployment |

## Schema

Tables: 16. Access rules: PostgreSQL Row Level Security (RLS) on Supabase.
Full DDL specification is maintained in [`replica/schema.sql`](file:///Volumes/Study/Projects/Replica/replica/schema.sql).

### Key Constraints & Invariants
1. **Monotonic Ball Sequencing**: `deliveries (over_id, delivery_seq)` is strictly unique to prevent race conditions during rapid entry.
2. **Consecutive Bowler Lock**: Over validation requires `over[n].bowler_player_id != over[n-1].bowler_player_id`.
3. **Distinct Strikers**: Check constraint `striker_player_id != non_striker_player_id` enforced in the database.
4. **ICC Net Run Rate Precision**: Stored as `numeric(6,3)` to maintain exact cricket tie-breaker accuracy.

---

## API

### F01: Quick Match Setup & Initialization
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches` | Create a new match record | Scorer / Organizer | `{team_a_id, team_b_id, total_overs, match_type, ball_type, ground_name, match_date}` | `{match: Match}` | F01 |
| `POST /api/matches/:id/squad` | Set Playing XI and roles | Scorer / Captain | `{team_id, playing_xi_ids: UUID[], captain_id, wicket_keeper_id}` | `{squad: MatchSquad[]}` | F01 |
| `POST /api/matches/:id/toss` | Record toss winner and choice | Scorer | `{toss_winner_team_id, toss_decision: 'bat' \| 'bowl'}` | `{match: Match}` | F01 |
| `POST /api/matches/:id/openers` | Select openers and opening bowler | Scorer | `{striker_id, non_striker_id, opening_bowler_id}` | `{innings_id, over_id, match_state}` | F01 |

### F02 & F03: Ball-by-Ball Scoring, Strike Rotation & Extras
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches/:id/deliveries` | Record single ball delivery | Assigned Scorer | `{runs_scored, is_extra, extra_type, extra_runs, shot_zone, is_free_hit}` | `{delivery: Delivery, updated_innings, current_over, strike: {striker_id, non_striker_id}}` | F02, F03 |
| `POST /api/matches/:id/deliveries/undo` | Undo the last recorded delivery | Assigned Scorer | `{}` | `{restored_delivery_seq, strike, updated_innings}` | F02 |

### F04: Wicket Dismissals & Incoming Batter
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches/:id/dismissals` | Record dismissal and incoming batter | Assigned Scorer | `{delivery_id, out_player_id, dismissal_type, fielder_player_id, next_batter_player_id, run_out_end}` | `{dismissal: Dismissal, fall_of_wicket, next_striker}` | F04 |

### F05: Over Completion & Bowler Handover
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches/:id/overs/next` | Finalize completed over & set next bowler | Assigned Scorer | `{current_over_id, next_bowler_player_id}` | `{over: Over, strike_rotated: boolean}` | F05 |

### F06: Innings Completion & Target Chase
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches/:id/innings/next` | Conclude 1st innings & initialize 2nd innings | Assigned Scorer | `{target_runs, chase_striker_id, chase_non_striker_id, opening_bowler_id}` | `{innings: Innings, rrr: number}` | F06 |

### F07: Match Finalization & Public Scorecard
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/matches/:id/complete` | Conclude match, compute winner & MVP | Assigned Scorer | `{}` | `{match: Match, player_of_match: Player, mvp_points}` | F07 |
| `GET /api/matches/:id/scorecard` | Public detailed match scorecard | Public | Query: `?tab=summary\|scorecard\|commentary` | `{match, innings_1, innings_2, batting, bowling, fow}` | F07 |
| `GET /api/matches/:id/analytics` | Fetch Manhattan & Worm chart data | Public | `{}` | `{manhattan: OverRuns[], worm: CumulativeRuns[]}` | F07 |

### F08: Tournament Management & Dynamic Points Table
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `POST /api/tournaments` | Create tournament | Organizer | `{name, category, ball_type, start_date, end_date, rules}` | `{tournament: Tournament}` | F08 |
| `POST /api/tournaments/:id/fixtures/generate` | Auto-generate round-robin fixture list | Organizer | `{group_ids: UUID[], venues: string[]}` | `{fixtures: Match[]}` | F08 |
| `GET /api/tournaments/:id/standings` | Dynamic Points Table with automated NRR | Public | `{}` | `{groups: [{id, name, standings: TournamentStanding[]}]}` | F08 |
| `GET /api/tournaments/:id/leaderboards` | Top tournament run scorers & wicket takers | Public | Query: `?type=runs\|wickets\|mvp` | `{leaders: PlayerStats[]}` | F08 |

### F09: Live Streaming & Overlay
| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| `GET /api/matches/:id/overlay` | Clean transparent lower-third HTML for OBS | OBS Browser Source | Query: `?key=stream_key&theme=classic` | HTML Webpage with WebSocket live score feed | F09 |

---

### Webhooks & Background Jobs

- **Webhooks In**:
  - `POST /api/webhooks/stripe`: Manages Pro subscription activations, renewals, and cancellations.
- **Webhooks Out**:
  - `POST /api/webhooks/match-events`: Dispatches match milestones (centuries, 5-wicket hauls, match won) to third-party team channels (Discord / Telegram).
- **Background Jobs**:
  - `cron/recalculate-nrr` (Nightly): Audits tournament group tables and verifies Net Run Rate integrity across finished games.
  - `cron/cleanup-live-channels` (Every 2 hours): Closes idle WebSocket channels for completed or abandoned matches.
  - `cron/leaderboard-refresh` (Hourly): Updates cached tournament top run-scorers and purple cap leaders.

---

## The parts that bite

- **Cricket Strike Rotation Logic**: Odd runs (1, 3, 5) swap striker and non-striker. Even runs (0, 2, 4, 6) keep the same striker. At the end of an over, the strike flips again (so the batter who faced the 6th ball becomes the non-striker for the 1st ball of the next over, unless an odd run occurred on ball 6). All mutations must be calculated within an atomic database transaction.
- **Extras & Legal Delivery Counting**: Wides and No-Balls cost runs (typically +1) but **do not increment the legal ball counter**. An over only completes after 6 legal deliveries. No-balls trigger a Free Hit flag on the next delivery where the batter cannot be dismissed bowled, caught, or LBW.
- **The Undo Stack**: Scorers in amateur games frequently miskey numbers. The undo endpoint must roll back the latest delivery, restore the exact previous striker/non-striker configuration, and deduct recorded runs/wickets without leaving orphaned dismissal or boundary records.
- **ICC Net Run Rate (NRR) Formula**:
  $$\text{NRR} = \left(\frac{\text{Total Runs Scored}}{\text{Total Overs Faced}}\right) - \left(\frac{\text{Total Runs Conceded}}{\text{Total Overs Bowled}}\right)$$
  If a team is bowled out before their allotted overs, the calculation uses the full quota of overs (e.g., 20.0 overs), not the actual overs faced. Rain-affected matches using DLS must adjust both runs and overs accordingly.
- **Broadcast Concurrency**: Spectators and OBS streamers refresh simultaneously during live matches. All live scores are delivered over WebSocket channels with Redis/Supabase caching so the primary database is never hammered by spectator read traffic.

---

## Build order

### 1. Vertical Slice (Core Loop End-to-End)
- **Goal**: Score a match ball-by-ball, rotate strike automatically, and view the live scorecard.
- **Screens**: S03 (Match Setup) -> S05 (Toss) -> S06 (Openers) -> S07 (Live Scoring Console) -> S13 (Scorecard).
- **Tables**: `users`, `players`, `teams`, `matches`, `innings`, `overs`, `deliveries`, `dismissals`.
- **Routes**: `POST /api/matches`, `POST /api/matches/:id/toss`, `POST /api/matches/:id/openers`, `POST /api/matches/:id/deliveries`, `GET /api/matches/:id/scorecard`.

### 2. Must-Haves (Complete Gameplay & Tournaments)
- **Areas**: Onboarding & Squad Selection (S01, S04), Over Completion & Bowler Switch (S10), Innings Break (S11), Match Result & Winner (S12), Tournament Setup, Fixtures & Dynamic Points Table with NRR (S15, S16, S17, S18), Player Career Profiles (S20).
- **Tables**: `match_squads`, `tournaments`, `tournament_groups`, `tournament_teams`, `tournament_standings`.
- **Routes**: Remaining CRUD endpoints for squads, tournament fixtures, standings, and player profiles.

### 3. Should-Haves (Analytics & Broadcast Tools)
- **Areas**: Wagon wheel directional chart (S09), Match analytics (Manhattan, Worm chart - S14), Tournament leaderboards (S19), Team profile roster (S21), OBS lower-third live stream overlay (S22).
- **Tables**: `live_stream_configs`.
- **Routes**: `/api/matches/:id/overlay`, `/api/matches/:id/analytics`, `/api/tournaments/:id/leaderboards`.

### 4. Could-Haves & Fixes from `/replica-entrepreneur`
- **Areas**: Community matchmaking board ("Looking For" - S23), Pro subscription paywall & CricInsights (S24), customer complaints and UX improvements identified during the public review sweep.
- **Tables**: `subscriptions`.
