ARCADE AGENT SYSTEM - PROJECT OVERVIEW AND CURRENT STATE
=======================================================

🔍 OBJECTIVE
-----------
Build a unified management system to control and maintain multiple arcade-style machines (running BigBox/LaunchBox and Visual Pinball), from a central Windows-based controller. Each machine runs a lightweight local agent that can:

*   Identify itself (type, hostname, controls)
*   Share its configured game list and playlists (LaunchBox)
*   Report control layouts (joysticks, spinners, lightguns, etc.)
*   Be remotely updated via a single executable push
*   Serve local diagnostics (logs, UI view of installed games)

The long-term goal is to make this system modular, scalable (can handle more machines), and partially self-aware (e.g. flag missing game assets, detect configuration drift, validate control compatibility).


🌐 INFRASTRUCTURE SUMMARY
------------------------
*   Central Controller (Windows PC)
    *   Hosts a dashboard UI (Tkinter-based)
    *   Discovers and interacts with all arcade machines
    *   Allows control layout editing, game list inspection, agent update deployment

*   Arcade/Pinball Machines (Windows 10/11)
    *   Each runs agent.exe (built from agent.py)
    *   Frontend: LaunchBox + BigBox (Arcade), or Visual Pinball X + PinUP Popper (Pinball)
    *   Source games via SMB shares (Unraid-hosted)


🌍 CURRENT ARCHITECTURE
----------------------
*   Machine Agent (`arcade-agent/`)
*   `agent.py` (Flask app, port 5151) - Current Version: 2.0.2
*   See `arcade-agent/readme.txt` and `arcade-agent/CHANGELOG.md` for details.
*   Key APIs: `/api/ping`, `/api/control-layout`, `/api/launchbox/*`, `/api/update-agent`

*   Central Controller (`arcade-controller/`)
    *   `app.py` (Tkinter UI)
    *   See `arcade-controller/readme.txt` and `arcade-controller/CHANGELOG.md` for details.
    *   Reads `machines.json` for target hosts.
    *   Interacts with Agent APIs.


🛠️ DEVELOPMENT WORKFLOW
----------------------
When making changes to either the Agent or the Controller:

1.  **Implement Code Changes:** Modify the relevant Python files (`agent.py` or `app.py`), HTML templates, etc.
2.  **Update Version (Agent Only):** If changes were made to `agent.py`, increment the `AGENT_VERSION` constant within the file.
3.  **Update Changelog:** Add a detailed entry under a new version heading (or "[Unreleased]") in the corresponding `CHANGELOG.md` file (`arcade-agent/CHANGELOG.md` or `arcade-controller/CHANGELOG.md`). Follow the "Keep a Changelog" format.
4.  **Update READMEs:** Briefly mention significant new features or changes in the relevant `readme.txt` files (root, agent, or controller).
5.  **Install Dependencies (Agent Only):** If new libraries were added to `arcade-agent/requirements.txt`, ensure they are installed in the build environment (`pip install -r arcade-agent/requirements.txt`).
6.  **Build Executable (Agent Only):** Run the `arcade-agent\build_agent.bat` script manually to create the updated `agent.exe` in the `dist` folder.
7.  **Test:** Thoroughly test the changes.
*   **AI Modifications:** When Cline (the AI assistant) modifies files, it must always use the `write_to_file` operation to ensure file integrity, rather than attempting partial replacements with `replace_in_file`.


📆 KEY FEATURES IMPLEMENTED (Agent v2.0.3)
-----------------------------------------
- Fixed log tab not displaying logs in React app

📆 KEY FEATURES IMPLEMENTED (Agent v2.0.0)
-----------------------------------------
*   Control layout reporting + editing.
*   Remote agent updating (with checksum verification, version checking, suffix handling). Attempts to add firewall rule for new version (requires admin privileges).
*   LaunchBox integration (games, playlists, add to playlist, orphaned games, game details API).
*   System monitoring (Disk, CPU, RAM, BigBox running status) via API and Web UI.
*   Remote BigBox start/stop via API and Web UI.
*   Tabbed Web UI (Status, Games, Playlists, Orphaned, Log, File Browser).
*   Persistent live log streaming via SSE in React UI (v2.0.2+).
*   Robust error handling.
*   Filesystem browsing API (restricted to LaunchBox path).


🌐 VISION (NEXT PHASES)
----------------------
*   Integrate MAME control mapping validator.
*   Remote game asset management.
*   Cabinet compatibility reporting.
*   Pinball integration.
*   Controller UI enhancements (dark mode, filtering, use new agent APIs).


✅ DELIVERABLES FOR NEW DEVELOPERS
---------------------------------
*   `agent.py` (current version)
*   `agent.spec` file
*   `build_agent.bat` (for building `agent.exe`)
*   `app.py` (controller UI)
*   `run_controller.bat` (for running the controller)

*NOTE: The primary web UI is now a React application located in `arcade-agent/react-ui/`. The `templates/index.html` file is no longer directly served.*


ℹ️ NOTES FOR HANDOFF
-------------------
*   Each arcade machine runs a unique copy of the agent.
*   LaunchBox paths are dynamically resolved using `os.path.expanduser("~")`.
*   All file parsing is local XML (games, playlists).
*   The controller (`arcade-controller/app.py`) queries agents using `/api/*` endpoints.
*   Game art is optional, UI gracefully degrades.
*   The agent web UI has been migrated to React (v2.0.0). The playlist feature may still have JavaScript issues.

LICENSE
-------
MIT (or project-specific license placeholder)

BUILDING THE EXECUTABLE
-----------------------
To build a one-file executable (`agent.exe`):

1.  Build the React UI:
        `cd arcade-agent/react-ui && npm run build && cd ..`
2.  Run the build script:
        `arcade-agent\build_agent.bat`

*   Using Command Prompt:
        `pyinstaller --onefile --add-data "templates;templates" --add-data "build/react_ui_dist;static/react" agent.py`
    Or run the batch file:
        `build_agent.bat`

*   Using PowerShell:
        `pyinstaller --onefile --add-data "templates:templates" --add-data "build/react_ui_dist:static/react" agent.py`
