# Plan: Hide Agent Window on Windows

**Goal:** Hide the console window when the agent executable is run on Windows.

**Plan:**

1.  **Modify `agent.spec`:** Change the `console=True` option to `windowed=True` in the `EXE` section of the `arcade-agent/agent.spec` file. This will configure PyInstaller to build a windowed application without a console window.

2.  **Update Agent Version:**
    *   Increment the version number in the `arcade-agent/agent.py` file.
    *   Add a new entry to the `arcade-agent/CHANGELOG.md` file detailing the change (hiding the console window on Windows).

3.  **Build Windows Agent:** Execute the `arcade-agent/build_agent_windows.sh` script to rebuild the agent executable with the updated configuration.

4.  **Confirmation:** Ask the user to review and approve this plan. (Already completed)

5.  **Document Plan (Optional):** Write this plan to a markdown file for documentation. (Current step)

6.  **Implementation:** Switch to Code mode to perform the necessary file modifications and execute the build script.