# Arcade Agent

A Python-based agent for arcade machine management, featuring a modern web dashboard for real-time monitoring and control.

## Features
- **Modern Dark-Themed Web UI**: Sleek dashboard with tab navigation, real-time log viewer, and status panels.
- **Log Streaming**: Live logs streamed to the web UI via Server-Sent Events (SSE).
- **Status Monitoring**: View system status, running processes, and more.
- **Game & Playlist Management**: Browse games, playlists, and orphaned games.

## Autoupdate
The agent automatically checks for and downloads updates from a remote server.
- The agent checks `https://arcade.elierodrigue.cloud/api/agent/latest_version` every 20 seconds for a newer version.
- If a newer version is found, it downloads the latest executable from `https://arcade.elierodrigue.cloud/api/agent/download/latest`.
- The agent will then automatically replace the running executable with the downloaded version and restart.

## UI Guidelines & Color Palette

### Color Palette (Dark Theme)
| Purpose        | Color        | Notes                        |
|--------------- |------------- |----------------------------- |
| Background     | #1e1e2f      | Very dark blue-gray          |
| Card/Panel BG  | #2b2c3b      | Slightly lighter for contrast|
| Primary Text   | #ffffff      | Clean white                  |
| Secondary Text | #a0a3b1      | Muted light gray             |
| Accent/Primary | #4cc9f0      | Bright blue for focus areas  |
| Success        | #43aa8b      | Green for healthy systems    |
| Warning        | #f9c74f      | Yellow-orange for warnings   |
| Error/Critical | #f94144      | Bright red for alerts        |
| Chart Line     | #577590      | Soft blue-gray (charts)      |
| Chart Fill     | #4cc9f020    | 20% opacity blue (chart fill)|
| Border/Divider | #3a3b4f      | Subtle divider lines         |

### Font
- Uses a modern sans-serif font stack: **Inter**, **Roboto**, **SF Pro**, Arial, sans-serif.

### UX Tips for Server Monitoring
- **Green = Normal**, **Yellow = Degraded**, **Red = Critical** — used consistently for status.
- Blinking dots (not flashing backgrounds) are used for live alerts.
- Chart color grouping: CPU (blue), Memory (purple), Disk (orange), Network (green).

### Example CSS Variables
```css
:root {
  --bg-main: #1e1e2f;
  --bg-header: #2b2c3b;
  --primary-text: #ffffff;
  --secondary-text: #a0a3b1;
  --accent: #4cc9f0;
  --success: #43aa8b;
  --warning: #f9c74f;
  --error: #f94144;
  --chart-line: #577590;
  --chart-fill: #4cc9f020;
  --border: #3a3b4f;
}
```

These guidelines ensure a modern, accessible, and visually appealing UI for the Arcade Agent dashboard.

## Getting Started

1. **Install Dependencies**
   - Python backend: See `requirements.txt`
   - Frontend: `cd arcade-agent/react-ui && npm install`

2. **Run the Agent**
   - Start backend: `python agent.py`
   - Start frontend (dev): `cd arcade-agent/react-ui && npm start`
   - Or build frontend: `npm run build` (served by backend automatically)

3. **Access the Dashboard**
   - Open your browser to `http://localhost:5151/`

## Versioning & Changelog
- See `CHANGELOG.md` for all notable changes.
- The backend version is defined in `agent.py` as `AGENT_VERSION`.

## Screenshots
![Web UI Screenshot](screenshot.png)

## License
MIT
