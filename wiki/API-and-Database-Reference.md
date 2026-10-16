# API & Database Reference

Comprehensive specification of TallyPitch backend endpoints, data models, and database invariants.

---

## 1. REST API Specification

### Matches & Scoring (`server/api.js`)

| Method & Path | Description | Key Parameters |
| :--- | :--- | :--- |
| `POST /api/matches` | Create a new match | `team_a_id`, `team_b_id`, `total_overs`, `ball_type` |
| `POST /api/matches/:id/toss` | Record toss winner & choice | `toss_winner_team_id`, `toss_decision` ('bat' \| 'bowl') |
| `POST /api/matches/:id/openers` | Confirm opening batters & bowler | `striker_id`, `non_striker_id`, `opening_bowler_id` |
| `POST /api/matches/:id/deliveries` | Record a single ball delivery | `runs_scored`, `is_extra`, `extra_type`, `shot_zone` |
| `POST /api/matches/:id/deliveries/undo` | Atomic 0ms delivery rollback | None |
| `POST /api/matches/:id/dismissals` | Record wicket & next batter | `out_player_id`, `dismissal_type`, `next_batter_id` |
| `POST /api/matches/:id/overs/next` | Finalize over & assign next bowler | `next_bowler_player_id` |

### Tournaments & Standings

| Method & Path | Description | Key Parameters |
| :--- | :--- | :--- |
| `POST /api/tournaments` | Create a new tournament | `name`, `format`, `stages` |
| `GET /api/tournaments/:id/standings` | Fetch points table with NRR | `tournament_id` |

---

## 2. PostgreSQL Database Schema (`supabase/migrations/`)

The database architecture consists of 16 relational tables with Row-Level Security:

1. `profiles`: Player, scorer, and organizer user accounts.
2. `clubs`: Registered cricket clubs and community organizations.
3. `teams`: Squads participating in leagues or standalone games.
4. `team_members`: Association of players with clubs/teams and historical roles.
5. `tournaments`: Multi-stage tournament metadata and rules.
6. `tournament_teams`: Registration of teams into tournament stages.
7. `matches`: Individual match records, venue, toss details, and match status.
8. `match_squads`: Playing XI and substitute designations.
9. `innings`: Innings 1 and Innings 2 summary statistics.
10. `overs`: Sequential overs bowled per innings.
11. `deliveries`: Immutable granular delivery log with sequential ball numbers.
12. `dismissals`: Specific wicket details, dismissal types, and catch/run-out fielders.
13. `wagon_wheel_events`: Pitch coordinates and radial trajectory angles for shot maps.
14. `tournament_standings`: Computed points, wins, losses, ties, and Net Run Rate (numeric 6,3).
15. `subscriptions`: Stripe billing status, tier ('pro' / 'association'), and renewal dates.
16. `broadcast_tokens`: Security tokens for live OBS overlay endpoints.

---

## 3. Data Integrity Invariants

- **Monotonic Sequence**: `UNIQUE(over_id, delivery_seq)` strictly enforces monotonic ordering of deliveries.
- **Consecutive Bowler Prohibition**: `over[n].bowler_id != over[n-1].bowler_id` ensures bowler change at over transition.
- **Distinct Strikers**: `CHECK(striker_id != non_striker_id)` prevents the same player from occupying both ends.
