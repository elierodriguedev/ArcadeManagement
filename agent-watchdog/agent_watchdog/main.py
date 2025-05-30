import sys
import os
import time
import pathlib
import requests
import logging
import argparse # Import argparse
from PyQt5.QtCore import QThread, QTimer, QDateTime, QObject, pyqtSignal
from agent_watchdog.config import Config
from agent_watchdog.process_manager import is_agent_running, start_agent, kill_agent
from agent_watchdog.update_checker import get_installed_agent_version, get_latest_online_version, trigger_update_sequence
from agent_watchdog.watchdog_ui import run_ui, WatchdogTrayIcon, WatchdogSignals

# Define the watchdog version
WATCHDOG_VERSION = "1.0.7" # Incremented version for build

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add a handler to display ERROR level messages on the console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

class WatchdogWorker(QThread):
    """
    Worker thread to handle background tasks like agent checking and updates.
    """
    def __init__(self, signals: WatchdogSignals, config: Config):
        super().__init__()
        self.signals = signals
        self.config = config
        self._is_running = True

    def run(self):
        """
        Main loop for the worker thread.
        """
        logging.info("WatchdogWorker thread started.")
        while self._is_running:
            try:
                # Check if agent is running
                agent_running = is_agent_running()
                logging.info(f"Checking agent status. Agent running: {agent_running}")
                self.signals.agent_status_updated.emit(agent_running)

                # Get installed agent version
                current_version = get_installed_agent_version()
                logging.info(f"Installed agent version: {current_version}")
                if current_version:
                    self.signals.current_version_updated.emit(current_version)
                else:
                    self.signals.current_version_updated.emit("Unknown")

                # Check for updates
                latest_version = get_latest_online_version(self.config.get_agent_version_check_url())
                logging.info(f"Latest online agent version: {latest_version}")
                if latest_version:
                    self.signals.latest_version_updated.emit(latest_version)
                    # Trigger update if needed (logic moved from update_checker)
                    if current_version and latest_version:
                         try:
                            from packaging import version
                            installed_ver = version.parse(current_version)
                            latest_ver = version.parse(latest_version)
                            if latest_ver > installed_ver:
                                logging.info("Update needed. Triggering update sequence.")
                                # This will block the worker thread during download/install
                                # Consider moving download/install to another thread if it becomes an issue
                                trigger_update_sequence(current_version, latest_version)
                         except version.InvalidVersion as e:
                            logging.error(f"Error parsing version string during update check: {e}")
                            self.signals.error_occurred.emit(f"Version parsing error: {e}")
                         except Exception as e:
                            logging.error(f"An unexpected error occurred during version comparison: {e}")
                            self.signals.error_occurred.emit(f"Update check error: {e}")

                else:
                    self.signals.latest_version_updated.emit("Unknown")

                # Update last check timestamp
                self.signals.last_check_updated.emit(QDateTime.currentDateTime())

            except Exception as e:
                logging.error(f"An error occurred in the watchdog worker: {e}")
                self.signals.error_occurred.emit(f"Watchdog error: {e}")

            time.sleep(60) # Check every 60 seconds

    def stop(self):
        """
        Stops the worker thread.
        """
        self._is_running = False
        self.wait()


def main():
    """
    Main entry point for the Agent Watchdog application.
    """
    logging.info("Agent Watchdog main function started.")
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Arcade Agent Watchdog")
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {WATCHDOG_VERSION}',
        help='Show the watchdog version and exit'
    )
    args = parser.parse_args() # argparse handles printing version and exiting if --version is present

    print("Agent Watchdog started.")
    config = Config()
    logging.info(f"Using Agent Download URL: {config.get_agent_download_url()}")
    logging.info(f"Using Agent Version Check URL: {config.get_agent_version_check_url()}")
    
    try:
        app = run_ui() # run_ui now returns the QApplication instance
        logging.info("Watchdog UI started.")
        tray_icon = WatchdogTrayIcon(app) # Pass the app instance
        tray_icon.show()
    
        # Create and start the worker thread
        worker = WatchdogWorker(tray_icon.signals, config)
        worker.start()
        logging.info("WatchdogWorker thread created and started.")
    
        # Ensure the worker thread is stopped when the application quits
        app.aboutToQuit.connect(worker.stop)
        logging.info("Connecting aboutToQuit signal to worker stop.")
    
        # Run the GUI event loop
        logging.info("Running GUI event loop.")
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"An error occurred during UI initialization or event loop: {e}")
        sys.exit(1) # Exit with a non-zero code to indicate an error


if __name__ == "__main__":
    # Ensure the script is running in the correct directory if needed
    # os.chdir(os.path.dirname(sys.argv[0]))
    main()