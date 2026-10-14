# CricHeroes Replica - Build Log

Tracks progress screen by screen according to `replica/recon.md` and `replica/features.csv`.

| ID | Screen Name | Date | Status | Missing / Deferred | Hard Parts / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S03 | Match Setup | 2026-10-14 | Done | Custom powerplay rules | Clean team name binding and quick over steppers (5 to 20 overs) |
| S05 | The Toss | 2026-10-14 | Done | Sound effects on coin landing | 3D CSS coin flip animation with heads/tails randomized landing and manual override |
| S06 | Openers & Bowler Selection | 2026-10-14 | Done | Bench sub list | Roster validation ensuring striker != non-striker before ball 1 |
| S07 | Live Scoring Console | 2026-10-14 | Done | Wagon wheel radial prompt popup | Atomic strike rotation on odd runs, over-end strike flip, extra ball counting, and instant rollback undo stack |
| S08 | Wicket Dismissal Dialog | 2026-10-14 | Done | Direct retired hurt mode | Modal covering 6 dismissal types, bowler wicket attribution (run out non-credited), and dynamic next batter roster |
| S10 | End of Over Handover | 2026-10-14 | Done | Bowler max quota alert | Enforces non-consecutive bowler validation and prompts over summary |
| S11 | Innings Break & Target | 2026-10-14 | Done | DLS rain calculator | Target score calculation (`Innings 1 + 1`), live required run rate (RRR) and chase banner |
| S12 | Match Result & Summary | 2026-10-14 | Done | Share image generator | Winner announcement by runs/wickets, tie detection, and automated weighted MVP calculation |
| S13 | Full Match Scorecard | 2026-10-14 | Done | PDF export | ICC standard scorecard with batting SR, bowling Eco, FOW timeline, extras, and live ball-by-ball commentary |
| S15 | Create Tournament Wizard | 2026-10-14 | Done | Multi-venue selector | Full wizard specifying name, category (Club/Corporate/Box/School), dates, and ball type |
| S16 | Tournament Format & Groups | 2026-10-14 | Done | Custom qualification rules | Pool A/B stage definition with automated progression to semi-finals/finals |
| S17 | Auto Fixtures Generator | 2026-10-14 | Done | Weather delays integration | Automated round-robin match scheduler across venues with time slots and live status |
| S18 | Dynamic Points Table & NRR | 2026-10-14 | Done | Bonus point configuration | ICC standard NRR calculation (`Runs/Overs Scored - Runs/Overs Conceded`) sorting standings |
| S19 | Tournament Leaderboard | 2026-10-14 | Done | Filter by stage | Orange Cap (runs), Purple Cap (wickets), and Tournament MVP leaderboards |
| S20 | Digital Player Career Record | 2026-10-14 | Done | Career milestone timeline | Full career statistics card: matches, innings, runs, average, strike rate, best bowling, and economy |
| S21 | Team Squad Roster Manager | 2026-10-14 | Done | Player transfer requests | Roster editor with Captain (C) / Wicket-keeper (WK) flags and S01 role badges (Batter/Bowler/All-Rounder/Keeper) |
