# Project Context & Working Memory

**Last Updated:** 2026-10-18 12:01:34
**Version:** 1.8.0  
**Stack:** Single-File Web (SPA) / Progressive Web App (PWA) / Node.js Backend / Supabase PostgreSQL / Playwright / MQTT 3.1.1 Bridge / Android TWA  

---

## 1. Current Status & Milestone
- **Active Phase**: Milestone 16 Completed — Android TWA & Native APK Packaging (`app.tallypitch.twa`) Live & Verified!
- **Test Health**: 100% Passing (42 e2e Playwright tests passing across 10 modules: `test_cricket_engine.py`, `test_wagon_wheel_and_charts.py`, `test_realtime_bridge.py`, `test_community_and_badges.py`, `test_ground_and_insights.py`, `test_pwa_offline.py`, `test_social_card_exporter.py`, `test_dls_engine.py`, `test_tournament_realtime.py`, and `test_android_packaging.py`)
- **Distribution Health**: Synced (`dist/index.html`, `dist/manifest.json`, `dist/sw.js`, `dist/.well-known/assetlinks.json`, `dist/icon-*.png` byte-for-byte in parity)
- **Feature Parity**: 100.0% against CricHeroes (33/33 core features completed) + Advanced Intelligence + Social Media Graphics Engine (S16) + DLS Standard Edition Engine (S07) + Real-time Tournament Stream (S18) + Android TWA Packaging

---

## 2. Implemented Features
- [x] **Android TWA & Native APK Packaging (Track 3 & Modal 10)**: Google Trusted Web Activity (TWA) architecture (`app.tallypitch.twa`) wrapping TallyPitch with zero URL browser chrome, full-screen viewport, Min SDK 21, and Target SDK 34 (Android 14). Includes complete Gradle project structure (`android/app/build.gradle`, `AndroidManifest.xml`, `twa-manifest.json`), Google Digital Asset Links (`.well-known/assetlinks.json`), launcher mipmap drawables, Modal 10 UI with direct PWA install prompt, Bubblewrap/Gradle build instructions, and standalone validation engine (`scripts/build_android_twa.py`).
- [x] **Real-time Tournament Standings Stream (Track 2 & S18)**: Native pub/sub streaming integration for tournament tables via CricHeroes topic architecture (`cricheroes/tournaments/{tournament_id}/standings`). Node.js binary MQTT 3.1.1 packet encoding/decoding, dual WebSocket broadcast, S18 live stream telemetry badge, manual push trigger button, cross-tab BroadcastChannel and storage listeners, and automated standings recalculation (played, won, lost, points, NRR) on match conclusion.
- [x] **Duckworth-Lewis-Stern (DLS) Standard Edition Engine (S07)**: Full client-side ICC Standard Edition DLS rain rule engine. Embedded 20-over resource matrix (`DLS_RESOURCES_T20` across 0..20 overs remaining and 0..9 wickets lost), mathematical target revision calculator (`R2 / R1 * S`), live DLS Par Score HUD on S07 with dynamic ahead/behind badge (`+X (Ahead)`, `-X (Behind)`, `Par Tied`), and Modal 9 (`#dls-modal`) with target revision calculator, live par score matrix, and official DLS match stoppage decision handler.
- [x] **Social Match Graphic & Award Card Exporter (S16)**: Native client-side HTML5 Canvas (1080x1080) high-resolution graphic exporter for WhatsApp and Instagram. Dual-mode generator supporting two-innings match scorecards with top performers, result banner, and MVP spotlight, or individual Player of the Match certificate award cards. Includes 1-click PNG download, image clipboard copy, Web Share API integration, and trigger buttons across S07, S13, S21, and the match result modal.
- [x] **Ground & Pitch Intelligence Engine (Track A)**: Multi-venue ground telemetry (Wankhede, Oval Maidan, Chinnaswamy, Kotla) rendering toss win ratios (Bat 1st vs Chasing %), benchmark 1st/2nd innings averages, pace vs spin economies/wickets, and 4-way dismissal breakdown (Caught, Bowled, LBW, Run Out).
- [x] **Match Setup Venue Telemetry Preview (S03)**: Instant pitch conditions preview pill on ground dropdown selection.
- [x] **Live Match Win Predictor HUD (Track B)**: Un-paywalled real-time win probability meter on S07 calculating CRR, RRR, wickets in hand, and venue historical benchmarks with dynamic team bars.
- [x] **Wagon Wheel Field Vulnerability Heatmap**: CricInsights tactical overlay highlighting boundary hazards (74% scoring zone) and dot-ball traps on 360° SVG turf.
- [x] **CricInsights Player Scouting Query Engine (S06)**: Multi-metric grassroots search engine filtering squads by role, batting strike rate, bowling economy, and captaincy.
- [x] **Native PWA & Offline Service Worker (Track C)**: Web App Manifest (`manifest.json`), standalone display mode, 192x192 & 512x512 app icons, cache-first Service Worker (`sw.js`), and header network status badge (Online/Ground Offline).
- [x] **Zero-Ad Scoring Console (S07)**: Full ball-by-ball scoring keypad (0-6, extras, wickets) with 0ms atomic rollback.
- [x] **Player Milestone Badges & Honors (S21)**: Auto-awarded career achievements (Centurion, 5x Fifties, Fifer 5-Wkt, Hat-Trick Club, Maximum Striker, Maiden Master, Match MVP, Safe Hands) with unlocked counter and accessible tooltips.
- [x] **Community Matchmaking Board (S23)**: Grassroots cricket classifieds for finding players, joining teams, booking umpires, and securing grounds with category filter tabs and classified posting modal.
- [x] **CricHeroes MQTT 3.1.1 Realtime Bridge (Track 1)**: Dual-mode broker in `server/realtime.js` supporting binary MQTT packets (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ), subprotocols (`mqtt`, `mqttv3.1`), topic filters (`+`, `#`), and JSON pub/sub on ports 1884/8884/4000.
- [x] **CricHeroes Forensic Data Schemas**: Ball-by-ball events broadcast to `cricheroes/matches/{id}/ball` with polar vector wagon wheel coordinates (`zone`, `angle_degrees`, `distance_pct`) and live score summaries to `cricheroes/matches/{id}/score`.
- [x] **Broadcast-Grade OBS Lower-Third Overlay**: Dedicated transparent graphics route (`?overlay=true` / `?view=overlay`) rendering live team badge, runs/wickets, overs, CRR, RRR, active batsmen, bowler figures, and over delivery chips with 0ms cross-tab `BroadcastChannel` synchronization.
- [x] **Scorer Streaming Hub Modal**: S07 streaming console button (`📡 OBS Stream`), instant copyable browser source URL, topic inspector, and live animation test triggers.
- [x] **Interactive 8-Zone SVG Wagon Wheel (S09)**: Real-time shot placement on cricket turf canvas with polar vector coordinates (angle 0-360°, distance %, zones 1-8).
- [x] **Match Setup & Toss (S03)**: Team configuration, overs selection (5-20), ball types, 3D toss animation, and opener selection.
- [x] **Digital Scorecard (S13)**: Official ICC scorecard with batting, bowling, fall-of-wickets timeline, and commentary.
- [x] **Visual Match Progression Charts (S14)**: SVG over-by-over Manhattan runs bar chart, cumulative Worm curve with Fall of Wickets pins, match shot direction filter, and 3-phase match breakdown.
- [x] **Tournament Hub (S05)**: Multi-stage tournament management with Pool A/B round-robin tables, knockout brackets, and fixtures.
- [x] **Automated Net Run Rate (NRR)**: Standard ICC formula dynamically computed to 3 decimal places.
- [x] **Team Rosters & Player Profiles (S06)**: Squad management, player career statistics, strike rates, and bowling economies.
- [x] **Offline-First Resilience**: In-memory state storage, local `BroadcastChannel`, and Service Worker caching ensure uninterrupted scoring on grounds with dropped cellular signal.
- [x] **Backend & Database Infrastructure**: Node.js REST API (`server/api.js`), WebSocket server (`server/realtime.js`), Supabase auth, and 16 PostgreSQL tables with RLS.
- [x] **Universal Pipeline Integration**: Standalone `./pipeline.sh` runner, accessible tooltips, automated test summary reporter, and distribution synchronizer.

---

## 3. Core Architecture & Constraints
1. **Zero Ads in the Box**: The matchday scoring interface must never display interruptive video ads or full-screen interstitials.
2. **0ms Atomic Rollback**: Delivery undos must immediately restore innings runs, overs, wickets, and striker positions without server roundtrip delay.
3. **Distribution Parity**: `dist/index.html` must always be synchronized before shipping.
4. **Deterministic Testing**: All Playwright test cases across all test modules must run and pass without critical console errors.

---

## 4. Active Roadmap
- [x] Milestone 1: Core scoring engine, match flows, and scorecard generation
- [x] Milestone 2: Tournament standings, NRR engine, team rosters, and career profiles
- [x] Milestone 3: Clean up replica meta-tooling and establish standalone repository
- [x] Milestone 4: Setup Universal Pipeline (doctor, heal, test, ship) and self-healing test harness
- [x] Milestone 5: Forensic REA analysis of CricHeroes XAPK (v26.5.1), extract MQTT realtime protocols, and data schemas (Wagon Wheel, Manhattan, Worm charts) documented in `replica/cricheroes_spec.md`
- [x] Milestone 6: Build interactive 8-zone SVG Wagon Wheel (S09) and Match Progression charts (Manhattan, Worm, Phases in S14) reaching 97.2% CricHeroes parity.
- [x] Milestone 7 (Track 1): Implement CricHeroes-compatible MQTT realtime protocol bridge, binary packet encoding/decoding, dual-stack WebSockets, and transparent OBS lower-third live streaming overlay.
- [x] Milestone 8 (Track 3): Implement Milestone Badges (S21) & Grassroots Community Matchmaking Board (S23), reaching 100.0% CricHeroes feature parity.
- [x] Milestone 9 (Track A): Build Ground & Pitch Intelligence Engine (`ground_insights` schema: venue selection, toss win rates, pace/spin, dismissals).
- [x] Milestone 10 (Track B): Un-paywall CricInsights PRO with real-time Live Win Predictor, Field Vulnerability Heatmap, and Player Scouting Query Engine.
- [x] Milestone 11 (Track C): Package as installable Progressive Web App (PWA) with offline Service Worker caching and network status HUD.
- [x] Milestone 12 (Track D): Comprehensive test automation (27 passing tests), distribution verification, and release shipping.
- [x] Milestone 13: Build Social Match Summary & Award Card Exporter (S16) via HTML5 Canvas 1080x1080 generator for WhatsApp & Instagram (31 passing tests).
- [x] Milestone 14 (Track 1): Implement Duckworth-Lewis-Stern (DLS) Standard Edition Rain Rule & Target Revision Engine (S07) with Modal 9, live ahead/behind HUD, and stoppage decision handling (35 passing tests).
- [x] Milestone 15 (Track 2): Implement Real-time Tournament Standings Stream (`cricheroes/tournaments/{id}/standings`) with Node.js MQTT pub/sub, S18 live telemetry badge, automated match conclusion standings recalculation, and cross-tab synchronization (39 passing tests).
- [x] Milestone 16 (Track 3): Build Android TWA & Native APK Packaging (`app.tallypitch.twa`) with Gradle project structure, Google Digital Asset Links (`.well-known/assetlinks.json`), Modal 10 UI, and packaging verification suite (42 passing tests).
