# TallyPitch 🏏

> **The Transparent Grassroots Cricket Platform**  
> Fast, ad-free ball-by-ball scoring with 0ms rollback, automated ICC Net Run Rate standings, digital scorecards, and free OBS broadcast overlays.

---

## Overview

**TallyPitch** is an independent, production-grade cricket scoring and tournament management platform designed specifically for grassroots clubs, weekend leagues, and local tournament organizers. Built to overcome the invasive video popups, locked basic stats, and expensive paywalls of legacy scoring apps, TallyPitch provides an uncompromised matchday experience.

> 📚 **Complete Documentation**: Explore the [**TallyPitch GitHub Wiki**](https://github.com/manvenpratap/TallyPitch/wiki) for matchday scoring guides, OBS streaming setups, tournament NRR mathematics, and database specifications.

---

## 🏛️ System Architecture & Compiled Diagrams

TallyPitch architecture, offline rollback workflows, realtime streaming sequences, and match lifecycles are formally compiled via [Archify](https://github.com/tt-a1i/archify):

* 📐 **System Architecture**: [Interactive HTML View](./docs/diagrams/architecture.html) | [Spec](./docs/diagrams/architecture.json)
* 🔄 **Scoring Workflow**: [Interactive HTML View](./docs/diagrams/workflow.html) | [Spec](./docs/diagrams/workflow.json)
* ⚡ **Realtime OBS Sequence**: [Interactive HTML View](./docs/diagrams/sequence.html) | [Spec](./docs/diagrams/sequence.json)
* 🌊 **Data Flow Pipeline**: [Interactive HTML View](./docs/diagrams/dataflow.html) | [Spec](./docs/diagrams/dataflow.json)
* ⏱️ **Match Lifecycle**: [Interactive HTML View](./docs/diagrams/lifecycle.html) | [Spec](./docs/diagrams/lifecycle.json)

Native embedded vector diagrams are available directly on the [**GitHub Wiki: Offline Resilience & Architecture**](https://github.com/manvenpratap/TallyPitch/wiki/Offline-Resilience-and-Architecture).

### Key Features

- **Zero-Ad Scoring Console**: 100% ad-free scoring interface so scorers never miss a ball to an unskippable video popup.
- **0ms Instant Rollback**: Atomic undo stack allows immediate correction of miskeyed runs, extras, or wickets with complete state restoration.
- **Offline-First Resilience**: Local in-memory persistence and state caching ensures matches on rural grounds continue uninterrupted if cellular signal drops.
- **Official ICC Digital Scorecards**: Clean batting, bowling, fall-of-wickets tables, and ball-by-ball commentary.
- **Tournament Manager & Automated NRR**: Pool A/B round-robin tables, knockout brackets, and dynamically computed Net Run Rate with 3-decimal precision.
- **Free Broadcast Overlays**: Dedicated, clean lower-third URL ready to embed directly into OBS Studio or vMix for live streaming without extra fees.
- **Team & Player Career Profiles**: Comprehensive player statistics, strike rates, bowling economies, and head-to-head records.

---

## Project Structure

```text
TallyPitch/
├── index.html            # Main single-page web app (Scoring console, Tournaments, Teams, Profiles)
├── landing.html          # Marketing landing page with product tour and pricing
├── server/               # Node.js backend services
│   ├── api.js            # Express REST API routes for matches, tournaments, and teams
│   ├── auth.js           # Supabase Auth verification & session handlers
│   ├── db.js             # PostgreSQL / Supabase connection pool
│   ├── realtime.js       # WebSocket live broadcast server for spectators & OBS overlays
│   └── stripe.js         # Stripe Checkout & billing webhook handlers
├── supabase/             # Database migrations & schemas
│   └── migrations/
│       └── 20261014000000_init_tallypitch.sql  # 16 PostgreSQL tables with Row-Level Security
├── scripts/
│   └── seed.sql          # Seed fixtures, test clubs, players, and sample matches
├── replica/              # Architectural specs & design audit documentation
│   ├── architecture.md   # System architecture, API contracts, and invariants
│   ├── backend.md        # Database schema, auth flows, and Stripe integration specs
│   ├── brand.json        # Brand metadata, color roles, and font definitions
│   ├── brand.md          # Voice guide, trademark checks, and contrast testing
│   ├── features.csv      # Feature matrix with parity audit records
│   ├── parity.md         # Parity comparison and validation report
│   ├── design/           # Design tokens (tokens.css, tokens.json, tailwind.config.js)
│   └── launch/           # Landing page specs, store listing metadata, and pricing
├── wiki/                 # Comprehensive documentation pages mirroring GitHub Wiki
├── dist/                 # Production distribution build (synced with index.html)
├── pipeline.sh           # Standalone self-analyzing & self-healing pipeline runner
├── tests/
│   ├── conftest.py       # Playwright browser fixtures
│   ├── helpers.py        # Collision detection & assertion helpers
│   ├── README.md         # Test suite inventory
│   └── test_cricket_engine.py  # Playwright E2E test suite covering core scoring flows
├── package.json          # Node backend dependencies & npm scripts
├── .env.example          # Environment variable template
└── LICENSE               # MIT License
```

---

## Quick Start

### 1. Run the Web Application Locally

The frontend is a lightweight, zero-dependency application that can be run directly:

```bash
# Using Python's built-in static HTTP server:
python3 -m http.server 8080

# Or using npx:
npx serve .
```

Then visit:
- **Scoring App**: `http://localhost:8080/index.html`
- **Landing Page**: `http://localhost:8080/landing.html`

### 2. Backend Services

To enable remote database synchronization, authentication, and WebSocket live broadcasting:

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Configure your Supabase and Stripe credentials in .env
# 3. Start the API & Realtime server:
node server/api.js
```

### 3. Database Setup

Apply the schema and seed sample tournament data:

```bash
# Apply migrations to your Postgres / Supabase instance:
psql "$DATABASE_URL" -f supabase/migrations/20261014000000_init_tallypitch.sql

# Optional: Seed sample tournament and teams:
psql "$DATABASE_URL" -f scripts/seed.sql
```

### 4. Running Tests

End-to-end automated tests for match initialization, live scoring, wicket dismissals, and over completion:

```bash
# Run the Playwright test suite:
python3 -m unittest tests/test_cricket_engine.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
