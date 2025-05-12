# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.3] - 2025-04-12
### Fixed
- Fixed UI freeze during agent updates by moving the update loop (`_update_thread_func`) to a background thread.
- Replaced Tkinter event-based communication for updates with a thread-safe `queue.Queue` (`update_queue`) for more reliable progress and completion reporting.
- Implemented `check_update_queue` function scheduled via `root.after` to process messages from the queue in the main UI thread.
- Fixed `NameError: name 'check_update_queue' is not defined` by moving the `check_update_queue` function definition before `run_ui`.

## [1.2.2] - 2025-04-12
### Added
- Added double-click functionality on the machine list to open the selected agent's web UI (`http://{hostname}:5151/`) in the default browser (`open_agent_ui` function using `webbrowser`).
### Changed
- Modified "Update Selected Agent" functionality to support updating multiple selected machines simultaneously.
  - Renamed button to "Update Selected".
  - Renamed function to `update_selected_agents` and updated logic to handle a list of hostnames.
  - Renamed helper `get_selected_hostname` to `get_selected_hostnames` to return the list of selected item IDs.
- Updated single-machine actions ("Edit Layout", "View Games") to operate on the *first* selected machine if multiple are selected.
- Added summary message box after "Update Selected" completes, listing any machines that failed to update.
- Refactored agent update process (`update_selected_agents`) to run in a background thread, preventing UI freezes during updates. Used Tkinter events (`<<UpdateProgress>>`, `<<UpdateComplete>>`) for thread-safe UI updates (status label, progress bar).
### Removed
- Removed "Update All Agents" button and associated `update_all_agents` function.

## [1.2.1] - 2025-04-12
### Changed
- Reverted discovery saving logic: `machines.json` is now saved immediately by the UDP listener thread when a new machine is discovered, instead of being deferred to the UI refresh cycle.
- Refined locking in `save_machines` and `udp_listener_thread` to perform file I/O *after* releasing the lock, minimizing potential blocking time while still saving immediately.
### Fixed
- Fixed `NameError: name 'machines_list' is not defined` in the `print` statement within the `save_machines` function (corrected to `machines_to_save`).
- Ensured machines loaded from `machines.json` are displayed immediately on startup by calling `populate_initial_list` before the first UI refresh.
### Removed
- Removed `config_dirty` flag as saving is no longer deferred.

## [1.2.0] - 2025-04-12 (Hybrid Discovery & Control)
### Added
- Reintroduced loading machine configurations from `machines.json` at startup (`load_machines`).
- Implemented saving of newly discovered machines (via UDP) back to `machines.json` (`save_machines`).
- Added `known_machines_config` dictionary to store the configuration loaded/saved from JSON.
- Reintroduced manual "Refresh (Manual Ping)" button and `manual_ping_all` function to perform HTTP pings on demand for all known machines.
- Added "Update Selected Agent" button and `update_selected_agent` function to force update on a single machine regardless of status.
- Reintroduced `ping_machine(hostname)` function for manual HTTP pings.
### Changed
- UDP listener (`udp_listener_thread`) now updates `discovered_machines` (real-time data) and adds new hostnames to `known_machines_config` (persistent config).
- UI refresh (`refresh_ui`) now displays machines based on `known_machines_config`, using data from `discovered_machines` to show real-time status (Online/Offline based on UDP `last_seen`).
- "Update All Agents" button (`update_all_agents`) now attempts to update all machines listed in `known_machines_config`, ignoring their current Online/Offline status.
- Refactored agent update logic into `attempt_single_update(hostname, filepath)` used by both "Update All" and "Update Selected".
- Adjusted button layout and column widths.
### Removed
- Removed previous `update_agent` function (replaced by `update_all_agents` and `update_selected_agent`).

## [1.0.0] - 2025-04-12 (Assumed previous version)
### Added
- Initial Changelog file.
- Added `run_controller.bat` to simplify running the controller application.
- Improved formatting and readability of `readme.txt`.
- Implemented mass agent update functionality, allowing the controller to update all online agents with a single action.
- Added a progress bar to the UI to visually indicate the progress of the mass agent update.
### Fixed
- Fixed a bug where the `status_label` and `progress_bar` were not accessible in the `update_agent` function due to scoping issues.
- Implemented SHA256 checksum verification to ensure the integrity of the agent update file during transfer.
- Fixed a bug where the `root` was not accessible in the `update_agent` function due to scoping issues.
- Updated the agent version to 1.6.10
- Added disk space reporting to the controller UI, displaying total and free disk space in GB in new columns.
- Added CPU and RAM percentage display to the controller UI table.
- Added BigBox running status display ("Running" / "Stopped" / "N/A") to the controller UI table.
### Fixed
- Corrected how the SHA256 checksum is sent during agent update (now uses `data` parameter instead of `files`).
- Fixed bug in `ping_machine` where disk space, CPU, RAM, and BigBox status info from agent ping was not being returned correctly, preventing display in UI.
