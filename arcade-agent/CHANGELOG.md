# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.dev/spec/v2.0.0.html).

## [2.1.69] - 2025-05-12
### Changed
- Incremented version for build.
## [2.1.68] - 2025-05-12
### Changed
- Incremented version for build.
## [2.1.67] - 2025-05-12
### Changed
- Incremented version for build.
## [2.1.66] - 2025-05-12
### Changed
- Updated the Windows build script to use `pushd` and `popd` when running from a UNC path.

## [2.1.65] - 2025-04-27
### Removed
- Removed all auto-update functionality from the agent.

## [2.1.64] - 2025-04-27
### Changed
- Applied Tailwind CSS styling to the React web UI components to match the visual style of the web controller.

## [2.1.63] - 2025-04-27
### Changed
- Updated the agent auto-update batch script to include validation and retry logic for each step, and to ensure the removal of _MEI folders before starting the new agent executable.
## [2.1.62] - 2025-04-26
### Added
- Implemented the reboot agent feature, including a "Reboot Agent" button in the web UI System Status tab and a corresponding API endpoint in the agent backend to initiate a graceful shutdown and restart.

## [2.1.61] - 2025-04-26
### Changed
- Moved BigBox start/stop and delete cache controls to a new "Controls" tab within the "Arcade" tab in the web UI.

## [2.1.60] - 2025-04-26
### Changed
- Further adjusted web UI tab styling to improve matching the provided screenshot, addressing potential style conflicts.

## [2.1.59] - 2025-04-26
### Changed
- Updated web UI tab styling to match the provided screenshot, including icons and an active tab indicator.

## [2.1.58] - 2025-04-26
### Changed
- Implemented Tailwind CSS for web UI styling and created a tabbed interface.

## [2.1.57] - 2025-04-26
### Changed
- Modified the agent update script logic to rename the old executable, move the new one, check if the new one is running, and roll back if necessary.

## [2.1.56] - 2025-04-26
### Changed
- Updated CHANGELOG.md version to match agent.py for build script.

## [2.1.55] - 2025-04-26
### Changed
- Integrated implemented tab layout changes into the agent project.

## [2.1.54] - 2025-04-26
### Added
- Implemented logic to hide the console window when the agent executable is run on Windows.

## [2.1.53] - 2025-04-19
### Changed
- Configured PyInstaller to hide the console window when running the agent executable on Windows.

## [2.1.52] - 2025-04-19
### Changed
- Removed the update agent panel and actions from the System Status panel in the web UI.

## [2.1.51] - 2025-04-19
### Changed
- Modified the update batch file generation to include deleting all subfolders at the same time of deleting the old agent.exe.
- Removed the update agent panel and actions from the System Status panel in the web UI.

## [2.1.50] - 2025-04-19
### Added
- Added logging to `/api/ping` endpoint and `get_ping_payload` function to debug System Status update issues in the built executable.
- Added logging around Flask server startup in `agent.py`.

## [2.1.49] - 2025-04-19
### Changed
- Refactored the System Status tab in the web UI to include distinct "Information" and "Control" sections.

## [2.1.48] - 2025-04-19
### Fixed
- Corrected `get_ping_payload` function signature to accept `agent_version` argument.

## [2.1.47] - 2025-04-19
### Changed
- Added the image cache delete functionnality.

## [2.1.46] - 2025-04-19
### Changed
- Consolidated AGENT_VERSION to agent.py and removed unused build scripts and template file.

## [2.1.45] - 2025-04-19
### Fixed
- Corrected import paths in `image_utils.py`.

## [2.1.45] - 2025-04-19
### Fixed
- Corrected import paths in `image_utils.py`.

## [2.1.44] - 2025-04-19
### Fixed
- Corrected import paths and added missing imports in `api_routes.py`.

## [2.1.43] - 2025-04-19
### Fixed
- Added missing `import os` in `udp_broadcast.py`.

## [2.1.42] - 2025-04-19
### Fixed
- Corrected import paths in `agent.py` after refactoring.

## [2.1.41] - 2025-04-19
### Fixed
- Manually included individual Python files from `arcade_agent` directory in PyInstaller spec.

## [2.1.40] - 2025-04-19
### Fixed
- Added '.' to pathex in PyInstaller spec to help locate `arcade_agent` package.

## [2.1.39] - 2025-04-19
### Fixed
- Added '.' to pathex in PyInstaller spec to help locate `arcade_agent` package.

## [2.1.38] - 2025-04-19
### Fixed
- Used `collect_data` in PyInstaller spec to correctly include `arcade_agent` package.

## [2.1.37] - 2025-04-19
### Fixed
- Included `arcade_agent` directory in PyInstaller build to resolve `ModuleNotFoundError`.

## [2.1.36] - 2025-04-19
### Changed
- Refactored `agent.py` into smaller, functional Python files for improved organization and maintainability.

## [2.1.35] - 2025-04-19
### Changed
- Incremented agent version to 2.1.35 to reflect previous code changes.

## [2.1.34] - 2025-04-19
### Added
- Implemented temporary storage and serving of generated playlist banner images in the agent backend.
- Modified `/api/generate-image` and `/api/generate-image-gpt` endpoints to save generated images to a temporary directory and return a URL to the temporary file.
- Added new endpoint `/api/launchbox/playlists/apply_banner` to copy a temporary image to the permanent playlist banner location.

## [2.1.33] - 2025-04-19
### Added
- Added "GenAI" button to the web UI Playlists tab to generate banner images for playlists without existing images.
- Implemented frontend logic to call `/api/improve-prompt` and `/api/generate-image` endpoints to generate and display playlist banner images.

## [2.1.32] - 2025-04-19
### Added
- Added new endpoint `/api/improve-prompt` to improve image generation prompts using the Gemini API.

## [2.1.31] - 2025-04-19
### Changed
- Updated autoupdate functionality in `agent.py` to improve update check, download, and batch script execution process.

## [2.1.30] - 2025-04-18
### Changed
- Updated image generation functionality to include size input and "Use OpenAI" checkbox in the web UI.
- Modified OpenAI image generation endpoint (`/api/generate-image-gpt`) to use `requests` library instead of `openai` library.

## [2.1.29] - 2025-04-18
### Fixed
- Fixed a file encoding issue.

## [2.1.28] - 2025-04-18
### Changed
- Changed image generation endpoint to GET with prompt URL parameter and return raw image binary.

## [2.1.27] - 2025-04-18
### Fixed
- Corrected reference to google library in agent.py.

## [2.1.26] - 2025-04-18
### Fixed
- Applied manual fix to requirements.txt.

## [2.1.25] - 2025-04-18
### Changed
- Applied manual fix.

## [2.1.24] - 2025-04-18
### Fixed
- Corrected image generation flow in `/api/generate-image` to use `genai.Client` and properly extract image data from the API response, based on the working `test_image_generation_script.py`.

## [2.1.23] - 2025-04-18
### Fixed
- Fixed `module 'google.generativeai.types' has no attribute 'Modality'` error by updating `google-generativeai` dependency.

## [2.1.22] - YYYY-MM-DD
### Changed
- Removed `sys.exit(0)` from the update process, relying on `taskkill` in the batch script to stop the agent.

## [2.1.21] - YYYY-MM-DD
### Changed
- Switched image generation API from OpenRouter to direct Gemini API using `google-generativeai` SDK.

## [2.1.20] - 2025-04-18
### Fixed
- Implemented streaming for Gemini image generation via OpenRouter API to fix "Non-streaming requests not supported" error.

## [2.1.19] - 2025-04-18
### Fixed
- Corrected `NameError` in `/api/check_update` endpoint by calling the correct function `check_for_updates()`.
- Removed output redirection from the update script content generated in `check_for_updates`.
- Updated image generation API call (`/api/generate-image`) to use the correct OpenRouter endpoint (`/api/v1/chat/completions`), the specified model (`google/gemini-2.5-flash-preview`), and the correct payload structure with modalities. Also adjusted image URL extraction logic and removed unused `size` and `quality` parameters from the backend.
### Note
- The frontend image generation UI (`arcade-agent/react-ui/src/components/ImageGenerator.tsx`) needs to be updated to remove the 'Size' and 'Quality' input fields as they are no longer used by the backend.

## [2.1.18] - 2025-04-18
### Changed
- Removed the separate "Trigger Update" button from the web UI. The "Check for Update" button now initiates both the check and the update process if a new version is found.

## [2.1.17] - 2025-04-18
### Changed
- Modified build_agent_windows.sh to prevent PyInstaller from running if the React build fails.

## [2.1.16] - 2025-04-18
### Changed
- Rebuilt agent executable with latest changes.

## [2.1.15] - 2025-04-18
### Added
- Added ability to specify image size and quality from the web UI image generation form.
### Fixed
- Modified update batch script logging to prevent file locking issues.

## [2.1.13] - 2025-04-18
### Changed
- Rebuilt executable with minor code fixes (e.g., frontend import correction).

## [2.1.14] - 2025-04-18
### Added
- Added a button to the web UI status page to check for agent updates.
- Implemented backend endpoints (`/api/check_update` and `/api/trigger_update`) to handle update checks and trigger the update process.

## [2.1.12] - 2025-04-18
### Added
- Added a new tab in the web UI for image generation using Gemini 2.5 Flash via the OpenRouter API.
- Implemented a backend endpoint (`/api/generate-image`) to handle image generation requests.

## [2.1.11] - 2025-04-18
### Changed
- Modified the auto-update batch script to delete the old agent.log file, log its execution steps to update_script.log, and persist after execution for debugging.
- Added detailed logging in agent.py around the update check and agent startup.

## [2.1.10] - 2025-04-18
### Added
- Added API endpoint (`/api/launchbox/playlists/banner/<playlist_name>`) to serve playlist banner images.
- Updated web UI to fetch and display playlist banner images using the new API endpoint.

## [2.1.9] - 2025-04-18
### Added
- Added display of playlist banner images in the web UI Playlists tab.

## [2.1.8] - 2025-04-18
### Fixed
- Corrected web UI static asset loading issue when running as an executable by updating the Flask route to match the asset paths generated by the React build.

## [2.1.7] - 2025-04-18
### Fixed
- Corrected web UI API and static resource loading issues by updating frontend to use absolute paths based on agent port and configuring Vite base path.
- Fixed autoupdate process failing to replace executable by adding process termination to the update script.

## [2.1.6] - 2025-04-18
### Fixed
- Corrected web UI static resource loading issue when accessed via proxy by updating Vite configuration to use relative paths.
### Changed
- Updated agent version to 2.1.6.

## [2.1.5] - 2025-04-18
### Added
- Started a periodic thread to check for agent updates every 20 seconds.

## [2.1.4] - 2025-04-18
### Fixed
- Corrected web UI asset loading issue by updating Vite configuration to use absolute paths matching the Flask server route.

## [2.1.3] - 2025-04-18
### Changed
- Simplified autoupdate process to check a URL for the latest version and download from a URL.
- Incremented agent version to 2.1.3.

## [2.1.1] - 2025-04-18
### Changed
- Updated Screenshot Viewer UI to prevent flickering, remove loading text, and display last updated timestamp.

## [2.1.0] - 2025-04-15
### Added
- Ability to upload and update agent.exe from the web UI (System Status panel)
- AgentUpdate React component for agent upload
- Integration of AgentUpdate into SystemStatus panel
### Changed
- Improved update logging in agent.py for better troubleshooting
- Various UI and backend improvements for maintainability and debugging


## [2.0.3] - 2025-04-14
### Fixed
- Fixed log tab not displaying logs in React app
### Changed
- Modernized web UI with a dark theme, improved navigation, and enhanced log readability.
- **UI:** Applied new color palette and UI guidelines:
  - Background: #1e1e2f, Panel: #2b2c3b, Text: #fff/#a0a3b1, Accent: #4cc9f0, Success: #43aa8b, Warning: #f9c74f, Error: #f94144, Borders: #3a3b4f
  - Font: Inter, Roboto, SF Pro, sans-serif
  - Status colors standardized (Green/Yellow/Red), blinking dot for live alerts, chart color grouping

## [2.0.2] - 2025-04-13
### Fixed
- Refactored React UI Log Viewer (`LogViewer.tsx` and `App.tsx`) to establish a persistent `EventSource` connection managed by the main `App` component, ensuring logs are continuously received and displayed correctly even when switching tabs.
### Changed
- Updated agent version to 2.0.2.

## [2.0.1] - 2025-04-13
### Added
- Attempt to automatically add Windows Firewall rule for the new agent executable during the update process (`perform_update` in `agent.py`) using PowerShell. This requires the agent to be run with sufficient privileges.
### Changed
- Updated agent version to 2.0.1.

## [2.0.0] - 2025-04-13
### Added
- Initial setup for React-based web UI using Vite and TypeScript in `arcade-agent/react-ui/`.
- Configured Vite (`vite.config.ts`) to build static assets to `arcade-agent/build/react_ui_dist` with base path `/static/react/`.
- Added `@types/node` development dependency for React project.
### Changed
- Updated agent version to `2.0.0` in `agent.py`.
- Modified `agent.py` to serve the React build output:
    - Serves `index.html` from `build/react_ui_dist` for the root route (`/`).
    - Serves static assets from `build/react_ui_dist` under the `/static/react/` path.
- Removed old `template_folder` logic from Flask app initialization in `agent.py`.
### Removed
- The old Jinja2 template (`templates/index.html`) is no longer served by default (though the file still exists).

## [1.10.0] - 2025-04-13
### Added
- File monitoring thread (`monitor_for_update`) to handle agent updates instead of using a batch script.
- Custom version comparison logic (`parse_agent_filename`, `find_latest_agent_exe`) to handle version suffixes (e.g., `1.10.0b`).
- Logic to determine the next available suffix when renaming `agent-new.exe` if an executable with the same base version already exists.
### Changed
- Updated agent version to 1.10.0.
- Simplified `/api/update-agent` endpoint to only save the uploaded file as `agent-new.exe`.
- Agent startup check now uses custom version comparison to find the truly latest executable (including suffixes).
- Update process now relies on the monitoring thread to detect `agent-new.exe`, validate it, rename it (with suffix if needed), and launch the new version before the old one exits.
### Removed
- Removed the `perform_update` function and batch script generation logic.

## [1.9.2] - 2025-04-13
### Changed
- Updated agent version to 1.9.2.
- Made agent update process more robust (`perform_update` function):
    - Validates the new executable using `--get-version` before proceeding.
    - Aborts update if the new executable is invalid or version cannot be determined.
    - Aborts update if renaming the new executable fails.
    - Generated `update.bat` now checks if the new process started successfully before killing the old one using its PID.
    - Old agent process no longer explicitly exits after launching `update.bat`.
### Fixed
- Fixed `NameError` in `perform_update` function when generating `update.bat`. The script now correctly uses the dynamically determined `current_exe_name` for `taskkill` and `del` commands instead of the removed `AGENT_EXECUTABLE` global. (Note: This fix was part of 1.9.1 but is implicitly included in the new logic).
- Fixed JavaScript bug in the web UI (`index.html`) where CPU and RAM usage were not updating due to incorrect element IDs being targeted in the `updateSystemStatus` function.

## [1.9.1] - 2025-04-12
### Fixed
- Fixed `NameError` in `perform_update` function when generating `update.bat`. The script now correctly uses the dynamically determined `current_exe_name` for `taskkill` and `del` commands instead of the removed `AGENT_EXECUTABLE` global.
### Changed
- Updated agent version to 1.9.1.

## [1.9.0] - 2025-04-12
### Added
- Filesystem API Endpoints (Restricted to LaunchBox Path):
    - `GET /api/launchbox/basepath`: Returns the detected LaunchBox path.
    - `GET /api/filesystem/list?path=...`: Lists directory contents within the LaunchBox path.
    - `GET /api/filesystem/content?path=...`: Gets content of allowed text files within the LaunchBox path.
- Added `is_path_safe` validation function to ensure API calls stay within the `LAUNCHBOX_PATH`.
- Web UI File Browser Tab (`index.html`):
    - New "File Browser" tab.
    - Displays current path, file/folder list with icons.
    - Allows navigation into subdirectories within LaunchBox path.
    - Allows viewing content of allowed text files.
    - Includes "Go Up" button functionality.
### Changed
- Updated agent version to 1.9.0.

## [1.8.0] - 2025-04-12
### Added
- Agent startup check: Compares versions of `agent-*.exe` files in its directory and launches the newest one, exiting if the current process isn't the latest. Uses `packaging` library for version parsing.
- `--get-version` command-line argument to print the agent version and exit (used during update process).
### Changed
- Updated agent version to 1.8.0.
- Modified `perform_update` function:
    - Saves incoming update file as `agent-new.exe`.
    - Runs `agent-new.exe --get-version` to determine the new version.
    - Renames `agent-new.exe` to `agent-{new_version}.exe`.
    - Generates `update.bat` to simply start `agent-{new_version}.exe` (no kill/del needed due to self-check).
- Modified `build_agent.bat` to clean `build`, `dist`, and `.spec` files before running PyInstaller and added `--clean` and `--runtime-tmpdir .` flags to the `pyinstaller` command. (Note: Build output is still `agent.exe` in `dist/`; manual rename or copy needed after build for versioned deployment).
### Dependencies
- Added `packaging` to `requirements.txt`.

## [1.7.5] - 2025-04-12
### Added
- New API endpoint `POST /api/launchbox/games/details` that accepts a list of game IDs and returns full details for found games.
### Changed
- Refactored playlist game display in web UI (`index.html`):
  - Removed embedding of all game data in HTML.
  - Removed client-side `gameLookup` table and parsing logic.
  - Modified `showPlaylistGames` JavaScript function to fetch game details for the specific playlist on demand using the new `/api/launchbox/games/details` endpoint.
- Updated agent version to 1.7.5.

## [1.7.4] - 2025-04-12
### Added
- Added `promptAddToPlaylist` JavaScript function in `index.html` to allow adding orphaned games to playlists.
- Made orphaned game cards clickable in the web UI to trigger the add-to-playlist prompt.
- Added `data-game-id` attribute to orphaned game cards for easier UI manipulation after assignment.
### Changed
- Updated agent version to 1.7.4.

## [1.7.3] - 2025-04-12
### Added
- Added cache-control headers (`no-cache`, `no-store`, `must-revalidate`) to the main `/` route response to prevent browser caching of `index.html`.
- Modified the `perform_update` function to generate an `update.bat` script that explicitly deletes the old `agent.exe` before moving the new one, potentially improving update reliability related to PyInstaller temporary files.
- Updated agent version to 1.7.3.

## [1.7.2] - 2025-04-12
### Added
- Added "Log" tab to the web UI (`index.html`).
- Implemented JavaScript using `EventSource` to connect to the `/log` endpoint and stream log content live into the new tab.
- Added logic to automatically close the `EventSource` connection when navigating away from the Log tab to conserve resources.
### Changed
- Updated agent version to 1.7.2.

## [1.7.1] - 2025-04-12
### Added
- Added `DELETE /api/launchbox/playlists/<playlist_name>` endpoint to delete playlist XML files.
- Added delete button ('X') next to each playlist in the web UI (`index.html`).
- Added `deletePlaylist` JavaScript function to handle confirmation and API call for deletion.
- Added debug logging in `agent.py` for extracted game/playlist IDs.
- Added debug logging in `index.html` JavaScript for game lookup table creation and playlist game display logic.
### Changed
- Updated agent version to 1.7.1.
- Modified playlist `<li>` structure in `index.html` to separate clickable name span from delete button.

## [1.7.0] - 2025-04-12
### Added
- Implemented periodic UDP broadcast of agent status (ping payload) every 2 seconds to port 5152.
- Added `get_broadcast_address()` function to determine the appropriate subnet broadcast address using `psutil`.
- Started UDP broadcast in a separate background thread on agent launch.
### Changed
- Refactored status gathering logic into `get_ping_payload()` function.
- Updated `/api/ping` HTTP endpoint to use `get_ping_payload()`.
- Updated agent version to 1.7.0.

## [1.6.11] - 2025-04-12
### Fixed
- Improved reliability of disk usage reporting in `/api/ping` on Windows by using `psutil.disk_usage('C:\\')` instead of `shutil.disk_usage('/')`, addressing potential errors on Windows 10.

## [1.6.10] - 2025-04-12
### Changed
- Updated agent version to 1.6.10.
### Fixed
- Corrected JavaScript implementation in `index.html` for embedding game data and displaying games when a playlist is clicked.
- Corrected main route (`/`) in `agent.py` to only pass static data needed for initial template render, preventing server-side errors when accessing dynamic status variables.

## [1.6.9] - 2025-04-12
### Added
- Added `/api/launchbox/stop_bigbox` endpoint to remotely stop BigBox.exe using `psutil`.
- Added "Stop BigBox" button to web UI, conditionally displayed based on running status.
- Added clickable playlist names in web UI to display games within that playlist (NOTE: JavaScript implementation currently has errors and needs debugging).
### Changed
- Updated agent version to 1.6.9.

## [1.6.8] - 2025-04-12
### Added
- Added `is_process_running` helper function to check for running processes (e.g., "BigBox.exe") using `psutil`.
- Added `bigbox_running` status to `/api/ping` response.
- Added BigBox running status display (with start button) to System Status tab in web UI.
- Added `/api/launchbox/start_bigbox` endpoint to remotely start BigBox.exe.
- Added `find_orphaned_games` function and `/api/launchbox/orphaned_games` endpoint.
- Added "Orphaned Games" tab to web UI to display games not found in any playlist.
### Changed
- Updated agent version to 1.6.8.
- Main web route (`/`) now passes less initial data; status info (Disk, CPU, RAM, BigBox) is fetched dynamically via JS.
### Fixed
- Corrected filename sanitization in `serve_game_image` to handle characters like colons (`:`) by replacing them with underscores (`_`) to match LaunchBox media naming conventions.
- Corrected XML parsing logic in `get_playlists` to match LaunchBox playlist file structure (`<Playlist>/<Name>` and `<PlaylistGame>/<GameId>`).
- Removed server-side Jinja logic for dynamic status elements in `index.html`.

## [1.6.5] - 2025-04-12
### Changed
- Updated agent version to 1.6.5.
- Enhanced `get_playlists` to include `game_count`.
- Passed playlist data (including counts) to web UI template.
- Updated web UI (`index.html`) to display playlists with game counts in the "Playlists" tab.
### Fixed
- Reverted incorrect URL encoding fix in `serve_game_image`; Flask handles decoding automatically.

## [1.6.4] - 2025-04-12
### Changed
- Set logging level to DEBUG for more verbose output.
- Updated agent version to 1.6.4.
### Fixed
- Corrected how the SHA256 checksum is received in `/api/update-agent` (now expects it in `request.form` instead of `request.files`).

## [1.6.3] - 2025-04-12
### Added
- Implemented SHA256 checksum verification to ensure the integrity of the agent update file during transfer.
- Added disk space reporting to the `/api/ping` endpoint.
- Restructured web UI (`index.html`) into tabs: System Status, Game List, Playlists.
- Added disk space display (text and progress bar) to System Status tab in web UI.
### Changed
- Now logging the Python version at startup.
- Updated agent version to 1.6.3.
### Fixed
- Fixed `NameError: name 'log' is not defined` by moving the initial Python version log call to after the `log` function definition.

## [1.6.2] - 2025-04-12
### Added
- Global Flask error handler (`@app.errorhandler(Exception)`) to catch unhandled exceptions during request processing.
- Logging of full tracebacks for unhandled exceptions to `agent.log`.
### Changed
- Unhandled exceptions now return a JSON `{"error": "Internal Server Error", "message": "..."}` with HTTP status 500 instead of crashing the agent.
- Updated `AGENT_VERSION` constant to "1.6.2".
- Changed log format to include level name (`%(asctime)s %(levelname)s: %(message)s`).
- Explicitly log XML parsing errors with `level=logging.ERROR`.
### Fixed
- Prevented agent crashes caused by exceptions within Flask route handlers.

## [1.6.1] - YYYY-MM-DD
### Note
- Reflects the version found in agent.py code (1.6.1) before this session started. Actual changes for 1.6.1 are unknown without prior history.
### Added
- Added `build_agent.bat` to simplify building the one-file executable.
- Improved formatting and readability of `readme.txt`.
- Initial Changelog file created.
