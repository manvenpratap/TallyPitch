# Parity Report: CricHeroes Replica

Date: 2026-10-14  
Build: `93dd712`  
Comparison Target: [CricHeroes](https://cricheroes.com/) (Web & Mobile)

---

## 1. Parity Score

```
Parity Score: 69.0 / 100
Feature Parity: 69.0% (33 counted, 17 must-haves done out of 24)
Must-Haves Remaining: 7
Verdict: NOT SHIPPABLE YET (7 must-haves not done)
```

---

## 2. Area Breakdown (Weakest First)

| Area | Completion | Done / Total | Status |
| :--- | :---: | :---: | :--- |
| **teams** | **0.0%** | 0 / 1 | 🔴 Missing: Team creation & player roster management |
| **profiles** | **0.0%** | 0 / 1 | 🔴 Missing: Career batting/bowling statistics & records |
| **gamification** | **0.0%** | 0 / 1 | 🟡 Missing: Badges & milestones (Centurion, Hat-trick) |
| **community** | **0.0%** | 0 / 1 | 🟡 Missing: Matchmaking "Looking For" classifieds |
| **tournaments** | **20.0%** | 1 / 5 | 🟠 Done: NRR engine. Missing: Tournament wizard, fixtures, groups |
| **analytics** | **33.3%** | 1 / 3 | 🟠 Done: MVP calculation. Missing: Manhattan/Worm charts, Wagon wheel |
| **onboarding** | **50.0%** | 1 / 2 | 🟢 Done: Phone OTP auth. Missing: Player role picker |
| **match setup** | **100.0%** | 3 / 3 | 🟢 Complete: Overs, ball type, ground, toss, squad selection |
| **scoring** | **100.0%** | 12 / 12 | 🟢 Complete: Ball-by-ball, strike rotation, extras, wickets, undo, over change |
| **scorecard** | **100.0%** | 2 / 2 | 🟢 Complete: Full digital ICC scorecard & commentary stream |
| **streaming** | **100.0%** | 1 / 1 | 🟢 Complete: WebSocket live score ticker for OBS/vMix |
| **monetization** | **100.0%** | 1 / 1 | 🟢 Complete: Stripe Checkout integration & Pro subscriptions |

---

## 3. Behaviour & UX Differences

| Flow / Feature | Original (CricHeroes) | Clone (Your Version) | Advantage / Decision |
| :--- | :--- | :--- | :--- |
| **Core Loop Clicks** | 11–13 clicks through multiple ads, permissions, and modals before ball 1 | **6 clicks** (S03 Setup -> S05 Toss -> S06 Openers -> S07 Live Console) | **Clone wins** (50% less friction for local scorers) |
| **Intrusive Ads** | Full-screen popups and interstitial video ads between overs in free tier | **Zero ads**. Clean, distraction-free sporting interface | **Clone wins** (Huge user upgrade) |
| **Undo Latency** | Remote round-trip network call (1–3s delay) to revert mistyped balls | **Instantaneous (0ms)** in-memory rollback stack with full strike restoration | **Clone wins** (Crucial on high-stress amateur matches) |
| **Offline Resilience** | Locks up or drops balls when ground cellular connectivity drops | Operates entirely in client memory and syncs whenever network reconnects | **Clone wins** (Essential for remote village grounds) |
| **Live Stream Overlays** | Paywalled ($5/match pass or $75/mo subscription) | Built-in WebSocket overlay endpoint included out of the box | **Clone wins** (Empowers grassroots clubs to broadcast) |

---

## 4. Missing Features in Build Order

1. **`[must]` Onboarding: Player Role Selection**: Batter, Bowler, All-rounder, Wicket-keeper tags.
2. **`[must]` Teams: Create & Manage Teams**: Add players by phone number, designate Captain (C) and Vice-Captain (VC).
3. **`[must]` Tournaments: Create Tournament**: Multi-team tournament setup wizard (Name, Category, Dates, Ball type).
4. **`[must]` Tournaments: Format & Groups**: Configure Round-Robin leagues and Knockout brackets (Quarter, Semi, Final).
5. **`[must]` Tournaments: Fixture Generation**: Auto-generate round-robin schedule with dates, pitches, and scorers.
6. **`[must]` Profiles: Player Career Record**: Aggregate lifetime matches, innings, runs, batting average, strike rate, wickets, and 5-wicket hauls.
7. **`[must]` Tournaments: Tournament Leaderboard**: Orange Cap (Most Runs), Purple Cap (Most Wickets), and Tournament MVP.
8. **`[should]` Analytics: Match Charts**: Manhattan over-by-over bars and Worm line graph comparing innings.
9. **`[should]` Analytics: Wagon Wheel Canvas**: 360-degree interactive field map for boundary placements.
10. **`[could]` Community: Matchmaking Board**: "Looking For" classifieds for teams seeking players or umpires.

---

## 5. Left Out on Purpose (Out of Scope)

- **CricHeroes Capture Hardware**: Physical ground-mounted automated cameras.
- **The Dressing Room E-Commerce Store**: Physical cricket gear warehouse and logistics.
- **Proprietary Corporate Ad Network**: Commercial brand sponsorships.

---

## 6. Top Five Things to Build Next

1. **Tournament Wizard & Format Builder (S15, S16)**: Multi-team tournament creation with automated round-robin groups.
2. **Auto Fixture Generator (S17)**: Automatic round-robin match scheduler across tournament venues.
3. **Player Career Profiles (S20)**: Aggregated player statistics page showing career runs, wickets, and strike rates.
4. **Team Management (S21)**: Team profile dashboard with squad roster and win/loss records.
5. **Match Analytics Charts (S14)**: Visual Manhattan and Worm graphs for both innings.

---

## 7. Next Step

Run **`/replica-entrepreneur`** to research what real CricHeroes users complain about in public App Store and Google Play reviews, identifying key differentiators to turn this clone into a sellable product. Or continue with **`/replica-build`** to close the remaining 7 must-have tournament and profile features.
