# Welcome to the TallyPitch Wiki 🏏

**TallyPitch** is an independent, ad-free, high-integrity cricket scoring and tournament management platform built specifically for grassroots clubs, weekend leagues, and local tournament organizers.

---

## 📖 Wiki Navigation

### 🎯 Core Features & User Guides
- [[Scoring-Engine-and-Rollback|Scoring Engine & 0ms Rollback]] — Complete guide to matchday scoring, extras, dismissals, and instant error recovery.
- [[Tournament-Management-and-NRR|Tournament Management & Net Run Rate]] — Managing round-robin pools, knockout brackets, and automated ICC NRR calculations.
- [[OBS-and-Live-Streaming|OBS & Live Broadcast Streaming]] — Setting up free lower-third scoreboard overlays in OBS Studio and vMix.

### 🏗️ Technical Architecture & Operations
- [[Offline-Resilience-and-Architecture|Offline Resilience & Realtime Architecture]] — Local state caching for rural grounds, WebSocket broadcasts, and Supabase integration.
- [[API-and-Database-Reference|API & Database Reference]] — REST endpoints, PostgreSQL DDL schema with RLS, and data invariants.
- [[Contributing-and-Development|Developer Guide & Universal Pipeline]] — Running the local dev environment, executing Playwright tests, and distribution verification.

---

## ⚡ Why TallyPitch?

Legacy cricket scoring applications subject grassroots clubs to aggressive monetization:
1. **Unskippable Ads in the Box**: Scorers frequently miss the first ball of an over due to 30-second full-screen video ads.
2. **Paywalled Integrity**: Basic league standings, Net Run Rate calculations, and head-to-head comparisons are locked behind subscriptions.
3. **Per-Match Streaming Surcharges**: Broadcasting volunteer club games with graphics overlays carries steep per-game fees.

**The TallyPitch Guarantee:**
- **100% Ad-Free Live Scoring**: Zero video popups or distracting banners during active play.
- **0ms Atomic Undo**: Instant rollback of miskeyed deliveries with complete state restoration.
- **Unpaywalled League Math**: Full ICC Net Run Rate calculations and tournament brackets included for all leagues.
- **Free Broadcast Overlays**: Dedicated browser source URL for OBS/vMix live streaming without surcharges.

---

## 🚀 Quick Links
- **Repository**: [github.com/manvenpratap/TallyPitch](https://github.com/manvenpratap/TallyPitch)
- **Live Scoring App**: [`index.html`](https://github.com/manvenpratap/TallyPitch/blob/main/index.html)
- **Marketing Page**: [`landing.html`](https://github.com/manvenpratap/TallyPitch/blob/main/landing.html)
- **License**: [MIT License](https://github.com/manvenpratap/TallyPitch/blob/main/LICENSE)
