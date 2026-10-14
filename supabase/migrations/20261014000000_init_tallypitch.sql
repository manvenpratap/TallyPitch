-- Migration: 20261014000000_init_tallypitch.sql
-- Description: Core database schema, tables, foreign keys, constraints, and Row Level Security (RLS)

-- Extensions
create extension if not exists "pgcrypto";

-- ============================================================================
-- 1. USERS & PROFILES
-- ============================================================================

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  phone text unique not null,
  email text,
  full_name text not null,
  avatar_url text,
  role text not null default 'player' check (role in ('player', 'scorer', 'organizer', 'admin')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists players (
  id uuid primary key default gen_random_uuid(),
  user_id uuid unique not null references users(id) on delete cascade,
  display_name text not null,
  primary_role text not null default 'all_rounder' check (primary_role in ('batter', 'bowler', 'all_rounder', 'wicket_keeper')),
  batting_style text not null default 'rhb' check (batting_style in ('rhb', 'lhb')),
  bowling_style text not null default 'medium' check (bowling_style in ('fast', 'medium', 'spin', 'none')),
  city text,
  bio text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_players_user on players(user_id);
create index if not exists idx_players_role on players(primary_role);

-- ============================================================================
-- 2. TEAMS & ROSTERS
-- ============================================================================

create table if not exists teams (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  short_name text not null,
  logo_url text,
  city text,
  captain_player_id uuid references players(id) on delete set null,
  created_by_user_id uuid not null references users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_teams_creator on teams(created_by_user_id);

create table if not exists team_members (
  id uuid primary key default gen_random_uuid(),
  team_id uuid not null references teams(id) on delete cascade,
  player_id uuid not null references players(id) on delete cascade,
  role text not null default 'player' check (role in ('captain', 'vice_captain', 'wicket_keeper', 'player')),
  jersey_number int,
  joined_at timestamptz not null default now(),
  constraint uq_team_player unique (team_id, player_id)
);
create index if not exists idx_team_members_team on team_members(team_id);
create index if not exists idx_team_members_player on team_members(player_id);

-- ============================================================================
-- 3. TOURNAMENTS, GROUPS & STANDINGS
-- ============================================================================

create table if not exists tournaments (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  organizer_user_id uuid not null references users(id) on delete cascade,
  category text not null default 'open' check (category in ('open', 'club', 'corporate', 'school', 'box')),
  ball_type text not null default 'tennis' check (ball_type in ('tennis', 'leather', 'tape')),
  start_date date not null,
  end_date date not null,
  banner_url text,
  rules jsonb not null default '{"overs": 20, "powerplay_overs": 6, "balls_per_over": 6}',
  status text not null default 'upcoming' check (status in ('upcoming', 'ongoing', 'completed', 'abandoned')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint check_dates check (end_date >= start_date)
);
create index if not exists idx_tournaments_organizer on tournaments(organizer_user_id);
create index if not exists idx_tournaments_status on tournaments(status);

create table if not exists tournament_groups (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  name text not null,
  round_number int not null default 1,
  created_at timestamptz not null default now()
);
create index if not exists idx_groups_tournament on tournament_groups(tournament_id);

create table if not exists tournament_teams (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  group_id uuid references tournament_groups(id) on delete set null,
  team_id uuid not null references teams(id) on delete cascade,
  constraint uq_tournament_team unique (tournament_id, team_id)
);

create table if not exists tournament_standings (
  id uuid primary key default gen_random_uuid(),
  group_id uuid not null references tournament_groups(id) on delete cascade,
  team_id uuid not null references teams(id) on delete cascade,
  played int not null default 0,
  won int not null default 0,
  lost int not null default 0,
  tied int not null default 0,
  no_result int not null default 0,
  points int not null default 0,
  runs_scored int not null default 0,
  overs_faced numeric(5,1) not null default 0.0,
  runs_conceded int not null default 0,
  overs_bowled numeric(5,1) not null default 0.0,
  net_run_rate numeric(6,3) not null default 0.000,
  constraint uq_group_team unique (group_id, team_id)
);
create index if not exists idx_standings_rank on tournament_standings(group_id, points desc, net_run_rate desc);

-- ============================================================================
-- 4. MATCHES & SQUADS
-- ============================================================================

create table if not exists matches (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid references tournaments(id) on delete set null,
  team_a_id uuid not null references teams(id) on delete restrict,
  team_b_id uuid not null references teams(id) on delete restrict,
  match_type text not null default 'limited_overs' check (match_type in ('limited_overs', 'box', 'test')),
  total_overs int not null check (total_overs > 0),
  ball_type text not null default 'tennis' check (ball_type in ('tennis', 'leather', 'tape')),
  ground_name text,
  match_date timestamptz not null,
  toss_winner_team_id uuid references teams(id) on delete set null,
  toss_decision text check (toss_decision in ('bat', 'bowl', null)),
  status text not null default 'scheduled' check (status in ('scheduled', 'live', 'innings_break', 'completed', 'abandoned')),
  winner_team_id uuid references teams(id) on delete set null,
  win_margin_text text,
  player_of_match_id uuid references players(id) on delete set null,
  scorer_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint diff_teams check (team_a_id != team_b_id)
);
create index if not exists idx_matches_status_date on matches(status, match_date);
create index if not exists idx_matches_teams on matches(team_a_id, team_b_id);
create index if not exists idx_matches_tournament on matches(tournament_id);

create table if not exists match_squads (
  id uuid primary key default gen_random_uuid(),
  match_id uuid not null references matches(id) on delete cascade,
  team_id uuid not null references teams(id) on delete cascade,
  player_id uuid not null references players(id) on delete cascade,
  is_playing_xi boolean not null default true,
  is_captain boolean not null default false,
  is_wicket_keeper boolean not null default false,
  constraint uq_match_player unique (match_id, player_id)
);
create index if not exists idx_match_squads_match_team on match_squads(match_id, team_id);

-- ============================================================================
-- 5. SCORING STATE: INNINGS, OVERS & DELIVERIES
-- ============================================================================

create table if not exists innings (
  id uuid primary key default gen_random_uuid(),
  match_id uuid not null references matches(id) on delete cascade,
  innings_number int not null check (innings_number in (1, 2, 3, 4)),
  batting_team_id uuid not null references teams(id) on delete restrict,
  bowling_team_id uuid not null references teams(id) on delete restrict,
  total_runs int not null default 0,
  total_wickets int not null default 0,
  total_overs numeric(4,1) not null default 0.0,
  extras jsonb not null default '{"wides": 0, "no_balls": 0, "byes": 0, "leg_byes": 0, "penalties": 0}',
  target_runs int,
  is_completed boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_match_innings unique (match_id, innings_number)
);
create index if not exists idx_innings_match on innings(match_id);

create table if not exists overs (
  id uuid primary key default gen_random_uuid(),
  innings_id uuid not null references innings(id) on delete cascade,
  over_number int not null check (over_number >= 0),
  bowler_player_id uuid not null references players(id) on delete restrict,
  total_runs int not null default 0,
  total_wickets int not null default 0,
  is_maiden boolean not null default false,
  created_at timestamptz not null default now(),
  constraint uq_innings_over unique (innings_id, over_number)
);
create index if not exists idx_overs_innings on overs(innings_id);

create table if not exists deliveries (
  id uuid primary key default gen_random_uuid(),
  over_id uuid not null references overs(id) on delete cascade,
  ball_number int not null check (ball_number between 1 and 6),
  delivery_seq int not null,
  striker_player_id uuid not null references players(id) on delete restrict,
  non_striker_player_id uuid not null references players(id) on delete restrict,
  bowler_player_id uuid not null references players(id) on delete restrict,
  runs_scored int not null default 0 check (runs_scored between 0 and 6),
  is_extra boolean not null default false,
  extra_type text check (extra_type in ('wide', 'no_ball', 'bye', 'leg_bye', 'penalty', null)),
  extra_runs int not null default 0,
  is_legal_ball boolean not null default true,
  is_wicket boolean not null default false,
  shot_zone int check (shot_zone between 1 and 8 or shot_zone is null),
  is_free_hit boolean not null default false,
  created_at timestamptz not null default now(),
  constraint diff_strikers check (striker_player_id != non_striker_player_id),
  constraint uq_over_seq unique (over_id, delivery_seq)
);
create index if not exists idx_deliveries_over_seq on deliveries(over_id, delivery_seq);
create index if not exists idx_deliveries_striker on deliveries(striker_player_id);
create index if not exists idx_deliveries_bowler on deliveries(bowler_player_id);

create table if not exists dismissals (
  id uuid primary key default gen_random_uuid(),
  delivery_id uuid unique not null references deliveries(id) on delete cascade,
  out_player_id uuid not null references players(id) on delete restrict,
  dismissal_type text not null check (dismissal_type in ('bowled', 'caught', 'run_out', 'stumped', 'lbw', 'hit_wicket', 'retired')),
  bowler_player_id uuid references players(id) on delete set null,
  fielder_player_id uuid references players(id) on delete set null,
  run_out_end text check (run_out_end in ('striker', 'non_striker', null)),
  next_batter_player_id uuid references players(id) on delete set null,
  created_at timestamptz not null default now()
);
create index if not exists idx_dismissals_out_player on dismissals(out_player_id);

-- ============================================================================
-- 6. BROADCAST STREAMING & MONETIZATION
-- ============================================================================

create table if not exists live_stream_configs (
  id uuid primary key default gen_random_uuid(),
  match_id uuid unique not null references matches(id) on delete cascade,
  stream_key text unique not null default encode(gen_random_bytes(16), 'hex'),
  overlay_theme text not null default 'classic_dark',
  show_wagon_wheel boolean not null default true,
  show_sponsor_banner boolean not null default false,
  sponsor_banner_url text,
  is_live boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_stream_key on live_stream_configs(stream_key);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid unique not null references users(id) on delete cascade,
  plan text not null check (plan in ('pro_monthly', 'pro_annual')),
  status text not null default 'active' check (status in ('active', 'past_due', 'canceled', 'trialing')),
  stripe_customer_id text,
  stripe_subscription_id text,
  current_period_end timestamptz not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_subscriptions_user on subscriptions(user_id);

-- ============================================================================
-- 7. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

alter table users enable row level security;
alter table players enable row level security;
alter table teams enable row level security;
alter table tournaments enable row level security;
alter table matches enable row level security;
alter table match_squads enable row level security;
alter table innings enable row level security;
alter table overs enable row level security;
alter table deliveries enable row level security;
alter table dismissals enable row level security;
alter table tournament_standings enable row level security;
alter table live_stream_configs enable row level security;

-- Public Read Policies
create policy "Public read on users" on users for select using (true);
create policy "Public read on players" on players for select using (true);
create policy "Public read on teams" on teams for select using (true);
create policy "Public read on tournaments" on tournaments for select using (true);
create policy "Public read on matches" on matches for select using (true);
create policy "Public read on match_squads" on match_squads for select using (true);
create policy "Public read on innings" on innings for select using (true);
create policy "Public read on overs" on overs for select using (true);
create policy "Public read on deliveries" on deliveries for select using (true);
create policy "Public read on dismissals" on dismissals for select using (true);
create policy "Public read on standings" on tournament_standings for select using (true);
create policy "Public read on stream overlays" on live_stream_configs for select using (true);

-- Scorer Write Policies (Match Mutators)
create policy "Scorers can mutate deliveries" on deliveries
  for all using (
    exists (
      select 1 from overs o
      join innings i on o.innings_id = i.id
      join matches m on i.match_id = m.id
      where o.id = deliveries.over_id
      and (m.scorer_user_id = auth.uid() or auth.uid() is not null)
    )
  );

create policy "Scorers can mutate dismissals" on dismissals
  for all using (
    exists (
      select 1 from deliveries d
      join overs o on d.over_id = o.id
      join innings i on o.innings_id = i.id
      join matches m on i.match_id = m.id
      where d.id = dismissals.delivery_id
      and (m.scorer_user_id = auth.uid() or auth.uid() is not null)
    )
  );

-- Enable Supabase Realtime Publication for Live Scores
alter publication supabase_realtime add table matches;
alter publication supabase_realtime add table innings;
alter publication supabase_realtime add table overs;
alter publication supabase_realtime add table deliveries;
alter publication supabase_realtime add table dismissals;
