# Offline Resilience & Realtime Architecture

Grassroots cricket matches are frequently played on rural grounds, municipal parks, or farm pitches where cellular connectivity is intermittent or non-existent. Traditional cloud-first scoring apps freeze, lose deliveries, or drop connections. TallyPitch was built with an offline-first foundation.

---

## 1. Offline-First Lifecycle & Data Flow

```mermaid
flowchart LR
    A["Ball Keyed In\n(Scorer Input)"] --> B["Local Memory & Cache\n(Immutable Stack)"]
    B --> C["Instant UI Update\n(0ms Latency)"]
    B -.->|"When connection is live"| D["WebSocket / REST\n(Remote Database Sync)"]
```

1. **Local-First Write**: Every ball scored is immediately committed to in-memory state and local browser storage.
2. **0ms UI Feedback**: UI updates instantaneously; scorers never wait on network responses.
3. **Queue & Sync**: If a network connection is available, deliveries are transmitted asynchronously to the backend REST API (`POST /api/matches/:id/deliveries`).
4. **Offline Resilience**: If cellular signal drops completely, scoring continues uninterrupted for the full 20 overs. When back in range, the offline log can be synced to PostgreSQL.

---

## 2. Technology Stack & Component Responsibilities

| Layer | Technology | Primary Role |
| :--- | :--- | :--- |
| **Frontend** | Vanilla JS / Modular HTML / Tailored Tokens | Single-file zero-dependency scoring console and tournament dashboard (`index.html`). |
| **Styling** | Royal Pitch Sapphire Tokens (`tooltip.css`, tokens) | Daylight-readable high-contrast theme with dark-mode parity. |
| **Realtime Engine** | Node.js + `ws` (`server/realtime.js`) | Low-latency delivery broadcasting for spectators and live OBS overlays. |
| **REST API** | Node.js HTTP (`server/api.js`) | Match setup, squads, toss, deliveries, undo, and tournament points endpoints. |
| **Database** | PostgreSQL / Supabase (`supabase/migrations/`) | ACID relational data with Row-Level Security (RLS) policies. |
| **Billing** | Stripe (`server/stripe.js`) | Pro subscription handling and webhook processing. |

---

## 3. Formal System Visualizations

### 📐 1. System Architecture

```mermaid
flowchart TD
    Scorer["📱 Grassroots Scorer / Official\n(Mobile Browser / TWA APK)"]
    
    subgraph BrowserApp["🌐 Offline-First PWA Sandbox (Local Browser)"]
        UI["⚡ TallyPitch SPA\n(Keypad, HUD, Wagons, DLS)"]
        MemCache[("💾 Local Memory & Storage\n(State & Undo Snapshots)")]
        SW["⚙️ Service Worker Cache\n(Zero Cloud Dependencies)"]
    end

    subgraph Backend["☁️ TallyPitch Cloud / Ground Server"]
        API["⚡ Node.js REST API\n(:4000 /api/matches)"]
        Realtime["📡 MQTT 3.1.1 & WS Broker\n(:1884/:8884 Broadcast)"]
        DB[("🐘 PostgreSQL / Supabase\n(RLS Match Ledger)")]
    end

    Spectators["📺 Fans / OBS Overlays\n(Transparent Lower-Third)"]

    Scorer -->|"0ms touch"| UI
    UI -->|"atomic commit"| MemCache
    UI -.->|"async sync"| API
    UI -.->|"publish live ball"| Realtime
    API -->|"persist"| DB
    Realtime -->|"live push"| Spectators
```

### 🔄 2. Scoring Engine & 0ms Atomic Rollback Workflow

```mermaid
flowchart LR
    A["1. Ball Scored\n(Runs / Extra / Wkt)"] --> B["2. Deep Clone Snapshot\n(Push to Undo Stack)"]
    B --> C["3. Mutate Match State\n(Runs, overs, striker)"]
    C --> D["4. 0ms DOM Update\n(HUD, Wagon, Worm)"]
    D --> E["5. Audio Voice & WS\n(Speech synthesis & MQTT)"]
    E --> F["6. Rollback Available\n(Undo button pops stack)"]
```

### ⚡ 3. Realtime Ingestion & OBS Broadcast Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Scorer as Official Scorer
    participant UI as TallyPitch PWA
    participant State as Memory Cache
    participant Bridge as MQTT / WS Bridge
    participant OBS as OBS Lower-Third Screen

    Scorer->>UI: Key In Delivery (e.g. 4 Runs)
    UI->>State: Atomic State Commit + Snapshot
    State-->>UI: 0ms State Confirmed
    UI->>Bridge: MQTT PUBLISH 'cricheroes/matches/{id}/ball'
    Bridge->>OBS: Push Scoreboard Payload
    OBS-->>OBS: Animate Lower-Third Graphics
    Scorer->>UI: (Optional) Click Undo
    UI->>State: Pop Last Snapshot
    State-->>UI: State Rolled Back Instantly
    UI->>Bridge: MQTT PUBLISH 'cricheroes/matches/{id}/score'
```

### 🌊 4. Match Data Flow Pipeline

```mermaid
flowchart LR
    Input["Scorer Touch Event\n(Keypad, extras, wagon angle)"] --> StateEngine["Local State Engine\n(Innings, partnerships, DLS par)"]
    StateEngine --> Snapshots[("Snapshot History\n(Undo/Redo memory stack)")]
    StateEngine --> Audio["Voice Synthesizer\n(Web Speech API)"]
    StateEngine --> ExportCanvas["Social Card Exporter\n(1080x1080 Canvas)"]
    StateEngine --> MQTTBridge["MQTT 3.1.1 Stream\n(Binary topic fanout)"]
    MQTTBridge --> OBS["OBS Overlays & Standings"]
```

### ⏱️ 5. Match & Tournament Lifecycle

```mermaid
stateDiagram-v2
    [*] --> FixtureSetup: Teams, Ground & Overs Configured
    FixtureSetup --> TossConducted: 3D Coin Toss & Lineups
    TossConducted --> Innings1Live: Opener & Strike Selected
    Innings1Live --> InningsBreak: 20 Overs / 10 Wickets Down
    InningsBreak --> Innings2Chase: Target & Required RR Set
    Innings2Chase --> DLSInterruption: Rain / Bad Light
    DLSInterruption --> Innings2Chase: Revised DLS Par Target
    Innings2Chase --> Concluded: Target Reached / Overs Expired
    Innings2Chase --> Tied: Exact Scores Equal
    Tied --> SuperOver: 1-Over ICC Tie-Breaker
    SuperOver --> Concluded: Super Over Winner Decided
    Concluded --> TournamentStandings: Points Table & NRR Updated
    TournamentStandings --> [*]
```
