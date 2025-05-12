import subprocess
import sys
import os

def is_agent_running():
    """
    Checks if the agent.exe process is currently running.
    Returns True if running, False otherwise.
    """
    # This implementation is basic and might need platform-specific adjustments
    # For Windows, tasklist can be used. For Linux, 'ps aux' or 'pgrep' might be more suitable.
    # Using a simple approach that might work on some systems or require refinement.
    try:
        # Attempt to list processes and check for 'agent.exe'
        # This command might vary significantly based on the OS.
        # A more robust solution would use a library like psutil.
        if sys.platform.startswith('win'):
            # Windows command to list processes
            result = subprocess.run(['tasklist'], capture_output=True, text=True, check=True)
            return 'agent.exe' in result.stdout
        else:
            # Basic check for non-Windows systems (might not be accurate)
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, check=True)
            return 'agent.exe' in result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error checking process list: {e}")
        return False
    except FileNotFoundError:
        print("Process listing command not found. Cannot check if agent is running.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking agent process: {e}")
        return False

def start_agent(agent_path):
    """
    Starts the agent.exe executable.
    Returns the process object if successful, None otherwise.
    """
    try:
        # Use subprocess.Popen to start the process without waiting
        # This assumes agent_path is the full path to the executable
        process = subprocess.Popen([agent_path])
        print(f"Attempted to start agent from: {agent_path}")
        return process
    except FileNotFoundError:
        print(f"Error: Agent executable not found at {agent_path}")
        return None
    except Exception as e:
        print(f"An error occurred while trying to start the agent: {e}")
        return None

def kill_agent():
    """
    Kills the running agent.exe process.
    Returns True if the process was found and a kill signal was sent, False otherwise.
    Note: This does not guarantee the process is immediately terminated.
    """
    try:
        if sys.platform.startswith('win'):
            # Windows command to kill process by image name
            # The '/F' switch forces termination, '/IM' specifies the image name
            result = subprocess.run(['taskkill', '/F', '/IM', 'agent.exe'], capture_output=True, text=True)
            if result.returncode == 0:
                print("agent.exe process termination signal sent.")
                return True
            elif result.returncode == 128: # Taskkill return code for process not found
                print("agent.exe process not found.")
                return False
            else:
                print(f"Error terminating agent.exe process: {result.stderr}")
                return False
        else:
            # Basic kill command for non-Windows systems (might need adjustment)
            # This attempts to kill all processes named 'agent.exe'
            result = subprocess.run(['pkill', 'agent.exe'], capture_output=True, text=True)
            if result.returncode == 0:
                print("agent.exe process termination signal sent.")
                return True
            elif result.returncode == 1: # pkill return code for no processes matched
                print("agent.exe process not found.")
                return False
            else:
                print(f"Error terminating agent.exe process: {result.stderr}")
                return False
    except FileNotFoundError:
        print("Process killing command not found. Cannot terminate agent.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while trying to kill the agent: {e}")
        return False

if __name__ == '__main__':
    # Example usage (for testing the functions directly)
    # This part won't run when imported by main.py
    print(f"Is agent running? {is_agent_running()}")
    # To test start_agent, you would need a dummy agent.exe or similar
    # print("Starting dummy agent...")
    # dummy_agent_path = "./dummy_agent.exe" # Replace with a real path for testing
    # started_process = start_agent(dummy_agent_path)
    # if started_process:
    #     print(f"Dummy agent started with PID: {started_process.pid}")
    #     # You might want to add a small delay and then check if it's running
    #     # time.sleep(5)
    #     # print(f"Is dummy agent running after start? {is_agent_running()}")
    # else:
    #     print("Failed to start dummy agent.")