# Recon map: CricHeroes (Mobile Web & App)

Scope: Grassroots cricket match scoring (ball-by-ball, strike rotation, extras, dismissals, live scorecard), tournament league management (multi-stage fixtures, groups, knockouts, dynamic points table with ICC NRR), and player/team profile tracking with basic analytics.
For: Independent cricket clubs, amateur leagues, box/corporate cricket organizers, and players wanting a modern, clean-room scoring and tournament system.
Date: 2026-10-14

## Sources

| # | source | URL | notes |
| --- | --- | --- | --- |
| 1 | CricHeroes Main Platform | `https://cricheroes.com/` | Public overview, feature hierarchy, core positioning |
| 2 | Google Play Store Listing | `https://play.google.com/store/apps/details?id=com.cricheroes.android` | Feature matrix, key screenshots, user reviews, permission scope |
| 3 | Apple App Store Listing | `https://apps.apple.com/app/cricheroes/id1084938198` | UI layouts, in-app purchases, iPad/iOS layouts |
| 4 | Official CricHeroes Tutorials | CricHeroes YouTube Channel / Help Guides | Ball-by-ball scoring mechanics, toss, over completions, strike logic |
| 5 | CricHeroes PRO & CricInsights | `https://cricheroes.com/pro` | Monetization gating, head-to-head metrics, scouting analytics |
| 6 | Live Streaming & OBS Overlays | `https://cricheroes.com/live-stream` | Lower-third OBS score ticker, theme templates, stream pricing |

## Core loop

Tournament organizers schedule competitions, scorers capture live ball-by-ball match actions (runs, extras, wickets) in real time with automated strike rotation, and players and teams track their career statistics, leaderboards, and standings.

## Screens

| ID | screen | route / how to reach | purpose | key components | states seen |
| --- | --- | --- | --- | --- | --- |
| S01 | Onboarding & Auth | `/auth` or initial launch | Sign in with phone number/OTP, profile creation, and primary role selection | PhoneInput, OTPInput, RoleSelectorChip, PrimaryButton | empty, phone entered, code sent, error |
| S02 | Home Feed / Dashboard | `/` or `/home` | Hub for active live matches, recent results, upcoming tournaments, and quick action launcher | LiveMatchCard, TournamentBannerCard, QuickActionFAB, BottomNavBar | empty, live match ongoing, loading |
| S03 | Start Match - Setup | `/matches/new` (from FAB) | Configure teams, match type (Limited Overs/Box/Test), total overs, ball type, ground, and rules | TeamPickerSelect, MatchTypeToggle, BallTypeRadio, OversStepperInput | default, custom overs, missing team validation |
| S04 | Squad & Playing XI | `/matches/new/squad` | Select playing XI from each team roster and designate Captain (C) and Wicket-keeper (WK) | PlayerCheckboxList, RoleBadgeChip (C/WK), SquadCounter | unselected, 11 selected, incomplete squad warning |
| S05 | The Toss | `/matches/:id/toss` | Record which team won the coin toss and whether they elected to bat or bowl | CoinFlipCanvas, TossWinnerRadio, DecisionToggle (Bat/Bowl) | default, coin spinning, toss confirmed |
| S06 | Openers & Bowler Selection | `/matches/:id/openers` | Choose opening striker, non-striker, and opening bowler before first delivery | StrikerDropdown, NonStrikerDropdown, OpeningBowlerDropdown | empty, duplicate selection error, confirmed |
| S07 | Live Scoring Console | `/matches/:id/score` | Primary ball-by-ball scoring workspace with keypad, active batter/bowler status, and over feed | RunsKeypad (0-6), ExtrasBar, WicketButton, UndoButton, DeliveryCircles, LiveStatusPill | active delivery, free hit active, over break |
| S08 | Dismissal / Wicket Dialog | Modal on S07 tap Wicket | Record dismissal mode (bowled, caught, run out, stumped, lbw, hit wicket), fielder involved, and next batter | DismissalTypeGrid, FielderPicker, OutBatterRadio, NextBatterDropdown | default, fielder required, valid dismissal |
| S09 | Wagon Wheel Direction | Radial prompt on S07 | Pinpoint shot direction on a 360-degree field graphic for boundary or scoring shots | RadialGroundCanvas, ZoneSelector, SkipButton | default prompt, zone clicked, disabled mode |
| S10 | End of Over & Bowler Switch | Sheet on 6 legal balls | Summarize finished over (runs, wickets), prompt next bowler with consecutive over restriction | OverSummaryCard, BowlerRadioList, ConsecutiveErrorAlert | over complete, bowler selected, invalid bowler |
| S11 | Innings Break & Target | Modal on 1st innings end | Display 1st innings summary, compute target and required run rate (RRR), select chase openers | TargetSummaryCard, RRRDisplay, OpenersPicker | innings finished, openers chosen |
| S12 | Match Result & Summary | `/matches/:id/result` | Announce winner, victory margin, calculate automated MVP/Player of the Match, and share options | WinnerBanner, MVPPlayerCard, ShareScorecardButton | match won, match tied (super over prompt) |
| S13 | Full Match Scorecard | `/matches/:id/scorecard` | Detailed ICC-style scorecard: Batting, Bowling, Fall of Wickets, Extras, and Commentary | ScorecardTabs, BattingTable, BowlingTable, FOWTimeline | live in-progress, completed, collapsed tabs |
| S14 | Match Analytics & Charts | `/matches/:id/charts` | Visual match progression charts comparing both innings | ManhattanBarChart, WormLineChart, RunRateComparisonGraph | 1st innings only, both innings compared |
| S15 | Host Tournament - Details | `/tournaments/new` | Configure tournament name, category (Club/Corporate/School), dates, ball type, and banner | TournamentFormInput, CategorySelector, DateRangePicker | empty, valid form, banner upload |
| S16 | Tournament Format & Rounds | `/tournaments/:id/format` | Define tournament structure: league rounds, group pools (Group A/B), and knockout bracket | RoundBuilderList, GroupAssignmentGrid, KnockoutStageToggle | single group, multi-group round robin |
| S17 | Tournament Fixtures | `/tournaments/:id/fixtures` | Schedule matches with dates, pitch assignments, and assigned match scorers | FixtureMatchCard, DateGroupList, ScorerAssignDropdown | auto-generated, manual edit, unscheduled |
| S18 | Dynamic Points Table | `/tournaments/:id/standings` | Auto-updating group standings table sorted by Points and ICC Net Run Rate (NRR) | StandingsTable (P, W, L, T, NR, Pts, NRR), GroupTabs | empty season, ongoing league, ties sorted |
| S19 | Tournament Leaderboard | `/tournaments/:id/leaders` | Statistical awards across tournament: Orange Cap (Most Runs), Purple Cap (Most Wickets), MVP | LeaderPodiumCard, StatRankTable, CategoryTabs | no matches, active rankings |
| S20 | Player Career Profile | `/players/:id` | Digital cricket resume: batting/bowling career averages, strike rates, recent matches, and badges | CareerStatGrid, RecentMatchHistoryList, BadgesRibbon | rookie (no matches), active player, filtered by ball type |
| S21 | Team Profile & Roster | `/teams/:id` | Team dashboard: win/loss record, current tournament entries, and player roster | TeamHeaderCard, WinLossBar, MemberAvatarList | empty roster, active team, admin view |
| S22 | Live Stream OBS Ticker | `/matches/:id/overlay` | Clean, transparent lower-third web overlay fed via WebSockets for OBS/vMix live streaming | TransparentScoreTicker, BatsmanStrips, BowlerStrip, SponsorLogoSlot | normal score, boundary alert, wicket alert |
| S23 | Community "Looking For" | `/community/looking-for` | Grassroots matchmaking board for teams seeking players, players seeking teams, umpires, grounds | FilterChips, ListingCard, PostRequirementButton | empty, filtered by city, user posting |
| S24 | Pro Subscription / Pricing | `/pro` | Paywall and feature upgrade showcase: CricInsights, ad-free experience, and custom themes | PricingTierCard, FeatureChecklistTable, CheckoutButton | monthly, annual plan selected |

## Flows

```
F01 Quick Match Setup & First Ball Bowled
    S02 home -> S03 setup match -> S04 pick playing XI -> S05 record toss -> S06 select openers & bowler -> S07 live scoring console
    happy path clicks: 6
    edge: fewer than desired players selected, team has no wicket-keeper, toss decided via coin animation vs manual selection

F02 Ball-by-Ball Scoring with Strike Rotation
    S07 keypad tap run button -> (optional) S09 wagon wheel direction -> S07 live score updated
    happy path clicks: 2 (1 if wagon wheel bypassed)
    edge: odd runs (1, 3) automatically swap striker and non-striker; boundaries (4, 6) keep strike unless on last ball of over

F03 Extras Recording & Penalty Runs
    S07 tap extra (Wd / Nb / Bye / Lb) -> enter runs scored off the delivery -> S07 live score updated
    happy path clicks: 2
    edge: Wide/No-ball does not advance legal ball counter; Wide + boundary; No-ball triggers Free Hit flag for next delivery

F04 Wicket Dismissal & New Batter Entry
    S07 tap Wicket -> S08 select dismissal mode & involved fielder -> S08 pick incoming batter -> S07 live score updated
    happy path clicks: 3
    edge: Run out of non-striker end vs striker end, caught & bowled, retired hurt (not counted as bowler wicket)

F05 Over Completion & Bowler Handover
    S07 6th legal delivery bowled -> S10 over summary card opens -> S10 select next bowler -> S07 next over begins
    happy path clicks: 2
    edge: Bowler who bowled previous over is disabled in picker, bowling quota reached for limited overs match

F06 Innings Completion & Target Chase Setup
    S07 final over completed or all out -> S11 innings summary modal -> S06 select chase openers & opening bowler -> S07 second innings live scoring
    happy path clicks: 4
    edge: Target score set as Innings 1 + 1, DLS revised target on rain delays, Required Run Rate (RRR) live calculated

F07 Match Finalization & MVP Scorecard Publishing
    S07 winning run scored / final wicket fallen -> S12 match result & MVP announcement -> S13 full scorecard -> S14 match analytics
    happy path clicks: 3
    edge: Match tied triggers Super Over prompt; forfeited match; rain washout / No Result

F08 Multi-Stage Tournament Creation & Fixture Generation
    S02 home -> S15 tournament basic info -> S16 configure rounds & groups -> S17 generate fixtures -> S18 dynamic points table initialized
    happy path clicks: 5
    edge: Odd number of teams requires bye rounds; knockout bracket progression after group stage

F09 Connect Live Match to OBS Stream Overlay
    S07 scoring console -> tap Stream Overlay -> S22 copy browser source URL into OBS Studio
    happy path clicks: 2
    edge: Internet drop reconnects WebSocket automatically; custom sponsor banner overlay toggled
```

## Components

| component | variants | states | used on |
| --- | --- | --- | --- |
| PrimaryButton | solid, outline, ghost, danger | default, hover, focus, disabled, loading | S01, S03, S04, S05, S06, S11, S15 |
| RunsKeypad | grid (0, 1, 2, 3, 4, 6) | default, pressed, disabled | S07 |
| ExtrasBar | buttons (Wide, No-Ball, Bye, Leg-Bye) | default, selected, disabled | S07 |
| DeliveryCircleChip | dot, 1-3, four (blue), six (green), wicket (red), extra | default, current, historical | S07, S10, S13 |
| ActiveBatterBowlerCard | striker, non-striker, bowler | active, on-strike indicator, bowling | S07 |
| DismissalModal | full-screen sheet | default, selecting fielder, submitting | S08 |
| RadialGroundCanvas | interactive 360-degree field | default, hovered zone, zone selected | S09 |
| ScoreTickerStrip | standard broadcast, compact, minimal | normal, boundary animation, wicket flash | S22 |
| ScorecardTable | batting card, bowling card, FOW table | standard, expanded details | S13 |
| PointsTableGrid | group standings | sorted by Pts/NRR, highlighted playoff spots | S18 |
| ManhattanChart | bar chart (runs per over) | innings 1 bars, innings 2 comparison | S14 |
| WormChart | line graph (cumulative runs) | live comparison curve, wicket markers | S14 |
| StatMetricPill | runs, wickets, avg, strike rate | default, highlighted | S07, S13, S19, S20 |
| UndoActionButton | icon button with label | enabled, disabled (when ball stack is empty) | S07 |
| QuickActionFAB | floating circular action button | default, expanded menu | S02 |

## Inferred data model

```
User          id, phone, name, email, avatar_url, role (player | scorer | organizer), created_at
              evidence: S01 auth screen, user profile settings
              confidence: high

Player        id, user_id, display_name, primary_role (batter | bowler | all_rounder | keeper),
              batting_style (rhb | lhb), bowling_style (fast | spin | seam | none), city, bio
              evidence: S01 role setup, S20 player profile, S04 squad selection
              confidence: high

Team          id, name, short_name, logo_url, city, captain_id, created_by_user_id
              evidence: S03 team picker, S21 team profile, S04 squad selection
              confidence: high

TeamMember    id, team_id, player_id, role (captain | vice_captain | wicket_keeper | player), joined_at
              evidence: S04 playing XI selection, S21 roster list
              confidence: high

Tournament    id, name, organizer_id, category (open | corporate | school | box), ball_type,
              start_date, end_date, banner_url, rules (json: overs, powerplay_rules)
              evidence: S15 tournament setup, S16 format setup, S18 standings
              confidence: high

TournamentGroup id, tournament_id, name (e.g. Group A, Group B), round_number
              evidence: S16 rounds and groups setup, S18 group standings tabs
              confidence: high

TournamentStanding id, tournament_group_id, team_id, played, won, lost, tied, no_result,
              points, runs_scored, overs_faced, runs_conceded, overs_bowled, net_run_rate
              evidence: S18 points table columns, automated ICC NRR formula
              confidence: high

Match         id, tournament_id (optional), team_a_id, team_b_id, match_type (limited_overs | box | test),
              total_overs, ball_type (tennis | leather | tape), ground_name, match_date,
              toss_winner_team_id, toss_decision (bat | bowl), status (scheduled | live | completed | abandoned),
              winner_team_id, win_margin_text, player_of_match_id, scorer_user_id
              evidence: S03 match setup, S05 toss, S12 match result
              confidence: high

MatchOfficial id, match_id, user_id, role (umpire | scorer | commentator)
              evidence: S03 match setup officials selection, community umpire listings
              confidence: medium

Innings       id, match_id, innings_number (1 | 2), batting_team_id, bowling_team_id,
              total_runs, total_wickets, total_overs, extras (json: wides, no_balls, byes, leg_byes, penalties)
              evidence: S07 live console, S11 innings break, S13 full scorecard
              confidence: high

Over          id, innings_id, over_number, bowler_player_id, total_runs, total_wickets, is_maiden
              evidence: S07 over circles, S10 bowler handover, S13 scorecard overs list
              confidence: high

Delivery      id, over_id, ball_number (legal 1-6), striker_player_id, non_striker_player_id,
              bowler_player_id, runs_scored, is_extra (boolean), extra_type (wide | no_ball | bye | leg_bye | penalty | none),
              extra_runs, is_wicket (boolean), shot_zone (0-360 deg or wagon zone), is_free_hit
              evidence: S07 ball-by-ball entry, S09 wagon wheel, S13 commentary feed
              confidence: high

Dismissal     id, delivery_id, out_player_id, dismissal_type (bowled | caught | run_out | stumped | lbw | hit_wicket | retired),
              bowler_player_id, fielder_player_id, run_out_end (striker | non_striker)
              evidence: S08 dismissal dialog, S13 scorecard fall of wickets
              confidence: high

Award         id, player_id, tournament_id, match_id, award_type (mvp | highest_scorer | best_bowler | centurion | hat_trick)
              evidence: S12 player of match card, S19 tournament awards, S20 profile badges
              confidence: medium
```

Relationships:
- `User` 1-1 `Player`
- `Team` 1-n `TeamMember`, `Player` 1-n `TeamMember`
- `Tournament` 1-n `TournamentGroup`, `TournamentGroup` 1-n `TournamentStanding`
- `Tournament` 1-n `Match`, `Team` 1-n `Match` (as team_a or team_b)
- `Match` 1-2 `Innings`
- `Innings` 1-n `Over`, `Over` 1-n `Delivery`
- `Delivery` 0-1 `Dismissal`
- `Player` 1-n `Award`

## Feature matrix

See `replica/features.csv`.
- Must: 24
- Should: 6
- Could: 3
- Skip (out of scope): 3
Total tracked features: 36

## Out of scope (cannot or should not be cloned)

- **CricHeroes Capture Hardware**: Physical ground-mounted automated video cameras and bespoke camera firmware.
- **The Dressing Room E-Commerce Store**: Physical cricket gear warehouse, inventory shipping, and return logistics.
- **Proprietary Ad Network & Brand Deals**: Exclusive brand partnerships and corporate sponsorships running across CricHeroes network.
- **The 35M+ Grassroots Player Network**: Proprietary user identity network and historical match database.

## Size

Screens: 24, Flows: 9, Entities: 14.
Hard parts:
1. **Cricket Rules & Ball-by-Ball State Machine**: Automated strike rotation on odd runs, over-end strike swaps, complex extras (wides/no-balls not advancing ball counter, free hits, byes off wide), bowler quota and consecutive-over validation, and bulletproof Undo stack.
2. **Automated Dynamic NRR & Points Table Engine**: Standard ICC Net Run Rate formula factoring total runs and legal overs faced vs conceded across variable-length or rain-reduced matches.
3. **Realtime Broadcast Synchronization**: Zero-latency delivery updates from the scorer's console to the public scorecard and OBS lower-third web overlay via WebSockets.

Size: **M** (3–4 weeks for a clean functional MVP covering match scoring, ICC scorecard, tournament NRR standings, and live OBS overlay).
