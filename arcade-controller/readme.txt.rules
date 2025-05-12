ARCADE CONTROLLER - README
==========================

The Arcade Controller is a Python-based desktop application designed to manage and monitor multiple arcade and pinball machines running the Arcade Agent. It provides a centralized interface to edit control layouts, monitor machine status, push agent updates, and manage LaunchBox game configurations remotely.

FEATURES
--------
*   Live dashboard listing all connected machines (from `machines.json`).
*   Ping/health monitoring and agent version check.
*   Edit control layout per machine (joystick, spinner, lightgun, etc.).
*   Trigger remote update of `agent.exe`.
*   View orphaned games (not in playlists).
*   Add games to LaunchBox playlists remotely.

REQUIREMENTS
------------
*   Python 3.9+
*   Tkinter (included with standard Python installations)
*   `requests` library

Install `requests` if needed:
    `pip install requests`

RUNNING THE CONTROLLER
----------------------
Launch the controller app from its directory:
    `python app.py`

Or run the batch file:
    `run_controller.bat`

The controller will load machine definitions from `machines.json`, a file containing entries like:
    ```json
    [
      {
        "name": "Simpsons",
        "host": "simpsons.local",
        "type": "arcade"
      },
      {
        "name": "Tekno",
        "host": "tekno.local",
        "type": "arcade"
      }
    ]
    ```

UI OVERVIEW
-----------
*   Machines are listed in a table with columns for name, type, status, last seen, agent version, disk space (total/free GB), CPU %, RAM %, and BigBox Status (Running/Stopped/N/A).
*   Buttons:
    *   Refresh: ping all machines
*   Edit Layout: open layout editor window
    *   Update Agent: Upload new agent binary to ALL online machines. A progress bar will show the update status.
    *   View Games: see orphaned games and assign them to playlists

API INTERACTIONS
----------------
The controller communicates with each machine's agent via HTTP (port 5151). It uses the following endpoints on the agent:

*   `GET /api/ping`
*   `GET/PUT /api/control-layout`
*   `GET /api/launchbox/games`
*   `GET /api/launchbox/playlists`
*   `GET /api/launchbox/orphaned_games` (New - Controller UI doesn't use this yet)
*   `POST /api/launchbox/start_bigbox` (New - Controller UI doesn't use this yet)
*   `POST /api/launchbox/stop_bigbox` (New - Controller UI doesn't use this yet)
*   `POST /api/launchbox/playlists/add`
*   `POST /api/update-agent`

NOTES
-----
*   Each arcade machine must have its agent running and accessible on the network.
*   Hostnames can be `.local` (Bonjour/mDNS) or static IPs.
*   Ensure agent and controller are on the same LAN and firewall rules allow communication on port 5151.

LICENSE
-------
MIT (or project-specific license placeholder)
