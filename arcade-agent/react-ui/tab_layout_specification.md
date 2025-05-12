# Agent Web UI Tab Layout Specification

## Overview

This document specifies the new tab layout for the Arcade Agent web user interface. The UI will feature three main tabs to organize different functionalities: Server, Arcade, and Pinball.

## Tab Structure

The main interface will consist of the following top-level tabs:

1.  **Server**: Contains components related to the agent's status, logging, and utility functions.
2.  **Arcade**: Contains components for managing Arcade-specific game data and lists.
3.  **Pinball**: Reserved for future Pinball-specific functionalities.

## Server Tab

The Server tab will include the following components:

*   **Status**: Displays the current status of the agent.
    *   *Requirement*: Include a toggle switch within this sub-tab to select between "Arcade" and "Pinball" modes.
*   **Log**: Displays the agent's operational logs.
*   **Screenshot**: Allows viewing screenshots captured by the agent.
*   **Image Generation**: Provides tools for generating images.
*   **Check for Update**: Allows checking for and initiating agent updates.

## Arcade Tab

The Arcade tab will include the following components:

*   **Playlists**: Manages game playlists.
*   **Games**: Displays and manages the list of games.
*   **Orphaned Games**: Lists games that are not associated with any playlist.

## Pinball Tab

The Pinball tab will initially be empty but is designed to accommodate future components related to Pinball functionalities.

## Future Considerations

The Pinball tab is a placeholder for future expansion. Components specific to Pinball game management and status will be added here in subsequent development phases.