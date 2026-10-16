# Design System & Theme Foundations

## Visual Principles
- **High-Contrast Ground Readability**: Clean slate surfaces with Royal Pitch Sapphire accents designed for high visibility under daylight and night matches.
- **Contextual Discovery**: Use accessible tooltips and clear scoreboards to keep matchday consoles focused on the active delivery.
- **Ad-Free Cleanliness**: Uncluttered interfaces prioritizing ball scoring speed and zero accidental misclicks.

## Color Tokens (TallyPitch Sapphire System)

### Core Palette
- **Background Root**: `#ffffff` (Pitch White) / `#0f172a` (Slate 900 Dark)
- **Surface**: `#f8fafc` (Slate 50) / `#1e293b` (Slate 800 Dark)
- **Border**: `#cbd5e1` (Slate 300)
- **Border Input**: `#64748b` (Slate 500)
- **Text Primary**: `#0f172a` (Slate 900)
- **Text Muted**: `#475569` (Slate 600)
- **Accent Primary**: `#1d4ed8` (Royal Pitch Sapphire)
- **On-Accent**: `#ffffff`
- **Danger / Wicket**: `#b91c1c` (Deep Crimson)
- **Success / Boundary**: `#047857` (Emerald Turf)
- **Warning / Extra**: `#9a3412` (Warm Amber)

## Typography
- **Primary Sans**: `Plus Jakarta Sans`, `Inter`, system-ui, sans-serif
- **Scoreboard Monospace**: `JetBrains Mono`, `SFMono-Regular`, Menlo, monospace

## Tooltips & Overlays
- **Tooltip Background**: `#0f172a` (Dark) with `#f8fafc` text
- **Z-Index System**:
  - Base Layout: `0 - 10`
  - Sticky Match HUD / Score Header: `100`
  - Floating Drawers / Sheets: `1000`
  - Modals / Toss Dialog: `5000`
  - Tooltips & Live Popovers: `99999`
