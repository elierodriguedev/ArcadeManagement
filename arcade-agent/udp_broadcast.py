import socket
import json
import time
import logging
import psutil # Needed for get_ping_payload
import os # Import the os module

# --- Configuration (These might need to be passed in or read from a config) ---
# For now, hardcoding based on original agent.py
UDP_BROADCAST_PORT = 5152
MACHINE_TYPE = "arcade"
BIGBOX_EXE_PATH = os.path.join(os.path.expanduser("~"), "LaunchBox", "BigBox.exe") # Define BigBox path


# --- Logging Setup (Assuming basic logging is configured in the main agent.py) ---
# Need to ensure logging is configured before these functions are called
def log(msg, level=logging.INFO):
    logging.log(level, msg)

# --- Helper for Ping Data ---
def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    try:
        for proc in psutil.process_iter(['name']):
            # Use proc.name() in newer psutil versions if proc.info['name'] fails
            if process_name.lower() in proc.info['name'].lower():
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass # Ignore processes that have died or we can't access
    except Exception as e:
        log(f"Error checking process {process_name}: {e}", level=logging.ERROR)
    return False

def get_ping_payload(agent_version):
    """Gathers all data required for the ping response."""
    disk_total_gb, disk_free_gb = "N/A", "N/A"
    cpu_percent, ram_percent = "N/A", "N/A"
    hostname = socket.gethostname()

    try:
        usage = psutil.disk_usage('C:\\')
        disk_total_gb = usage.total // (2**30)
        disk_free_gb = usage.free // (2**30)
    except Exception as e:
        log(f"Error getting disk usage for C:: {e}", level=logging.ERROR)

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent
    except Exception as e:
        log(f"Error getting CPU/RAM usage: {e}", level=logging.ERROR)

    bigbox_running = is_process_running("BigBox.exe")

    return {
        "status": "online", # Agents sending UDP are considered online
        "type": MACHINE_TYPE,
        "hostname": hostname,
        "version": agent_version, # Use the passed version
        "disk_total_gb": disk_total_gb,
        "disk_free_gb": disk_free_gb,
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "bigbox_running": bigbox_running
    }

def get_broadcast_address():
    """Attempt to find the primary non-loopback IPv4 broadcast address."""
    try:
        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == socket.AF_INET and not snic.address.startswith("127."):
                    if snic.broadcast:
                        log(f"Found broadcast address {snic.broadcast} for interface {interface}")
                        return snic.broadcast
        log("Could not determine specific subnet broadcast address, using <broadcast>", level=logging.WARNING)
        return '<broadcast>' # Fallback for systems where psutil doesn't provide it easily or none found
    except Exception as e:
        log(f"Error getting broadcast address: {e}. Falling back to <broadcast>", level=logging.ERROR)
        return '<broadcast>'

# --- UDP Broadcast Loop ---
def udp_broadcast_loop(agent_version):
    """Periodically broadcasts agent status via UDP."""
    broadcast_address = get_broadcast_address()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    log(f"Starting UDP broadcast to {broadcast_address}:{UDP_BROADCAST_PORT} every 2 seconds")

    while True:
        try:
            payload = get_ping_payload(agent_version) # Pass agent_version
            message = json.dumps(payload).encode('utf-8')
            udp_socket.sendto(message, (broadcast_address, UDP_BROADCAST_PORT))
            # Reduce log spam: log(f"UDP Ping sent to {broadcast_address}:{UDP_BROADCAST_PORT}", level=logging.DEBUG)
        except Exception as e:
            log(f"Error in UDP broadcast loop: {e}", level=logging.ERROR)
            time.sleep(5) # Longer sleep on error
        time.sleep(2) # Wait 2 seconds before next broadcast
