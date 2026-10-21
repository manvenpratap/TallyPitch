# Graph Report - TallyPitch  (2026-10-21)

## Corpus Check
- 75 files · ~137,578 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 752 nodes · 755 edges · 68 communities (65 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b96fa9f0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_3D WebGL Stadium & Visual Scene Engine|3D WebGL Stadium & Visual Scene Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_3D WebGL Stadium & Visual Scene Engine|3D WebGL Stadium & Visual Scene Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_Tournament Realtime Automated Test Suite|Tournament Realtime Automated Test Suite]]
- [[_COMMUNITY_Social Card Exporter Automated Test Suite|Social Card Exporter Automated Test Suite]]
- [[_COMMUNITY_Realtime MQTT 3.1.1 & WebSocket Streaming Bridge|Realtime MQTT 3.1.1 & WebSocket Streaming Bridge]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Compare Vs Engine Automated Test Suite|Compare Vs Engine Automated Test Suite]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Community And Badges Automated Test Suite|Community And Badges Automated Test Suite]]
- [[_COMMUNITY_Pwa Offline Automated Test Suite|Pwa Offline Automated Test Suite]]
- [[_COMMUNITY_Android Packaging Automated Test Suite|Android Packaging Automated Test Suite]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_3D WebGL Stadium & Visual Scene Engine|3D WebGL Stadium & Visual Scene Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Contributing Module Core|Contributing Module Core]]
- [[_COMMUNITY_Wagon Wheel And Charts Automated Test Suite|Wagon Wheel And Charts Automated Test Suite]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Universal Pipeline & CICD Health Automation|Universal Pipeline & CI/CD Health Automation]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_Database Layer, Relational Schema & Storage|Database Layer, Relational Schema & Storage]]
- [[_COMMUNITY_Database Layer, Relational Schema & Storage|Database Layer, Relational Schema & Storage]]
- [[_COMMUNITY_Tooltip Module Core|Tooltip Module Core]]
- [[_COMMUNITY_Conftest Module Core|Conftest Module Core]]
- [[_COMMUNITY_Product Module Core|Product Module Core]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Home Module Core|Home Module Core]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_DLS Target Calculation & Rain Rule Engine|DLS Target Calculation & Rain Rule Engine]]
- [[_COMMUNITY_Readme Module Core|Readme Module Core]]
- [[_COMMUNITY_AST Parsing & Semantic Syntax Tree Engine|AST Parsing & Semantic Syntax Tree Engine]]
- [[_COMMUNITY_Multi-Broker Execution & Order Gateway|Multi-Broker Execution & Order Gateway]]
- [[_COMMUNITY_Match Ball Scoring & State Engine|Match Ball Scoring & State Engine]]
- [[_COMMUNITY_Database Layer, Relational Schema & Storage|Database Layer, Relational Schema & Storage]]
- [[_COMMUNITY_Sw Module Core|Sw Module Core]]
- [[_COMMUNITY_Security Module Core|Security Module Core]]
- [[_COMMUNITY_validate_android_project() Subsystem|validate_android_project() Subsystem]]
- [[_COMMUNITY_TallyPitch Wiki(Home) Subsystem|[TallyPitch Wiki](Home) Subsystem]]
- [[_COMMUNITY_Test Plan CricHeroes Replica Subsystem|Test Plan: CricHeroes Replica Subsystem]]
- [[_COMMUNITY_CricHeroes Replica - Build Log Subsystem|CricHeroes Replica - Build Log Subsystem]]
- [[_COMMUNITY_build.gradle Subsystem|build.gradle Subsystem]]
- [[_COMMUNITY_settings.gradle Subsystem|settings.gradle Subsystem]]
- [[_COMMUNITY_build.gradle Subsystem|build.gradle Subsystem]]
- [[_COMMUNITY_tailwind.config.js Subsystem|tailwind.config.js Subsystem]]
- [[_COMMUNITY__Footer.md Subsystem|_Footer.md Subsystem]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 17 edges
2. `Component Specifications: CricHeroes Clone` - 16 edges
3. `TestTallyPitchFlows` - 13 edges
4. `API` - 10 edges
5. `Recon map: CricHeroes (Mobile Web & App)` - 10 edges
6. `TestGroundAndInsights` - 8 edges
7. `requestHandler()` - 8 edges
8. `TallyPitch - Marketing Landing Page Copy & Architecture` - 8 edges
9. `TestDlsEngine` - 7 edges
10. `TestRealtimeBridge` - 7 edges

## Surprising Connections (you probably didn't know these)
- `requestHandler()` --calls--> `sendPhoneOTP()`  [EXTRACTED]
  server/api.js → server/auth.js
- `requestHandler()` --calls--> `verifyPhoneOTP()`  [EXTRACTED]
  server/api.js → server/auth.js
- `requestHandler()` --calls--> `broadcastTournamentStandings()`  [EXTRACTED]
  server/api.js → server/realtime.js
- `requestHandler()` --calls--> `broadcastMatchEvent()`  [EXTRACTED]
  server/api.js → server/realtime.js
- `requestHandler()` --calls--> `createProCheckoutSession()`  [EXTRACTED]
  server/api.js → server/stripe.js

## Communities (68 total, 3 thin omitted)

### Community 0 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.08
Nodes (32): { createProCheckoutSession, handleStripeWebhook }, http, { parse }, readBody(), requestHandler(), sendJSON(), { sendPhoneOTP, verifyPhoneOTP }, server (+24 more)

### Community 1 - "Match Ball Scoring & State Engine"
Cohesion: 0.12
Nodes (21): DocBuilder, file_sha256(), GitOrchestrator, log_error(), log_step(), log_success(), log_warn(), main() (+13 more)

### Community 2 - "Match Ball Scoring & State Engine"
Cohesion: 0.06
Nodes (31): ActiveBatterBowlerCard, code:block1 (PrimaryButton), code:block10 (PointsTableGrid), code:block11 (ManhattanChart), code:block12 (WormChart), code:block13 (StatMetricPill), code:block14 (UndoActionButton), code:block15 (QuickActionFAB) (+23 more)

### Community 3 - "Match Ball Scoring & State Engine"
Cohesion: 0.08
Nodes (11): F04-H1: Dismissal modal, bowler attribution, and fall of wicket, F05-H1: 6 legal balls trigger over completion modal and bowler handover, F06-H1: Rollback delivery and verify complete restoration of match state, F08-H1: Digital scorecard populated with live commentary stream, F09-H1: Tournament management hub, fixtures, NRR standings, and cap leaderboards, F10-H1: Team squad management, role assignments (S01, S21), and digital career r, F01-H1: Setup match, record toss, select openers, and enter live console, F02-H1: Ball scoring and automatic strike rotation on odd runs (+3 more)

### Community 4 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.09
Nodes (21): 1. Executive Summary & Architectural Overview, 2. Infrastructure & Discovered Server Endpoints, 3.1 Topic Architecture, 3.2 MQTT Ball Event Payload Structure, 3. Realtime MQTT Scoring Protocol, 4.1 Wagon Wheel Engine (`match_insights_wagon_wheel`), 4.2 Match Progression (Manhattan & Worm Curves), 4.3 Phase-of-Play Head-to-Head Analytics (+13 more)

### Community 5 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.1
Nodes (20): 1. Vertical Slice (Core Loop End-to-End), 2. Must-Haves (Complete Gameplay & Tournaments), 3. Should-Haves (Analytics & Broadcast Tools), 4. Could-Haves & Fixes from `/replica-entrepreneur`, API, Architecture: CricHeroes Replica (a rebuild of CricHeroes's core features), Build order, F01: Quick Match Setup & Initialization (+12 more)

### Community 6 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.1
Nodes (19): 1. Hero Section, 2. The Problem: What Grassroots Scorers Dread, 3. How It Works: Matchday in 3 Steps, 4. Key Differentiators: Built Around the Fixes, 5. Transparent Pricing, 6. Frequently Asked Questions, 7. Final Call to Action, Problem 1: Missed Deliveries from Full-Screen Video Popups (+11 more)

### Community 7 - "3D WebGL Stadium & Visual Scene Engine"
Cohesion: 0.11
Nodes (17): 1. The Name, 2. Name Screening Checks, 3. Brand Color Palette & Tokens, 4. Logo & Visual Mark Brief, 5. Voice & Copy Guide, 6. Rebrand Sweep Status, code:json ({), code:text (AAA   17.85:1  text           on bg) (+9 more)

### Community 8 - "Match Ball Scoring & State Engine"
Cohesion: 0.12
Nodes (6): Verify Screen S06 Player Scouting Engine filters players by role, strike rate, a, Verify S14 Venue & Pitch Intelligence renders win ratio, benchmarks, pace/spin,, Verify S03 Match Setup updates instant venue telemetry preview badge on selectio, Verify S07 Live Scoring Console displays un-paywalled Win Predictor and updates, Verify S14 Wagon Wheel toggles CricInsights Field Vulnerability Heatmap overlay, TestGroundAndInsights

### Community 9 - "3D WebGL Stadium & Visual Scene Engine"
Cohesion: 0.14
Nodes (15): assert_no_critical_errors(), catalog_screenshots(), check_element_overlaps(), check_no_horizontal_overflow(), get_bounding_boxes(), helpers.py — Universal Playwright Visual Regression & UI Testing Engine Local ma, Saves a full viewport screenshot to the local machine directory.     Never uploa, Generates a zero-cloud local HTML gallery of all captured screenshots for local (+7 more)

### Community 10 - "Match Ball Scoring & State Engine"
Cohesion: 0.12
Nodes (15): 1. Run the Web Application Locally, 2. Backend Services, 3. Database Setup, 4. Running Tests, code:text (TallyPitch/), code:bash (# Using Python's built-in static HTTP server:), code:bash (# 1. Copy environment variables), code:bash (# Apply migrations to your Postgres / Supabase instance:) (+7 more)

### Community 11 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.12
Nodes (15): 1. Offline-First Lifecycle & Data Flow, 📐 1. System Architecture, 🔄 2. Scoring Engine & 0ms Atomic Rollback Workflow, 2. Technology Stack & Component Responsibilities, 3. Formal System Visualizations, ⚡ 3. Realtime Ingestion & OBS Broadcast Sequence, 🌊 4. Match Data Flow Pipeline, ⏱️ 5. Match & Tournament Lifecycle (+7 more)

### Community 12 - "Match Ball Scoring & State Engine"
Cohesion: 0.14
Nodes (5): Verify calling off match after minimum 5 overs declares winner by DLS Method, Verify DLS button on S07, modal markup, and accessible tooltips exist, Verify reducing innings 2 overs computes mathematically revised target and updat, Verify DLS Par Score HUD dynamically displays par runs and ahead/behind badge in, TestDlsEngine

### Community 13 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.14
Nodes (5): Verify delivery events format valid CricHeroes ball payload schema with polar co, Verify Node.js realtime module handles MQTT 3.1.1 packets and CricHeroes topic m, Verify standalone OBS Browser Source rendering (?overlay=true) with transparent, Verify live scoring console (S07) modal opens and exhibits complete broadcast te, TestRealtimeBridge

### Community 14 - "Tournament Realtime Automated Test Suite"
Cohesion: 0.14
Nodes (5): Verify match conclusion calculates points, updates standings, and triggers live, Verify Node.js realtime engine matches tournament MQTT topics and encodes standi, Verify Screen S18 displays live MQTT stream telemetry badge, tooltip, and initia, Verify dynamic DOM update when incoming real-time standings stream event is rece, TestTournamentRealtimeStream

### Community 15 - "Social Card Exporter Automated Test Suite"
Cohesion: 0.14
Nodes (5): Verify completion modal includes direct 'Share Match Graphic (S16)' CTA, Verify modal markup, mode tabs, action buttons and accessible tooltips exist, Verify opening modal from Screen S13 draws 1080x1080 canvas and updates preview, Verify switching mode to Player Award re-renders certificate with selected squad, TestSocialCardExporter

### Community 16 - "Realtime MQTT 3.1.1 & WebSocket Streaming Bridge"
Cohesion: 0.15
Nodes (12): code:block1 (F01 Quick Match Setup & First Ball Bowled), code:block2 (User          id, phone, name, email, avatar_url, role (play), Components, Core loop, Feature matrix, Flows, Inferred data model, Out of scope (cannot or should not be cloned) (+4 more)

### Community 17 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify 1-click 'Score Match' button pre-fills S03 setup, and iCal / clipboard ex, Verify S17 has Auto Scheduler controls and opens Modal 16 with parameters and te, Verify conflict-free schedule generation, preview rendering, and application to, TestAutoSchedulerEngine

### Community 18 - "Compare Vs Engine Automated Test Suite"
Cohesion: 0.17
Nodes (4): Verify opening Compare VS from career profile and from scouting table., Verify Compare VS container, default player comparison, 10 metrics, and marquee, Verify switching to Team vs Team mode, team selectors, and team benchmark metric, TestCompareVsEngine

### Community 19 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify initial S19 honors podium rendering and top-5 batting table, Verify switching between Batting Top 5 and Bowling Top 5 views, Verify dynamic cap honor reassignment when live match stats overtake tournament, TestTournamentLeaderboards

### Community 20 - "Community And Badges Automated Test Suite"
Cohesion: 0.17
Nodes (4): Verify Screen S14 Shot Analysis tab, 4 KPI cards, proportional distribution list, Verify Modal 3 interactive shot chips, zone inference, manual chip selection, an, Verify deliveries record shotType, wagonWheel.shot_type, commentary speech integ, TestShotTypeEngine

### Community 21 - "Pwa Offline Automated Test Suite"
Cohesion: 0.17
Nodes (4): Verify S21 Milestone Badges render cards with proper unlocked/locked states and, Verify S23 Community Board renders listings, counts, and filters correctly, Verify posting a new classified listing prepends card and updates counts dynamic, TestCommunityAndBadges

### Community 22 - "Android Packaging Automated Test Suite"
Cohesion: 0.17
Nodes (4): Verify Web App Manifest and PWA icons are valid and properly structured, Verify sw.js contains proper caching lifecycle and index.html includes manifest, Verify network status indicator badge is visible in header with accessible toolt, TestPwaOffline

### Community 23 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify batter dropdown selector and 0ms atomic undo rollback on radial engine., Verify S14 Wagon Wheel renders 4 Radial KPI cards and the 8-Sector Spray Distrib, Verify 360 SVG turf displays both lofted flight paths and ground lines, with gro, TestRadialSprayEngine

### Community 24 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify Android TWA project structure, Gradle config, and Digital Asset Links, Verify Python Android packaging validator script executes cleanly, Verify Modal 10 opens via header CTA, displays TWA cards, toggles AssetLinks JSO, TestAndroidPackaging

### Community 25 - "3D WebGL Stadium & Visual Scene Engine"
Cohesion: 0.17
Nodes (4): Verify perspective filter buttons (All, Batting, Bowling, Swings) and breakdown, Verify S07 Live Turning Point Alert pill appears on high impact overs and naviga, Verify S14 Turning Points tab renders 4 KPI cards and interactive Momentum Index, TestTurningPointEngine

### Community 26 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify S07 Match Vault button opens Modal 13 with status badges and actions., Verify delivery scoring auto-persists to vault and disaster recovery banner rest, Verify JSON match snapshot schema conforms to tbl_OfflineSyncQueue and imports c, TestMatchVaultEngine

### Community 27 - "Contributing Module Core"
Cohesion: 0.17
Nodes (4): Verify partnership completes on wicket, next partnership begins, and S13 scoreca, Verify initial S07 live partnership card layout, labels, and 0-score state, Verify live partnership updates runs, balls, boundaries, and batter splits as de, TestPartnershipsEngine

### Community 28 - "Wagon Wheel And Charts Automated Test Suite"
Cohesion: 0.17
Nodes (4): Verify boundary 4s, 6s, dots, and coin toss automatically trigger acoustic sound, Verify S07 header contains SFX toggle and Soundboard button opening Modal 15., Verify all 8 soundboard acoustic trigger cards invoke Web Audio API synthesizer., TestStadiumSfxEngine

### Community 29 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify Length x Line matrix table, delivery type filter buttons, and 0ms atomic, Verify delivery automatically attaches pitchLength/pitchLine and Modal 3 display, Verify S14 Pitch Map tab renders 4 KPI cards and 2D Turf Heatmap SVG., TestPitchMapEngine

### Community 30 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify interactive matrix cell spotlight inspection, delivery chips, and 0ms ato, Verify S07 Live Face-Off HUD button, real-time stat updates, Modal 12 opening, s, Verify Screen S14 Face-Off Matrix tab, 4 KPI telemetry cards, matrix table, and, TestFaceOffEngine

### Community 31 - "Match Ball Scoring & State Engine"
Cohesion: 0.17
Nodes (4): Verify 1-click pre-filling of S03 Match Setup from NRR simulator., Verify S18 NRR Calculator card renders with team selectors, presets, and telemet, Verify mathematical calculation of runs allowed, chase overs, and direct clash t, TestNrrScenarioEngine

### Community 32 - "Universal Pipeline & CI/CD Health Automation"
Cohesion: 0.17
Nodes (4): Verify 2-wicket limit, reserve batter rollover, chase target, winner declaration, Verify #btn-launch-super-over is hidden on standard win and visible on match tie, Verify Super Over Modal 11 opens, nominates 3 batters and 1 bowler, and launches, TestSuperOverEngine

### Community 33 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.17
Nodes (4): Verify print trigger invokes window.print and match result modal provides 1-clic, Verify S13 header has Official Scorebook button and opens Modal 14 with full ICC, Verify innings selector filters displayed blocks and officials checkbox toggles, TestScorebookPdfEngine

### Community 34 - "Database Layer, Relational Schema & Storage"
Cohesion: 0.17
Nodes (11): 1. The Three Lists, 2. The Fix Plan, 3. Positioning Angles, 4. Next Step, Fixes and Positioning Plan: CricHeroes Clone, Option A: The Scorer's Sanctuary (Focus on Speed & Zero Ads), Option B: The Transparent League Platform (Focus on Free Broadcast & Pricing) - **RECOMMENDED**, Option C: The Unbreakable Offline Scorer (Focus on Reliability) (+3 more)

### Community 35 - "Database Layer, Relational Schema & Storage"
Cohesion: 0.18
Nodes (3): Test natural language commentary generation with field zones, wickets, boundarie, Test HUD and S13 voice commentary toggle buttons update state and labels, TestVoiceCommentary

### Community 36 - "Tooltip Module Core"
Cohesion: 0.18
Nodes (10): 1. Development Principles, 2. Git & Branching Workflow, 3. Local Verification, 4. Submitting a Pull Request, Branch Naming, code:bash (git config core.hooksPath .githooks), code:bash (# 1. Run doctor check), Commit Messages (+2 more)

### Community 37 - "Conftest Module Core"
Cohesion: 0.2
Nodes (3): Verify opening S09 Wagon Wheel modal, clicking ground canvas, and saving shot pl, Verify S14 Match Progression Charts (Manhattan, Worm, Wagon, Phases) render clea, TestWagonWheelAndCharts

### Community 38 - "Product Module Core"
Cohesion: 0.22
Nodes (8): 1. Multi-Stage Tournament Structure, 2. Automated ICC Net Run Rate (NRR) Calculation, 3. Points Table Sorting Logic, Decimal Overs Conversion Invariant, Storage & Precision, The All-Out Rule, The Formula, Tournament Management & Net Run Rate (NRR)

### Community 39 - "Match Ball Scoring & State Engine"
Cohesion: 0.25
Nodes (7): 1. Mandatory Context Reading, 2. Minimal Tokens Protocol (MANDATORY), 3. Persistent Context Maintenance, 4. Regression Test Suite Rules, 5. UI Tooltips & Accessibility Invariants, 6. Packaging & Release Ship Rule, Project Agent Governance & Pipeline Rules

### Community 40 - "Home Module Core"
Cohesion: 0.25
Nodes (7): 1. Keypad Design & Ball Entry, 2. 0ms Atomic Rollback Architecture, 3. End of Over & Bowler Rotation, 4. Wicket Dismissals & Fall-of-Wickets, Extras Handling, How TallyPitch Solves This, Scoring Engine & 0ms Rollback

### Community 41 - "Match Ball Scoring & State Engine"
Cohesion: 0.25
Nodes (7): 1. Quick Start for Developers, 2. The Universal Pipeline (`./pipeline.sh`), 3. Playwright E2E Test Suite (`tests/`), 4. Single-File Distribution Parity, code:bash (# Clone the repository), code:bash (# 1. Run diagnostic invariant checks), Developer Guide & Universal Pipeline

### Community 42 - "DLS Target Calculation & Rain Rule Engine"
Cohesion: 0.25
Nodes (7): 1. Database & Migrations, 2. Authentication & Sessions, 3. Realtime Live Score Broadcasting, 4. Payments & Subscriptions (Stripe), 5. Security Checklist, 6. Next Steps, Backend Architecture & Security Checklist: CricHeroes Replica

### Community 43 - "Readme Module Core"
Cohesion: 0.25
Nodes (7): 1. Competitor Benchmark Analysis, 2. Reviewer Feedback on Price & Billing, 3. TallyPitch Pricing Tiers, 4. Product Billing Principles & Anti-Pattern Guarantees, 5. Stripe Products and Price IDs, code:bash (# 1. Product: TallyPitch Club Pro), TallyPitch - Pricing Strategy & Structure

### Community 44 - "AST Parsing & Semantic Syntax Tree Engine"
Cohesion: 0.25
Nodes (7): 1. Pre-Launch Beta & Quality Gate, 2. Community Outreach: Reaching Frustrated Users, 3. Product Hunt & Hacker News Launch Strategy, 4. First 10 User Interviews (Hands-on Feedback), Product Hunt Launch, Show HN Post Draft, TallyPitch - Launch & Go-To-Market Plan

### Community 45 - "Multi-Broker Execution & Order Gateway"
Cohesion: 0.43
Nodes (4): createTooltipElement(), getTooltipElement(), positionTooltip(), show()

### Community 46 - "Match Ball Scoring & State Engine"
Cohesion: 0.29
Nodes (5): blank_page(), page_with_data(), conftest.py — Universal Playwright Test Suite Fixtures Provides shared, isolated, Launches headless Chromium, navigates to target local app,     and captures cons, Launches headless Chromium for testing uninitialized or first-run empty states.

### Community 47 - "Database Layer, Relational Schema & Storage"
Cohesion: 0.29
Nodes (6): Operating Context, Platform, Positioning, Product Purpose, Product Specification, Users

### Community 48 - "Sw Module Core"
Cohesion: 0.29
Nodes (6): Color Tokens (TallyPitch Sapphire System), Core Palette, Design System & Theme Foundations, Tooltips & Overlays, Typography, Visual Principles

### Community 49 - "Security Module Core"
Cohesion: 0.29
Nodes (6): 🎯 Core Features & User Guides, 🚀 Quick Links, 🏗️ Technical Architecture & Operations, Welcome to the TallyPitch Wiki 🏏, ⚡ Why TallyPitch?, 📖 Wiki Navigation

### Community 50 - "validate_android_project() Subsystem"
Cohesion: 0.29
Nodes (6): 1. REST API Specification, 2. PostgreSQL Database Schema (`supabase/migrations/`), 3. Data Integrity Invariants, API & Database Reference, Matches & Scoring (`server/api.js`), Tournaments & Standings

### Community 51 - "[TallyPitch Wiki](Home) Subsystem"
Cohesion: 0.33
Nodes (5): 1. Current Status & Milestone, 2. Implemented Features, 3. Core Architecture & Constraints, 4. Active Roadmap, Project Context & Working Memory

### Community 52 - "Test Plan: CricHeroes Replica Subsystem"
Cohesion: 0.33
Nodes (5): code:bash (# Token-efficient summary (recommended for agents & CI)), Running Tests, Test Harness Helpers, Test Inventory, Test Suite: TallyPitch

### Community 53 - "CricHeroes Replica - Build Log Subsystem"
Cohesion: 0.33
Nodes (5): 1. How the Live Overlay Works, 2. OBS Studio Setup (Step-by-Step), 3. Realtime Synchronization, code:text (http://<your-host>/index.html?overlay=true), OBS & Live Broadcast Streaming

### Community 54 - "build.gradle Subsystem"
Cohesion: 0.33
Nodes (5): By area, Completed in this milestone, Left out on purpose (not scored), Parity: 100.0 / 100, Remaining, in build order

### Community 55 - "settings.gradle Subsystem"
Cohesion: 0.4
Nodes (4): BUG-001: Bowler selection dropdown in Over Complete modal should exclude previous bowler, BUG-002: Undo button on empty delivery stack, Bug Reports: CricHeroes Replica, Summary of Bug Severity

### Community 56 - "build.gradle Subsystem"
Cohesion: 0.4
Nodes (4): Asked for in their own words, What they ask for, What they hate, What users of the original hate and want

### Community 57 - "tailwind.config.js Subsystem"
Cohesion: 0.5
Nodes (3): responseToCache, STATIC_ASSETS, url

### Community 58 - "_Footer.md Subsystem"
Cohesion: 0.5
Nodes (3): Reporting a Vulnerability, Security Policy, Supported Versions

## Knowledge Gaps
- **307 isolated node(s):** `1. Current Status & Milestone`, `2. Implemented Features`, `3. Core Architecture & Constraints`, `4. Active Roadmap`, `Test Inventory` (+302 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `1. Current Status & Milestone`, `2. Implemented Features`, `3. Core Architecture & Constraints` to the rest of the system?**
  _307 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AST Parsing & Semantic Syntax Tree Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Match Ball Scoring & State Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Match Ball Scoring & State Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Match Ball Scoring & State Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `AST Parsing & Semantic Syntax Tree Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `AST Parsing & Semantic Syntax Tree Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._