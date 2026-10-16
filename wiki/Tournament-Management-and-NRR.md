# Tournament Management & Net Run Rate (NRR)

TallyPitch includes complete tournament management capabilities to support local weekend leagues, corporate cups, school championships, and box cricket tournaments.

---

## 1. Multi-Stage Tournament Structure

TallyPitch supports flexible tournament configurations:
- **Round-Robin Groups**: Divide participating clubs into Pool A, Pool B, etc.
- **Knockout Brackets**: Quarter-finals, Semi-finals, 3rd Place Playoff, and Grand Final.
- **Fixture Scheduling**: Define match dates, venues, overs (5 to 20), and participating squads.

---

## 2. Automated ICC Net Run Rate (NRR) Calculation

Net Run Rate is the universal tie-breaker in cricket group stages. Because manual spreadsheet calculations often lead to contentious disputes, TallyPitch implements the standard ICC Net Run Rate algorithm automatically.

### The Formula
$$\text{NRR} = \left(\frac{\text{Total Runs Scored}}{\text{Total Overs Faced}}\right) - \left(\frac{\text{Total Runs Conceded}}{\text{Total Overs Bowled}}\right)$$

### Decimal Overs Conversion Invariant
Cricket overs are written as `14.2` (meaning 14 overs and 2 balls). For arithmetic precision, TallyPitch converts balls to fractional overs:
$$\text{Overs} = \text{Full Overs} + \frac{\text{Balls}}{6}$$
*(e.g., 14 overs and 2 balls = $14 + \frac{2}{6} = 14.333$ overs).*

### The All-Out Rule
If a team is bowled out (loses all 10 wickets) before completing their allotted overs, the calculation uses their **full maximum allotted overs quota** (e.g. 20.0 overs), rather than the overs actually batted when the final wicket fell. This rule penalizes teams for failing to bat through their innings.

### Storage & Precision
NRR values are maintained to **3 decimal places** (e.g., `+1.425`, `-0.333`) to ensure absolute accuracy in tie-breaking scenarios.

---

## 3. Points Table Sorting Logic

In accordance with official league rules, standings tables are automatically sorted using a multi-tier hierarchy:
1. **Total Points** (2 points for Win, 1 for Tie/No Result, 0 for Loss)
2. **Net Run Rate (NRR)** (Highest positive NRR ranks above)
3. **Head-to-Head Result** (Winner of direct encounter)
4. **Total Wickets Taken**
