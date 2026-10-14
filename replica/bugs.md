# Bug Reports: CricHeroes Replica

QA Pass Date: 2026-10-14  
Build: `3853cad`  
Status: **0 Open S1/S2 Blocker Bugs**

---

### BUG-001: Bowler selection dropdown in Over Complete modal should exclude previous bowler

- Severity: S3
- Flow / case: F05-E1
- Screen: S10 (Over Complete Handover)
- Build: `3853cad`  Browser / device: Headless Chromium
- Steps:
  1. Complete 6 legal balls of over 1 bowled by Jasprit Bumrah.
  2. Over complete modal opens.
- Expected: Bowler who bowled over 1 (Jasprit Bumrah) must be excluded from the dropdown options.
- Actual: Bumrah was filtered correctly, but if the bowling squad has fewer than 2 bowlers registered, dropdown became empty.
- Status: **Fixed** in `index.html` (filters out previous bowler while ensuring available bowlers are listed).

---

### BUG-002: Undo button on empty delivery stack

- Severity: S4
- Flow / case: F06-E1
- Screen: S07 (Live Scoring Console)
- Build: `3853cad`  Browser / device: Headless Chromium
- Steps:
  1. Open console at 0.0 before any ball is bowled.
  2. Click Undo button.
- Expected: Friendly toast notification indicating no deliveries exist, without altering state.
- Actual: Handled cleanly with `showToast("No deliveries to undo!")`.
- Status: **Verified / Working as expected**.

---

### Summary of Bug Severity

| Severity | Description | Count | Open | Resolved |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | Data loss, security hole, core flow blocked | 0 | 0 | 0 |
| **S2** | Feature broken, no workaround | 0 | 0 | 0 |
| **S3** | Broken with a workaround, visible defect | 1 | 0 | 1 |
| **S4** | Cosmetic or minor polish | 1 | 0 | 1 |
| **Total** | | **2** | **0** | **2** |
