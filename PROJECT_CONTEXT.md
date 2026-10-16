# Project Context & Working Memory

**Last Updated:** 2026-10-17 00:10:51
**Version:** 1.0.0  
**Stack:** Single-File Web (SPA) / Node.js Backend / Supabase PostgreSQL / Playwright  

---

## 1. Current Status & Milestone
- **Active Phase**: Production Stabilization & Universal Pipeline Integration
- **Test Health**: 100% Passing (Playwright e2e test suite passing via `./pipeline.sh test --summary`)
- **Distribution Health**: Synced (`dist/index.html` byte-for-byte in parity with `index.html`)
- **Workflow Health**: 100% Clean (`./pipeline.sh doctor` reports 0 drift)

---

## 2. Implemented Features
- [x] **Zero-Ad Scoring Console (S07)**: Full ball-by-ball scoring keypad (0-6, extras, wickets) with 0ms atomic rollback.
- [x] **Match Setup & Toss (S03)**: Team configuration, overs selection (5-20), ball types, 3D toss animation, and opener selection.
- [x] **Digital Scorecard (S13)**: Official ICC scorecard with batting, bowling, fall-of-wickets timeline, and wagon wheel charts.
- [x] **Tournament Hub (S05)**: Multi-stage tournament management with Pool A/B round-robin tables, knockout brackets, and fixtures.
- [x] **Automated Net Run Rate (NRR)**: Standard ICC formula dynamically computed to 3 decimal places.
- [x] **Team Rosters & Player Profiles (S06)**: Squad management, player career statistics, strike rates, and bowling economies.
- [x] **Free Broadcast OBS Overlay**: Dedicated URL parameter (`?overlay=true`) for live lower-third streaming graphics.
- [x] **Offline-First Resilience**: In-memory state storage ensures uninterrupted scoring on grounds with dropped cellular signal.
- [x] **Backend & Database Infrastructure**: Node.js REST API (`server/api.js`), WebSocket server (`server/realtime.js`), Supabase auth, and 16 PostgreSQL tables with RLS.
- [x] **Universal Pipeline Integration**: Standalone `./pipeline.sh` runner, accessible tooltips, automated test summary reporter, and distribution synchronizer.

---

## 3. Core Architecture & Constraints
1. **Zero Ads in the Box**: The matchday scoring interface must never display interruptive video ads or full-screen interstitials.
2. **0ms Atomic Rollback**: Delivery undos must immediately restore innings runs, overs, wickets, and striker positions without server roundtrip delay.
3. **Distribution Parity**: `dist/index.html` must always be synchronized before shipping.
4. **Deterministic Testing**: All Playwright test cases in `tests/test_cricket_engine.py` must run and pass without critical console errors.

---

## 4. Active Roadmap
- [x] Milestone 1: Core scoring engine, match flows, and scorecard generation
- [x] Milestone 2: Tournament standings, NRR engine, team rosters, and career profiles
- [x] Milestone 3: Clean up replica meta-tooling and establish standalone repository
- [x] Milestone 4: Setup Universal Pipeline (doctor, heal, test, ship) and self-healing test harness
