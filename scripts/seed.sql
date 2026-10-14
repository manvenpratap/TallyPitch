-- Seed script: scripts/seed.sql
-- Realistic sample grassroots cricket data for CricHeroes clone

-- 1. Sample Users (Scorers & Organizers)
insert into users (id, phone, email, full_name, role)
values
  ('11111111-1111-1111-1111-111111111111', '+919876543210', 'scorer@cricheroes.local', 'Aditya Verma', 'scorer'),
  ('22222222-2222-2222-2222-222222222222', '+919876543211', 'organizer@cricheroes.local', 'Rajesh Patel', 'organizer'),
  ('33333333-3333-3333-3333-333333333333', '+919876543212', 'rohit@cricheroes.local', 'Rohit Sharma', 'player'),
  ('44444444-4444-4444-4444-444444444444', '+919876543213', 'virat@cricheroes.local', 'Virat Kohli', 'player')
on conflict (id) do nothing;

-- 2. Sample Players
insert into players (id, user_id, display_name, primary_role, batting_style, bowling_style, city)
values
  ('a1111111-0000-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 'Rohit Sharma', 'batter', 'rhb', 'spin', 'Mumbai'),
  ('a1111111-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'Ishan Kishan', 'wicket_keeper', 'lhb', 'none', 'Mumbai'),
  ('b1111111-0000-0000-0000-000000000001', '44444444-4444-4444-4444-444444444444', 'Virat Kohli', 'batter', 'rhb', 'medium', 'Bengaluru'),
  ('b1111111-0000-0000-0000-000000000002', '22222222-2222-2222-2222-222222222222', 'Jasprit Bumrah', 'bowler', 'rhb', 'fast', 'Ahmedabad')
on conflict (id) do nothing;

-- 3. Sample Teams
insert into teams (id, name, short_name, city, created_by_user_id, captain_player_id)
values
  ('aaaa0000-0000-0000-0000-000000000001', 'Mumbai Strikers', 'MUM', 'Mumbai', '11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001'),
  ('bbbb0000-0000-0000-0000-000000000002', 'Bangalore Blasters', 'BLR', 'Bengaluru', '22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001')
on conflict (id) do nothing;

-- 4. Sample Tournament
insert into tournaments (id, name, organizer_user_id, category, ball_type, start_date, end_date, status)
values
  ('t0000000-0000-0000-0000-000000000001', 'Premier Grassroots Cup 2026', '22222222-2222-2222-2222-222222222222', 'club', 'tennis', current_date, current_date + interval '14 days', 'ongoing')
on conflict (id) do nothing;

-- 5. Tournament Group & Standings
insert into tournament_groups (id, tournament_id, name, round_number)
values
  ('g0000000-0000-0000-0000-000000000001', 't0000000-0000-0000-0000-000000000001', 'Group A', 1)
on conflict (id) do nothing;

insert into tournament_standings (id, group_id, team_id, played, won, lost, points, net_run_rate)
values
  (gen_random_uuid(), 'g0000000-0000-0000-0000-000000000001', 'aaaa0000-0000-0000-0000-000000000001', 1, 1, 0, 2, 1.250),
  (gen_random_uuid(), 'g0000000-0000-0000-0000-000000000001', 'bbbb0000-0000-0000-0000-000000000002', 1, 0, 1, 0, -1.250)
on conflict do nothing;

-- 6. Sample Live Match
insert into matches (
  id, tournament_id, team_a_id, team_b_id, match_type, total_overs, ball_type,
  ground_name, match_date, toss_winner_team_id, toss_decision, status, scorer_user_id
)
values (
  'm0000000-0000-0000-0000-000000000001',
  't0000000-0000-0000-0000-000000000001',
  'aaaa0000-0000-0000-0000-000000000001',
  'bbbb0000-0000-0000-0000-000000000002',
  'limited_overs',
  20,
  'tennis',
  'Oval Ground, Mumbai',
  now(),
  'aaaa0000-0000-0000-0000-000000000001',
  'bat',
  'live',
  '11111111-1111-1111-1111-111111111111'
)
on conflict (id) do nothing;
