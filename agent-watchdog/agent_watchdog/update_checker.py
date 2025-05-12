import subprocess
import requests
import logging
import os
import time
from packaging import version # Using packaging for robust version comparison
from plyer import notification
from agent_watchdog import process_manager
from agent_watchdog.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_notification(title, message):
    """Displays a Windows notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Agent Watchdog',
            timeout=10 # Notification stays for 10 seconds
        )
    except Exception as e:
        logging.error(f"Error displaying notification: {e}")


def get_installed_agent_version():
    """
    Gets the current installed agent version by executing agent.exe --version.
    """
    try:
        # Assuming agent.exe is in the current directory or PATH
        result = subprocess.run(['agent.exe', '--version'], capture_output=True, text=True, check=True)
        # The version is expected to be in the standard output
        version_string = result.stdout.strip()
        logging.info(f"Installed agent version: {version_string}")
        return version_string
    except FileNotFoundError:
        logging.error("agent.exe not found. Make sure it's in the PATH or current directory.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing agent.exe --version: {e}")
        logging.error(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while getting installed version: {e}")
        return None

def get_latest_online_version(url):
    """
    Queries the configured URL to get the latest online version.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        latest_version = response.text.strip()
        logging.info(f"Latest online version: {latest_version}")
        return latest_version
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching latest online version from {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching online version: {e}")
        return None

def trigger_update_sequence(current_version, latest_version):
    """
    Triggers the agent update sequence.
    """
    logging.info(f"Update needed: Installed version {current_version} is older than latest online version {latest_version}.")
    show_notification("Agent Update Available", f"New version {latest_version} available. Starting update...")

    config = Config()
    download_url = config.get_agent_download_url()
    agent_filename = "agent.exe"
    new_agent_filename = "agent_new.exe"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    new_agent_path = os.path.join(current_dir, new_agent_filename)
    old_agent_path = os.path.join(current_dir, agent_filename)

    # 1. Download the new agent version
    logging.info(f"Downloading new agent from {download_url}...")
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(new_agent_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info("Download complete.")
        show_notification("Agent Update", "Download complete. Agent will restart.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading new agent: {e}")
        show_notification("Agent Update Failed", "Failed to download new agent.")
        return
    except IOError as e:
        logging.error(f"Error saving new agent executable: {e}")
        show_notification("Agent Update Failed", "Failed to save new agent executable.")
        return

    # 2. Kill the running agent.exe process
    logging.info("Attempting to kill running agent.exe process...")
    if process_manager.kill_agent():
        logging.info("Kill signal sent. Waiting for agent to terminate...")
        # 3. Wait for the agent.exe process to terminate
        wait_time = 0
        while process_manager.is_agent_running() and wait_time < 30: # Wait up to 30 seconds
            time.sleep(1)
            wait_time += 1
        
        if process_manager.is_agent_running():
            logging.error("Agent process did not terminate within the expected time.")
            show_notification("Agent Update Failed", "Agent process did not terminate.")
            return
        else:
            logging.info("Agent process terminated.")
    else:
        logging.warning("Agent process was not running or could not be killed.")
        # Continue with the update assuming the file is not in use

    # 4. Delete the old agent.exe file
    logging.info(f"Deleting old agent executable: {old_agent_path}")
    try:
        if os.path.exists(old_agent_path):
            os.remove(old_agent_path)
            logging.info("Old agent executable deleted.")
        else:
            logging.warning("Old agent executable not found.")
    except OSError as e:
        logging.error(f"Error deleting old agent executable: {e}")
        show_notification("Agent Update Failed", "Failed to delete old agent executable.")
        return

    # 5. Rename agent_new.exe to agent.exe
    logging.info(f"Renaming {new_agent_path} to {old_agent_path}")
    try:
        os.rename(new_agent_path, old_agent_path)
        logging.info("New agent executable renamed.")
    except OSError as e:
        logging.error(f"Error renaming new agent executable: {e}")
        show_notification("Agent Update Failed", "Failed to rename new agent executable.")
        return

    # 6. Start the newly updated agent.exe
    logging.info(f"Starting new agent executable: {old_agent_path}")
    started_process = process_manager.start_agent(old_agent_path)
    if started_process:
        logging.info(f"New agent started with PID: {started_process.pid}")
        show_notification("Agent Update Complete", "Agent updated and restarted successfully.")
    else:
        logging.error("Failed to start the new agent executable.")
        show_notification("Agent Update Failed", "Failed to start the new agent executable.")


def check_for_updates(update_url="https://arcade.elierodrigue.cloud/api/agent/latest_version"):
    """
    Checks for agent updates and triggers the update sequence if a newer version is available online.
    """
    logging.info("Checking for agent updates...")
    installed_version_str = get_installed_agent_version()
    if not installed_version_str:
        logging.error("Could not retrieve installed agent version. Cannot check for updates.")
        return

    latest_version_str = get_latest_online_version(update_url)
    if not latest_version_str:
        logging.error("Could not retrieve latest online version. Cannot check for updates.")
        return

    try:
        installed_version = version.parse(installed_version_str)
        latest_version = version.parse(latest_version_str)

        if latest_version > installed_version:
            trigger_update_sequence(installed_version_str, latest_version_str)
        else:
            logging.info("Agent is up to date.")
    except version.InvalidVersion as e:
        logging.error(f"Error parsing version string: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during version comparison: {e}")

if __name__ == "__main__":
    # Example usage when run directly
    check_for_updates()