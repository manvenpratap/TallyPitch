# Scoring Engine & 0ms Rollback

The heart of TallyPitch is a high-speed, zero-latency cricket scoring console built to endure high-pressure matchday conditions under bright sunlight.

---

## 1. Keypad Design & Ball Entry

The scoring console presents an ergonomic 6-button keypad (0, 1, 2, 3, 4, 6) alongside quick modifiers for extras and dismissals:
- **Dot Ball (0)**: Increments balls faced by striker, bowler deliveries, and updates over progression.
- **Singles & Threes (1, 3)**: Automatically rotates strike between striker and non-striker.
- **Boundaries (4, 6)**: Records boundary runs, updates batter boundary counters, strike rate, and team score without strike rotation.
- **Two & Fours**: Maintains striker on strike.

### Extras Handling
TallyPitch supports the standard ICC extras classifications:
- **Wide Ball (WD)**: Adds 1 extra run (or more if byes taken). Does not count toward legal over deliveries.
- **No Ball (NB)**: Adds 1 extra run and signals a Free Hit on the subsequent delivery.
- **Leg Bye (LB) & Bye (B)**: Legal deliveries where runs are attributed to team total and extras, not the batter's personal tally. Strike rotates on odd counts.

---

## 2. 0ms Atomic Rollback Architecture

Under matchday pressure on the boundary line, scorers occasionally press the wrong button or mishear the umpire's call. In traditional cloud-reliant apps, undoing an action requires a roundtrip network request, leaving scorers in limbo while the bowler starts their next run-up.

### How TallyPitch Solves This
TallyPitch maintains an **in-memory immutable delivery stack**:
1. Every delivery recorded creates a snapshot of:
   - Innings score and wicket count
   - Current over and legal ball index
   - Striker and non-striker player IDs
   - Active bowler figures (overs, maidens, runs, wickets)
   - Fall of wickets timeline
2. When the **Undo** button is pressed, TallyPitch pops the latest delivery from the stack and immediately restores the prior state in **0ms**.
3. The UI updates synchronously with zero network roundtrip wait, allowing the scorer to re-enter the correct delivery before the next ball is bowled.

---

## 3. End of Over & Bowler Rotation

When the 6th legal delivery of an over is bowled:
- **Strike Flips**: The non-striker becomes the new striker for the incoming over.
- **Bowler Selection Modal**: Prompt scorer to select the bowler for the next over.
- **Consecutive Bowler Lock**: The validation engine enforces the fundamental cricket rule preventing the same bowler from bowling two consecutive overs from opposite ends.

---

## 4. Wicket Dismissals & Fall-of-Wickets

Supported dismissal types:
- Bowled
- Caught (with fielder attribution)
- LBW (Leg Before Wicket)
- Run Out (with end selection: striker or non-striker end)
- Stumped
- Hit Wicket

Each dismissal records:
- Exact delivery sequence and current team score
- Out batter and dismissed bowler
- Replacement batter prompt
