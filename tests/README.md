# Test Suite: TallyPitch

Automated regression and end-to-end testing infrastructure powered by Playwright and Pytest.

## Test Inventory

| Module | Flow / Scope | Scenarios Covered |
| :--- | :--- | :--- |
| `test_cricket_engine.py` | Core Match & Scoring Flows | • F01: Match setup, toss, and openers<br>• F02/F03: Ball scoring, boundaries, extras, and strike rotation<br>• F04: Wicket dismissal & incoming batter<br>• F05: Over completion & bowler rotation<br>• Atomic 0ms rollback verification |
| `test_wagon_wheel_and_charts.py` | S09 Wagon Wheel & S14 Match Charts | • S09: 8-zone interactive SVG field click & trajectory vector saving<br>• S14: Over-by-over Manhattan runs bar chart<br>• S14: Cumulative Worm run chase & fall of wickets line curve<br>• S14: Match shot filter & CricHeroes 3-phase match breakdown |
| `test_realtime_bridge.py` | CricHeroes MQTT & OBS Overlay (Track 1) | • MQTT 3.1.1 binary packet encode/decode (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ)<br>• Topic wildcard filter matching (`+`, `#`)<br>• Transparent OBS lower-third live broadcast rendering (`?overlay=true`)<br>• Forensic CricHeroes ball event JSON serialization with polar coordinates<br>• Zero critical console errors verification |
| `test_community_and_badges.py` | S21 Badges & S23 Community Board (Track 3) | • S21: 8 Milestone Badges rendering, tooltips, and player switching<br>• S23: Community Matchmaking classifieds board & category filtering<br>• S23: Modal 7 classified listing creation and dynamic grid prepending<br>• Direct classified contact toast action trigger<br>• Zero critical console errors verification |
| `test_ground_and_insights.py` | Ground Intelligence & CricInsights PRO | • S14: Ground & pitch telemetry report rendering (win ratio, benchmarks, pace vs spin, dismissals)<br>• S03: Match setup venue selection & instant telemetry preview badge<br>• S07: Un-paywalled Live Match Win Predictor HUD with real-time probability updates<br>• S14: Wagon Wheel Field Vulnerability Heatmap toggle and hazard overlays<br>• S06: Multi-metric Player Scouting Engine filtering (role, strike rate, economy, search)<br>• Zero critical console errors verification |
| `test_pwa_offline.py` | PWA & Offline Service Worker | • Web App Manifest validation (name, standalone display, icons 192x192 & 512x512)<br>• Offline Service Worker (`sw.js`) cache-first asset lifecycle verification<br>• Header network status badge and accessible tooltips (Online/Ground Offline)<br>• Zero critical console errors verification |
| `test_social_card_exporter.py` | Social Match Graphic & Award Card Exporter (S16) | • S16: Publication-ready 1080x1080 Canvas graphic generation for WhatsApp & Instagram<br>• Dual mode switcher: Two-innings match summary vs. Player of the Match award certificate<br>• Squad player selector, high-res data URL preview rendering, and anchor download trigger<br>• Accessible tooltips, Escape key dismissal, and S07/S13/S21/Modal-4 CTA triggers<br>• Zero critical console errors verification |
| `test_dls_engine.py` | Duckworth-Lewis-Stern (DLS) Standard Edition (S07) | • ICC Standard Edition DLS resource matrix (0..20 overs, 0..9 wickets lost)<br>• Target revision calculations for rain-interrupted chases<br>• Live DLS Par Score HUD updates and ahead/behind status badge<br>• Modal 9 Target Calculator, live par matrix, and official DLS stoppage decision<br>• Zero critical console errors verification |
| `test_tournament_realtime.py` | Real-time Tournament Standings Stream (S18) | • CricHeroes topic architecture pub/sub (`cricheroes/tournaments/{id}/standings`)<br>• Node.js MQTT 3.1.1 binary packet encoding/decoding for tournament standings<br>• Screen S18 live MQTT telemetry badge and manual push trigger<br>• Live DOM auto-update on incoming standings stream without page refresh<br>• Automated match conclusion standings recalculation (points + NRR)<br>• Zero critical console errors verification |
| `test_android_packaging.py` | Android TWA & Native APK Packaging | • Android project structure (`android/app/build.gradle`, `AndroidManifest.xml`, `twa-manifest.json`)<br>• Google Digital Asset Links specification (`.well-known/assetlinks.json`)<br>• Standalone Python packaging validator script (`scripts/build_android_twa.py`)<br>• Modal 10 UI interaction, header CTA, AssetLinks drawer toggle, and Escape dismissal<br>• Zero critical console errors verification |
| `test_voice_commentary.py` | Real-time Audio Voice & Speech Commentary Synthesizer (Track 4) | • Zone-aware natural language commentary generator (`generateBallCommentary`)<br>• S07 HUD live voice commentary toggle button (`#btn-voice-commentary-toggle`)<br>• S13 scorecard commentary feed integration and over audio recap (`#btn-speak-over-recap`)<br>• Native `window.speechSynthesis` real-time delivery execution and over audio recap<br>• Zero critical console errors verification |
| `test_tournament_leaderboards.py` | Dynamic Tournament Leaderboards & Cap Honors Engine (Track 5 / S19) | • S19 4-cap podium honors cards rendering (Orange Cap, Purple Cap, MVP, Maximum Sixes)<br>• Top-5 Batting and Bowling leaderboards tab toggle and rankings table<br>• Dynamic live in-match cap overtaking on ball scoring (Orange Cap & Purple Cap)<br>• Match conclusion player stats consolidation into tournament baseline<br>• Zero critical console errors verification |
| `test_partnerships_engine.py` | Live Batting Partnerships Engine (Track 6 / tbl_Partnership) | • S07 Live Batting Partnership HUD card (runs, balls, RR, 4s/6s)<br>• Proportional visual contribution split bar<br>• Real-time updates on ball scoring and extras<br>• Wicket transition to next wicket partnership & unbroken active partnership tracking<br>• S13 scorecard partnerships breakdown rendering<br>• 0ms atomic delivery rollback (Undo)<br>• Zero critical console errors verification |
| `test_super_over_engine.py` | Official ICC Super Over Engine (Track 7 / tbl_MatchSuperOverBallByBall) | • Automated tied match detection on equal scores<br>• Modal 11 Super Over setup (nominating 3 batters & 1 bowler per side)<br>• S07 Super Over live console mode with dedicated telemetry banner<br>• 1-over (6 legal balls) and 2-wicket limits enforcement<br>• Reserve batter crease entry on 1st wicket & all-out trigger on 2nd wicket<br>• Innings 1 to Innings 2 chase target calculation and live RRR display<br>• Official ICC winner declaration and tournament standings consolidation<br>• S13 digital scorecard Super Over breakdown section<br>• 0ms atomic delivery rollback (Undo)<br>• Zero critical console errors verification |
| `test_compare_vs_engine.py` | Player & Team Head-to-Head Compare VS Engine (Track 8 / CricInsights PRO) | • Un-paywalled dual mode switcher (Player vs Player & Team vs Team)<br>• Marquee presets (Rohit vs Virat, Bumrah vs Siraj, Hardik vs Maxwell)<br>• 10 official comparative metrics with 10%-90% proportional split bars<br>• Dynamic head-to-head dominance index pill calculation<br>• Team vs team benchmark breakdown (matches, win %, innings averages, boundary pacing, pace share)<br>• Cross-screen triggers from S20 Player Profile (`#btn-compare-from-profile`) and Scouting Table (`⚡ VS`)<br>• Zero critical console errors verification |
| `test_shot_type_engine.py` | 8-Sector Ground Cricket Shot Type Classification Engine (Track 9 / tbl_ShotType) | • 8-sector ground mapping to canonical cricket shot types across Ground and Lofted/Air trajectories<br>• Modal 3 interactive shot chips (`#wagon-shot-type-chips`) and active shot badge (`#wagon-selected-shot-pill`)<br>• Delivery ball-by-ball shot recording (`d.shotType` & `d.wagonWheel.shot_type`)<br>• Speech commentary synthesis dynamically speaking shot names<br>• S14 Shot Analysis chart tab (`#btn-chart-shots`), filter selector, 4 KPI cards, and proportional distribution list<br>• 0ms atomic delivery rollback (Undo)<br>• Zero critical console errors verification |
| `test_face_off_engine.py` | Batter vs Bowler Head-to-Head Face-Off Matrix Engine (Track 10 / past_match_face_off) | • S07 Live Face-Off HUD button (`#btn-faceoff-hud`) & real-time striker vs bowler metrics<br>• Modal 12 (`#faceoff-modal`) interactive duel card, batter/bowler selectors, boundaries, dismissals & delivery chips<br>• S14 Face-Off Matrix chart tab (`#btn-chart-faceoff`), innings filter selector (`#faceoff-innings-select`)<br>• 4 KPI telemetry cards (Top Dominant Batter, Nemesis Bowler, Dot Ball Trap, Top Scoring Duel)<br>• Interactive grid matrix table with clickable cells and spotlight inspector (`#faceoff-spotlight-card`)<br>• 0ms atomic delivery rollback (Undo)<br>• Zero critical console errors verification |

## Running Tests

Execute tests via the Universal Pipeline:

```bash
# Token-efficient summary (recommended for agents & CI)
./pipeline.sh test --summary

# Fast smoke tests only
./pipeline.sh test --smoke

# Full verbose run
pytest -v tests/
```

## Test Harness Helpers
- `conftest.py`: Playwright browser session fixtures and local screenshot capturing.
- `helpers.py`: Bounding-box collision detection, viewport overflow checking, and zero console error assertion.

---
**Total Active Test Modules:** 17
**Total Passing E2E Tests:** 63 (100% passing)  

