# Test Plan: CricHeroes Replica

Build: `3853cad`  Date: 2026-10-14  Env: Local Chromium (Headless Playwright & Browser Subagent)

| Case ID | Flow | Type | Steps | Expected Outcome | Auto | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F01-H1** | Match Setup (S03) | Happy | Fill team names, pick 10 overs, submit form | Navigates to S05 (Toss) with correct team names | e2e | **PASS** |
| **F01-H2** | The Toss (S05) | Happy | Flip coin, select Mumbai Strikers, choice Bat | Displays toss decision announcement, proceeds to openers | e2e | **PASS** |
| **F01-H3** | Openers (S06) | Happy | Select Striker & Non-Striker from squad, click Start | Enters S07 with score 0/0, active batters, and over 0.0 | e2e | **PASS** |
| **F01-E1** | Openers (S06) | Edge | Select identical player as both Striker & Non-Striker | Alert prevents submission ("Must be distinct players") | e2e | **PASS** |
| **F02-H1** | Ball Scoring (S07) | Happy | Tap 1 run (Single) | Score updates to 1/0, striker and non-striker ends swap | e2e | **PASS** |
| **F02-H2** | Boundaries (S07) | Happy | Tap 4 runs (Four) | Score updates to 5/0, boundary registered, strike unchanged | e2e | **PASS** |
| **F02-E1** | Consecutive Fours | Edge | Tap 4, then tap 6 | Strike remains on same batter, 10 runs credited | e2e | **PASS** |
| **F03-H1** | Extras (Wide) | Happy | Tap +1 Wide | Score increments +1, legal ball counter stays 0.0 | e2e | **PASS** |
| **F03-H2** | Extras (No Ball) | Happy | Tap +1 No Ball | Score increments +1, free hit state flagged for next ball | e2e | **PASS** |
| **F03-E1** | Extras (Bye) | Edge | Tap +1 Bye | Legal ball counter advances +1, strike rotates on single | e2e | **PASS** |
| **F04-H1** | Dismissal (Caught) | Happy | Tap Wicket, select Caught, enter fielder, submit | Score updates to 0/1, batter marked out with bowler credit | e2e | **PASS** |
| **F04-E1** | Dismissal (Run Out) | Edge | Select Run Out | Bowler is not credited with wicket in figures | e2e | **PASS** |
| **F05-H1** | Over Completion | Happy | Bowl 6 legal deliveries | S10 modal appears, strike flips, prompts next bowler | e2e | **PASS** |
| **F05-E1** | Consecutive Bowler | Edge | Select the bowler who bowled the previous over | Validation prevents consecutive overs by same bowler | e2e | **PASS** |
| **F06-H1** | Undo Rollback Stack | Happy | Score 6, tap Undo | 6 runs and ball count reversed, original batter stats restored | e2e | **PASS** |
| **F06-E1** | Undo Empty Stack | Edge | Tap Undo on 0.0 with empty stack | Graceful toast alert ("No deliveries to undo!"), no crash | e2e | **PASS** |
| **F07-H1** | Innings Break | Happy | Complete innings quota / 10 wickets | S11 modal displays target score (`Innings 1 + 1`), sets RRR | e2e | **PASS** |
| **F08-H1** | Scorecard (S13) | Happy | Open Scorecard tab | Tables populate with runs, balls, strike rates, and FOW | e2e | **PASS** |
| **F08-H2** | Commentary (S13) | Happy | Inspect Ball-by-Ball commentary list | Automated commentary text rendered per ball in reverse order | e2e | **PASS** |
