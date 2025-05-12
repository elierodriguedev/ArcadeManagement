iARCADE AGENT - README
=====================

The Arcade Agent is a lightweight Python-based service designed to run on arcade and pinball machines powered by Windows. It exposes a local API and web-based UI that integrates with LaunchBox to provide remote control layout editing, game and playlist inspection, and support for centralized management through a controller application.

FEATURES
--------
*   Control layout API with joystick, button, lightgun, spinner, and pedal tracking.
*   LaunchBox integration: reads games from `Data/Platforms`, playlists from `Data/Playlists`.
*   React-based Web UI (v2.0.0+) showing System Status (game count, disk/CPU/RAM usage, BigBox status with start/stop buttons), Game List (with logos), Playlists (with game counts, clickable), Orphaned Games, Log Viewer, and File Browser.
*   Dynamic Clear Logo lookup (`Images/<Platform>/Clear Logo/<GameTitle>-01.png`), handles invalid filename characters (v1.6.6+).
*   Remote agent update via API with SHA256 checksum verification (v1.6.3+). Attempts to add Windows Firewall rule for new version (requires admin privileges) (v2.0.1+).
*   Persistent realtime system log view via `/log` in React UI (v2.0.2+).
*   Improved stability: Global error handling prevents crashes on request errors (v1.6.2+).

ENDPOINTS
---------
Endpoint                     | Description
-----------------------------|------------------------------------
`/api/ping`                  | Returns hostname, version, type, disk/CPU/RAM usage, BigBox status
`/api/control-layout`        | GET and PUT control config
`/api/launchbox/start_bigbox`| Attempts to start BigBox.exe
`/api/launchbox/stop_bigbox` | Attempts to stop BigBox.exe (v1.6.9+)
`/api/launchbox/games`       | List all games across platforms (sorted alphabetically)
`/api/launchbox/playlists`   | List all LaunchBox playlists
`/api/launchbox/playlists/add`| Add one or more games to a playlist
`/api/launchbox/orphaned_games`| List games not found in any playlist
`/api/update-agent`          | Upload a new `agent.exe` to replace current
`/`                          | React-based Web UI
`/static/react/<path:path>`  | Serves static assets for React UI
`/img/<platform>/<title>`    | Serves Clear Logo PNG from disk (handles special chars)
`/log`                       | Live updating log output in browser

LAYOUT STORAGE
--------------
The control layout is saved in a local file: `control-layout.json`

Example schema:
    ```json
    {
      "players": 2,
      "joysticks": 2,
      "buttonsPerPlayer": 6,
      "spinners": 1,
      "trackballs": 0,
      "lightguns": 0,
      "steeringWheels": 0,
      "pedalSets": 0
    }
    ```

WEB UI
------
*   Now a React application (v2.0.0+).
*   See `arcade-agent/react-ui/` for the React source code.

RUNNING THE AGENT
-----------------
1.  Install dependencies:
        `pip install flask`

2.  Then run directly:
        `python agent.py`

BUILDING THE EXECUTABLE
-----------------------
To build a one-file executable:

For Windows (`agent.exe`):
*   **On Windows:** Use the provided batch script.
    1.  Build the React UI:
            `cd react-ui && npm run build && cd ..`
    2.  Run the build script:
            `build_agent.bat`
*   **On Linux (Cross-Compiling):** Use Wine to run a Windows Python environment and PyInstaller.

The `build_agent_windows.sh` script automates this process:

1.  Ensure you have Wine and Winetricks installed. The script will attempt to install them if they are not present.
2.  Make the build script executable:
        `chmod +x build_agent_windows.sh`
3.  Run the build script:
        `./build_agent_windows.sh`

The script will:
*   Ensure Wine and Winetricks are installed.
*   Build the React UI.
*   Use the embedded `pyinstaller.exe` within Wine to build the Windows executable.

If the script runs successfully, the `agent.exe` executable will be in the `dist/` subdirectory within your Wine environment (e.g., `~/.wine/drive_c/data/ArcadeProject/arcade-agent/dist/agent.exe`).

For Linux (`agent`):
*   Use the provided shell script.
    1.  Build the React UI:
            `cd react-ui && npm run build && cd ..`
    2.  Make the build script executable:
            `chmod +x build_agent_linux.sh`
    3.  Run the build script:
            `./build_agent_linux.sh`

NOTES
-----
*   Works on Windows 10 and 11.
*   The Linux executable is built for the architecture it is built on.
*   Flask runs on port 5151 by default.
*   LaunchBox data is resolved per-user using `os.path.expanduser("~")`.
*   Compatible with controller apps using the documented REST API.

DELIVERABLES FOR NEW DEVELOPERS
---------------------------------
*   `agent.py` (current version)
*   `agent.spec` file
*   `build_agent.bat` (for building `agent.exe`)
*   `app.py` (controller UI)
*   `run_controller.bat` (for running the controller)

*NOTE: The primary web UI is now a React application located in `arcade-agent/react-ui/`. The `templates/index.html` file is no longer directly served.*

NOTES FOR HANDOFF
-------------------
*   Each arcade machine runs a unique copy of the agent.
*   LaunchBox paths are dynamically resolved using `os.path.expanduser("~")`.
*   All file parsing is local XML (games, playlists).
*   The controller (`arcade-controller/app.py`) queries agents using `/api/*` endpoints.
*   Game art is optional, UI gracefully degrades.
*   The agent web UI has been migrated to React (v2.0.0). The playlist feature may still have JavaScript issues.
