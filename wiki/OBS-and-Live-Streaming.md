# OBS & Live Broadcast Streaming

Many grassroots clubs and weekend leagues broadcast their matches to YouTube, Facebook Live, or club websites using OBS Studio, Streamlabs, or vMix. Legacy apps charge high per-game fees just to generate an overlay. TallyPitch provides free, real-time broadcast score overlays with zero fees.

---

## 1. How the Live Overlay Works

TallyPitch includes a dedicated broadcast mode accessible via URL parameter:

```text
http://<your-host>/index.html?overlay=true
```

When opened in overlay mode:
- The full navigation bar, tournament tabs, and scoring controls are hidden.
- The interface renders a clean, transparent **lower-third broadcast graphic**.
- As deliveries are scored on the scoring device, updates stream in real-time to the overlay.

---

## 2. OBS Studio Setup (Step-by-Step)

1. **Open OBS Studio** and navigate to your active match scene.
2. Under the **Sources** panel, click **+** and select **Browser**.
3. Name the source (e.g., `TallyPitch Scoreboard`).
4. In the Browser Source Properties:
   - **URL**: `http://localhost:8080/index.html?overlay=true` (or your hosted public URL).
   - **Width**: `1920`
   - **Height**: `1080`
   - **Custom CSS**: Leave empty or style as needed (the overlay has a transparent background by default).
   - Check **Shutdown source when not visible** (optional).
   - Check **Refresh browser when scene becomes active**.
5. Click **OK**. Position the lower-third graphics banner across the bottom of your video canvas.

---

## 3. Realtime Synchronization

When connected to the Node.js realtime server (`server/realtime.js`), live events (`delivery_recorded`, `wicket_fallen`, `over_completed`, `innings_changed`) are pushed over WebSockets. Spectators and stream viewers see updates within **<50ms** of the scorer entering the ball.
