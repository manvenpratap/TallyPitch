# Component Specifications: CricHeroes Clone

Rebuilt from the reconnaissance inventory in [`replica/recon.md`](file:///Volumes/Study/Projects/Replica/replica/recon.md). All components adhere strictly to semantic tokens in [`replica/design/tokens.json`](file:///Volumes/Study/Projects/Replica/replica/design/tokens.json) and follow WCAG 2.2 AA accessibility standards.

---

### PrimaryButton
```
PrimaryButton
  variants  primary (solid), secondary (surface outline), ghost, danger
  sizes     sm 32px (h-8 px-3 text-xs), md 40px (h-10 px-4 text-sm), lg 48px (h-12 px-6 text-base)
  states    default, hover, active, focus-visible (2px ring, 2px offset, ring-accent), disabled, loading
  tokens    bg accent, text on-accent, radius md, font sm/600, transition-fast
  a11y      Semantic <button>, aria-disabled, loading spinner uses aria-live="polite" and preserves accessible label
  used on   S01, S03, S04, S05, S06, S11, S15
```

---

### RunsKeypad
```
RunsKeypad
  variants  compact (scorer bottom bar), full-grid (2x3 keypad for quick finger taps on mobile)
  sizes     6 buttons (0, 1, 2, 3, 4, 6), each min-tap target 56px x 56px
  states    default, pressed (scale 0.96), active, disabled (during network sync or innings break)
  tokens    bg surface, border border, text text (font-display/800), radius lg, shadow-card
  a11y      Role "group" with aria-label="Runs scored", keyboard shortcuts 0, 1, 2, 3, 4, 6 supported
  used on   S07 (Live Scoring Console)
```

---

### ExtrasBar
```
ExtrasBar
  variants  button row: Wide (Wd), No-Ball (Nb), Bye (B), Leg-Bye (Lb), Penalty (Pen)
  sizes     height 38px, flex-1 width per pill
  states    default, active (highlighted with amber border), disabled
  tokens    bg surface, border border, text text-muted, active text warning, radius pill
  a11y      Toggles extra input sub-modal; aria-haspopup="dialog", aria-expanded
  used on   S07 (Live Scoring Console)
```

---

### DeliveryCircleChip
```
DeliveryCircleChip
  variants  dot (0), singles (1, 2, 3), four (boundary), six (maximum), wicket (W), extra (Wd, Nb, B, Lb)
  sizes     sm 24px (compact scorecard), md 32px (active over timeline)
  states    default, active/current ball (pulse ring), historical
  tokens    dot: bg ball-dot, text text-muted
            boundary: bg accent, text on-accent
            wicket: bg danger, text on-accent
            extra: bg warning, text on-accent
            radius pill (circular)
  a11y      aria-label="Ball 3: 4 runs scored" or "Ball 5: Wicket fallen"
  used on   S07, S10, S13
```

---

### ActiveBatterBowlerCard
```
ActiveBatterBowlerCard
  variants  striker (highlighted with cricket bat icon & green badge), non-striker, active bowler
  sizes     full-width card, vertical stack on mobile, horizontal row on tablet
  states    default, on-strike (active green indicator border), bowling, sub-menu triggerable
  tokens    bg surface, border border, text text, text-muted text-muted, radius md, shadow-card
  a11y      aria-live="polite" updates as runs and strike change; clear label for striker vs non-striker
  used on   S07 (Live Scoring Console)
```

---

### DismissalModal
```
DismissalModal
  variants  full-screen modal sheet on mobile, centered dialog on desktop (max-w-md)
  sizes     responsive dialog with dismissal type grid (Bowled, Caught, Run Out, Stumped, LBW, Hit Wicket)
  states    initial selection, selecting fielder, selecting out batsman (for run-outs), selecting next batsman, submitting
  tokens    bg surface, text text, border border, radius lg, shadow-pop
  a11y      Role "dialog", aria-modal="true", traps keyboard focus, Escape key closes modal
  used on   S08 (Wicket Dialog)
```

---

### RadialGroundCanvas (Wagon Wheel)
```
RadialGroundCanvas
  variants  inline modal trigger, post-boundary prompt
  sizes     circular SVG field map 280px x 280px with 8 primary cricket field zones
  states    default (unselected), zone hovered, zone selected, skipped/bypassed
  tokens    fill #0a6e38 (turf green), lines #ffffff opacity 0.2, selected zone #ffd700
  a11y      Accessible via numbered keyboard list (1: Fine Leg, 2: Square Leg, etc.) for non-pointer users
  used on   S09 (Wagon Wheel Direction)
```

---

### ScoreTickerStrip (OBS Live Overlay)
```
ScoreTickerStrip
  variants  standard lower-third banner (1920x1080 canvas, 80px bottom strip), compact corner badge
  sizes     fluid width, 72px fixed height, transparent background
  states    normal score display, boundary flash animation (4/6), wicket alert flash (W)
  tokens    bg rgba(17, 22, 29, 0.92) dark glass, text #ffffff, accent #0a6e38, danger #c92a2a, font-mono
  a11y      Public broadcast display, aria-hidden when loaded inside OBS/vMix browser source
  used on   S22 (Live Stream OBS Ticker)
```

---

### ScorecardTable
```
ScorecardTable
  variants  batting table (Batter, Dismissal, R, B, 4s, 6s, SR), bowling table (Bowler, O, M, R, W, Eco), FOW timeline
  sizes     full-width responsive table with horizontal scroll on small screens
  states    live in-progress (asterisk on active batters), completed, empty
  tokens    header: bg surface, text text-muted font-xs/600; row: border border, text text font-sm/400
  a11y      Semantic <table> with <thead>, <tbody>, <th scope="col">, and numerical alignment (text-right)
  used on   S13 (Full Match Scorecard)
```

---

### PointsTableGrid
```
PointsTableGrid
  variants  tournament group standings (Rank, Team, P, W, L, T, NR, Pts, NRR)
  sizes     full-width responsive table with sticky left team name on mobile
  states    sorted by Points desc, then NRR desc; playoff qualification cut-off line (top 2 highlighted)
  tokens    bg surface, text text, border border, playoff row border-l-4 border-l-accent
  a11y      aria-sort on headers (Points, NRR); semantic table markup
  used on   S18 (Dynamic Points Table)
```

---

### ManhattanChart
```
ManhattanChart
  variants  single innings bar chart, dual innings comparative bar chart
  sizes     responsive container (min-h-[220px])
  states    empty, loading skeleton, rendered bars with hover tooltips (Runs, Overs, Wickets)
  tokens    innings 1 bar: fill accent, innings 2 bar: fill #2563eb, wicket marker: dot danger
  a11y      Includes hidden tabular data table (<table class="sr-only">) for screen reader users
  used on   S14 (Match Analytics)
```

---

### WormChart
```
WormChart
  variants  cumulative runs line graph comparing Team A vs Team B over-by-over
  sizes     responsive container (min-h-[220px])
  states    1st innings curve, 2nd innings live chase curve, wicket markers on curve
  tokens    team 1 line: stroke accent (stroke-width 2.5), team 2 line: stroke #2563eb, background surface
  a11y      Accompanied by text summary of run rate differential and screen-reader data table
  used on   S14 (Match Analytics)
```

---

### StatMetricPill
```
StatMetricPill
  variants  runs, wickets, strike rate, economy, overs, average
  sizes     sm (px-2 py-0.5 text-2xs), md (px-2.5 py-1 text-xs)
  states    default, highlighted (record or milestone)
  tokens    bg surface, border border, text text font-mono, radius pill
  a11y      Clear prefix aria-label (e.g. "Strike Rate: 142.5")
  used on   S07, S13, S19, S20
```

---

### UndoActionButton
```
UndoActionButton
  variants  icon button with label ("Undo Last Ball")
  sizes     h-9 px-3 text-xs, min-tap target 44px
  states    default, disabled (when delivery stack is empty), loading (during rollback processing)
  tokens    bg surface, border border, text text-muted, hover text danger, radius md
  a11y      aria-label="Undo last recorded delivery", keyboard shortcut Ctrl+Z supported
  used on   S07 (Live Scoring Console)
```

---

### QuickActionFAB
```
QuickActionFAB
  variants  floating circular action button (+), expands to menu ("Start Match", "Host Tournament")
  sizes     56px x 56px circular floating button with elevated shadow
  states    default, expanded (menu open), hidden (when scrolling score console)
  tokens    bg accent, text on-accent, shadow-elevated, radius pill
  a11y      aria-expanded, aria-haspopup="menu", keyboard operable
  used on   S02 (Home Dashboard)
```
