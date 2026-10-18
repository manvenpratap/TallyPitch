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
**Total Active Test Modules:** 8
**Total Passing E2E Tests:** 35 (100% passing)
