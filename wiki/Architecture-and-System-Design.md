# Offline Resilience & Realtime Architecture

> **Executive Overview**: Production-grade grassroots cricket scoring platform, digital scorebook, and live OBS broadcast engine. Engineered with an offline-first architecture to guarantee 0ms latency scoring, zero dropped balls, instant atomic rollback, automated ICC Net Run Rate (NRR) computation, and real-time MQTT/WebSocket streaming.

All system architectures, scoring workflows, OBS sequence broadcasts, data pipelines, and match lifecycles are embedded below as native Mermaid diagrams with full architectural explanations.

---

## 🏛️ 1. System Architecture

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

### Architectural Breakdown & Component Responsibilities
* **Offline-First PWA Sandbox**: Grassroots matches are played in open municipal grounds and rural fields where 4G/5G signal frequently drops. TallyPitch runs locally in the scorer's browser cache via Service Worker, executing all cricket scoring rules with zero reliance on cloud connectivity.
* **Scoring Console & DOM HUD (`index.html`)**: Single-file high-contrast UI with daylight mode readability. Features full numeric keypad, extras selectors (Wide, No Ball, Bye, Leg Bye, Penalty), Wagon Wheel shot direction coordinates, and pitch trajectory maps.
* **In-Memory Snapshot Ring Buffer**: Every single scored delivery triggers an immutable deep clone of the match state pushed to an in-memory stack, enabling instantaneous, 0-millisecond single-click Undo without network roundtrips.
* **Node.js REST API & PostgreSQL**: Provides centralized match registration, tournament fixtures, official team rosters, and historical tournament points tables.
* **MQTT 3.1.1 & WebSocket Streaming Broker**: Low-latency message broker streaming live ball-by-ball updates to spectators and streaming OBS broadcast overlays in real time.
* **OBS Broadcast Overlay**: Standalone transparent webview (`/?overlay=true`) designed for live streaming overlays with dynamic animated lower-thirds, partnership worms, and striker stats.

---

## 🔄 2. Scoring Engine & 0ms Atomic Rollback Workflow

```mermaid
flowchart LR
    A["1. Ball Scored\n(Runs / Extra / Wkt)"] --> B["2. Deep Clone Snapshot\n(Push to Undo Stack)"]
    B --> C["3. Mutate Match State\n(Runs, overs, striker)"]
    C --> D["4. 0ms DOM Update\n(HUD, Wagon, Worm)"]
    D --> E["5. Audio Voice & WS\n(Speech synthesis & MQTT)"]
    E --> F["6. Rollback Available\n(Undo button pops stack)"]
```

### Operational Workflow Stages
1. **Delivery Input**: Scorer taps a runs button, extras chip, or wicket modal button.
2. **Immutable Snapshot Push**: Before modifying state, a structured snapshot of `state.currentLive` is pushed onto the `undoStack`.
3. **State Mutation**: Deliveries count, total runs increment, striker/non-striker positions swap on odd runs, bowler statistics update, and over boundaries (6 legal balls) trigger automatic bowler change alerts.
4. **Instant HUD Refresh**: Total score, current run rate (CRR), required run rate (RRR), partnership runs, and wagon wheels re-render instantly at 0ms latency.
5. **Voice Commentary & Stream Publish**: Uses Web Speech API to speak the delivery score (e.g. *"Four runs to Rohit Sharma"*) and broadcasts the MQTT payload.
6. **Instant Rollback**: If an umpire signal is corrected or a scorer misclicks, tapping "Undo" pops the previous snapshot from the stack and restores match state with zero database roundtrips.

---

## ⚡ 3. Realtime Ingestion & OBS Broadcast Sequence

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

### Execution Sequence Details
* **Steps 1–3**: The scorer logs a boundary. The local state commits the delivery, updates batsman and bowler figures, and pushes the undo snapshot.
* **Step 4**: The PWA publishes a lightweight binary/JSON payload to the MQTT topic `cricheroes/matches/{id}/ball`.
* **Step 5–6**: The OBS stream browser source receives the payload over WebSocket, triggering CSS keyframe animations to display the boundary banner and updated total.
* **Steps 7–10**: When Undo is triggered, the rollback payload is published immediately to synchronize the OBS screen with the corrected score.

---

## 🌊 4. Match Data Flow Pipeline

```mermaid
flowchart LR
    Input["Scorer Touch Event\n(Keypad, extras, wagon angle)"] --> StateEngine["Local State Engine\n(Innings, partnerships, DLS par)"]
    StateEngine --> Snapshots[("Snapshot History\n(Undo/Redo memory stack)")]
    StateEngine --> Audio["Voice Synthesizer\n(Web Speech API)"]
    StateEngine --> ExportCanvas["Social Card Exporter\n(1080x1080 Canvas)"]
    StateEngine --> MQTTBridge["MQTT 3.1.1 Stream\n(Binary topic fanout)"]
    MQTTBridge --> OBS["OBS Overlays & Standings"]
```

### Data Pipeline Mechanics & Invariants
* **Deterministic Cricket Engine**: MCC Law compliance for extras (no ball re-bowls, free hits, byes, leg-byes, penalty runs under Laws 28.3, 41, and 42).
* **Automated DLS Par Calculator**: Mathematical Duckworth-Lewis-Stern resource table calculation for rain-curtailed run chases.
* **Social Matchday Exporter**: Direct client-side rendering to an HTML5 `<canvas>` producing high-resolution 1080x1080 social media match cards with player scores, wagon wheels, and team logos.

---

## ⏱️ 5. Match & Tournament Lifecycle

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

### Lifecycle State Machine Transitions
* **`FixtureSetup`**: Teams, venue dimensions, ball type (leather/tennis), and scheduled overs (T20, 10 overs) configured.
* **`TossConducted`**: Interactive 3D coin toss animation records toss winner and decision (bat/bowl).
* **`Innings1Live`**: Scorer tracks first innings balls, maidens, partnerships, and wagon placements until 10 wickets fall or overs expire.
* **`InningsBreak`**: Target score and required run rate (RRR) locked in.
* **`Innings2Chase`**: Live run chase tracking balls remaining vs. runs required. Supports mid-innings DLS rain adjustments.
* **`SuperOver`**: Official ICC 1-over tie-breaker mode activated if scores are level at the end of both innings.
* **`TournamentStandings`**: On match conclusion, Net Run Rate (NRR) is recomputed across the entire tournament points table using ICC rules: `NRR = (Total Runs Scored / Total Overs Faced) - (Total Runs Conceded / Total Overs Bowled)`.
