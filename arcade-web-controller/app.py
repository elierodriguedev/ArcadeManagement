from flask import Flask, jsonify, request, render_template, send_from_directory
import requests
import json
import os
import threading
import time
import socket
from datetime import datetime
from packaging import version as packaging_version # Import for version comparison
import logging # Import logging

app = Flask(__name__, static_folder='static')

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
def log(msg, level=logging.INFO):
    logging.log(level, msg)

log("--- Starting Arcade Web Controller ---")

# --- Global Variables for UDP Discovery ---
discovered_machines = {} # Dictionary to store real-time data {hostname: {payload: {...}, last_seen: timestamp}}
machine_lock = threading.Lock() # Lock for accessing discovered_machines
UDP_LISTEN_PORT = 5152
OFFLINE_THRESHOLD = 10 # Seconds before marking a machine as offline

# --- Configuration ---
# Path to the machines.json file (relative to the app.py)
MACHINES_FILE = 'machines.json'

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/api/generate-image-gpt", methods=["GET"])
def generate_image_gpt():
    prompt = request.args.get("prompt")
    size = request.args.get("size", "1024x1024")

    # Validate size parameter
    allowed_sizes = ["256x256", "512x512", "1024x1024"]
    if size not in allowed_sizes:
        return jsonify({"error": f"Invalid size parameter. Allowed values are {allowed_sizes}"}), 400

    if not prompt:
        return jsonify({"error": "Missing prompt parameter"}), 400

    if not OPENAI_API_KEY:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size
    }

    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        image_url = result["data"][0]["url"]
        return jsonify({"url": image_url})
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"OpenAI API HTTP error: {http_err}", "details": response.text}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def load_machines():
    """Loads machine configurations from machines.json."""
    if not os.path.exists(MACHINES_FILE):
        return []
    try:
        with open(MACHINES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding {MACHINES_FILE}. Returning empty list.")
        return []
    except Exception as e:
        print(f"Error loading {MACHINES_FILE}: {e}")
        return []

def get_agent_url(agent_id):
    """Finds the agent URL based on the agent ID."""
    machines = load_machines()
    for machine in machines:
        # Assuming agent_id is the 'name' for now, could be adapted
        if machine.get('name') == agent_id:
            # Assuming agent runs on port 5151 as per agent.py
            return f"http://{machine.get('host')}:5151"
    return None

# --- UDP Listener ---
def udp_listener_thread():
    global discovered_machines, machine_lock
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        udp_socket.bind(("0.0.0.0", UDP_LISTEN_PORT))
        print(f"UDP Listener started on port {UDP_LISTEN_PORT}")
    except Exception as e:
        print(f"FATAL: Could not bind UDP listener to port {UDP_LISTEN_PORT}: {e}")
        # In a web context, we might log this or have a health check endpoint
        return # Exit thread if bind fails

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024) # buffer size is 1024 bytes
            print(f"Received UDP packet from {addr[0]}") # Log packet reception
            payload = json.loads(data.decode('utf-8'))
            print(f"Parsed UDP payload from {addr[0]}: {payload}") # Log parsed payload
            hostname = payload.get("hostname")

            if hostname:
                # print(f"UDP Received from {hostname} ({addr[0]})") # Verbose Debug
                with machine_lock:
                    discovered_machines[hostname] = {
                        "payload": payload,
                        "last_seen": time.time()
                    }
                print(f"Updated discovered_machines for {hostname}") # Log update

        except json.JSONDecodeError:
            print(f"Received invalid JSON UDP packet from {addr[0]}")
        except OSError as e:
             # Handle specific errors like socket closed during shutdown
             print(f"UDP socket error: {e}")
             break # Exit loop if socket is closed
        except Exception as e:
            print(f"Error in UDP listener: {type(e).__name__}: {e}")
            time.sleep(1) # Avoid busy-looping on errors

# --- Web UI Route ---
@app.route("/")
def index():
    """Serves the main index.html for the web UI."""
    # This will serve the index.html from the 'static' folder
    return send_from_directory(app.static_folder, 'index.html')

# --- API Routes ---

@app.route("/api/machines", methods=["GET"])
def list_machines():
    """Lists configured machines and their ping status."""
    machines = load_machines()
    results = []
    for machine in machines:
        agent_url = get_agent_url(machine.get('name'))
        status = "unknown"
        version = "N/A"
        hostname = "N/A"
        machine_type = "N/A"
        disk_free_gb = "N/A"
        cpu_percent = "N/A"
        ram_percent = "N/A"
        bigbox_running = "N/A"

        if agent_url:
            try:
                response = requests.get(f"{agent_url}/api/ping", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "online")
                    version = data.get("version", "N/A")
                    hostname = data.get("hostname", "N/A")
                    machine_type = data.get("type", "N/A")
                    disk_free_gb = data.get("disk_free_gb", "N/A")
                    cpu_percent = data.get("cpu_percent", "N/A")
                    ram_percent = data.get("ram_percent", "N/A")
                    bigbox_running = data.get("bigbox_running", "N/A")
                else:
                    status = f"error: {response.status_code}"
            except requests.exceptions.RequestException as e:
                status = f"offline: {e}"
            except Exception as e:
                 status = f"error: {e}"
        else:
            status = "invalid config"

        results.append({
            "id": machine.get('name'), # Use name as ID for now
            "name": machine.get('name'),
            "host": machine.get('host'),
            "type": machine.get('type'),
            "status": status,
            "version": version,
            "hostname": hostname,
            "disk_free_gb": disk_free_gb,
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "bigbox_running": bigbox_running
        })
    return jsonify(results)

# --- New API Route for Discovered Machines ---
@app.route("/api/discovered_machines", methods=["GET"])
def list_discovered_machines():
    """Lists discovered machines based on UDP broadcasts."""
    global discovered_machines, machine_lock
    current_time = time.time()
    results = []

    with machine_lock:
        # Iterate over discovered machines
        for hostname, data in list(discovered_machines.items()): # Use list() to iterate over a copy
            last_seen_time = data.get("last_seen", 0)
            time_since_seen = current_time - last_seen_time
            payload = data.get("payload", {})

            if time_since_seen <= OFFLINE_THRESHOLD:
                status = "Online"
                # Use payload data if online
                version = payload.get("version", "N/A")
                machine_type = payload.get("type", "N/A")
                disk_total = payload.get("disk_total_gb", "N/A")
                disk_free = payload.get("disk_free_gb", "N/A")
                cpu = payload.get("cpu_percent", "N/A")
                ram = payload.get("ram_percent", "N/A")
                bigbox_running = payload.get("bigbox_running", None)
                bigbox_display = "Running" if bigbox_running else ("Stopped" if bigbox_running is False else "N/A")
            else:
                status = "Offline"
                # Use placeholder data if offline
                version = "—"
                machine_type = payload.get("type", "N/A") # Keep last known type
                disk_total, disk_free, cpu, ram, bigbox_display = "—", "—", "—", "—", "—"

            results.append({
                "hostname": hostname,
                "type": machine_type,
                "status": status,
                "last_seen": datetime.fromtimestamp(last_seen_time).strftime("%H:%M:%S") if last_seen_time > 0 else "Never",
                "version": version,
                "disk_total_gb": disk_total,
                "disk_free_gb": disk_free,
                "cpu_percent": cpu,
                "ram_percent": ram,
                "bigbox_running": bigbox_display
            })
            # Optional: Clean up old offline entries from discovered_machines if needed
            # if time_since_seen > OFFLINE_THRESHOLD * 5: # Example: remove after 5x threshold
            #     del discovered_machines[hostname]


    return jsonify(results)

# --- Agent Version and Download Endpoints ---

def get_latest_agent_version():
    """Determines the latest agent version based on directory names using semantic versioning."""
    agent_dir = os.path.join(os.path.dirname(__file__), 'Agent')
    if not os.path.exists(agent_dir):
        log(f"Agent directory not found at: {agent_dir}", level=logging.WARNING)
        return None

    try:
        # List all entries in the Agent directory
        entries = os.listdir(agent_dir)
        # Filter for directories that look like version numbers
        version_dirs = [entry for entry in entries if os.path.isdir(os.path.join(agent_dir, entry)) and packaging_version.parse(entry)]

        if not version_dirs:
            log(f"No version directories found in {agent_dir}", level=logging.WARNING)
            return None

        # Sort directories using packaging.version for correct semantic version comparison
        version_dirs.sort(key=packaging_version.parse, reverse=True)

        # The first element after sorting in reverse should be the latest version
        latest_version = version_dirs[0]
        log(f"Determined latest agent version: {latest_version}")
        return latest_version

    except packaging_version.InvalidVersion as e:
        log(f"Error parsing version directory name: {e}", level=logging.ERROR)
        return None
    except Exception as e:
        log(f"Error determining latest agent version: {e}", level=logging.ERROR)
        return None

def get_latest_watchdog_version():
    """Determines the latest watchdog version based on directory names using semantic versioning."""
    watchdog_dir = os.path.join(os.path.dirname(__file__), 'Watchdog')
    if not os.path.exists(watchdog_dir):
        log(f"Watchdog directory not found at: {watchdog_dir}", level=logging.WARNING)
        return None

    try:
        # List all entries in the Watchdog directory
        entries = os.listdir(watchdog_dir)
        # Filter for directories that look like version numbers
        version_dirs = [entry for entry in entries if os.path.isdir(os.path.join(watchdog_dir, entry)) and packaging_version.parse(entry)]

        if not version_dirs:
            log(f"No version directories found in {watchdog_dir}", level=logging.WARNING)
            return None

        # Sort directories using packaging.version for correct semantic version comparison
        version_dirs.sort(key=packaging_version.parse, reverse=True)

        # The first element after sorting in reverse should be the latest version
        latest_version = version_dirs[0]
        log(f"Determined latest watchdog version: {latest_version}")
        return latest_version

    except packaging_version.InvalidVersion as e:
        log(f"Error parsing version directory name: {e}", level=logging.ERROR)
        return None
    except Exception as e:
        log(f"Error determining latest watchdog version: {e}", level=logging.ERROR)
        return None


@app.route("/api/agent/latest_version", methods=["GET"])
def get_latest_agent_version_route():
    """Returns the latest agent version."""
    latest_version = get_latest_agent_version()
    if latest_version:
        return jsonify({"latest_version": latest_version})
    else:
        return jsonify({"error": "Could not determine latest agent version"}), 404

@app.route("/api/agent/download/latest", methods=["GET"])
def download_latest_agent():
    """Downloads the latest agent executable."""
    latest_version = get_latest_agent_version()
    if not latest_version:
        return jsonify({"error": "Could not determine latest agent version"}), 404

    agent_file_path = os.path.join(os.path.dirname(__file__), 'Agent', latest_version, 'agent.exe')

    if not os.path.exists(agent_file_path):
        log(f"Agent executable not found for version {latest_version} at {agent_file_path}", level=logging.ERROR)
        return jsonify({"error": f"Agent executable not found for version {latest_version}"}), 404

    try:
        # Serve the file for download
        return send_from_directory(
            directory=os.path.join(os.path.dirname(__file__), 'Agent', latest_version),
            path='agent.exe',
            as_attachment=True,
            mimetype='application/octet-stream' # Generic binary file type
        )
    except Exception as e:
        log(f"Error serving agent executable: {e}", level=logging.ERROR)
        return jsonify({"error": "Could not serve agent executable"}), 500

@app.route("/api/watchdog/latest_version", methods=["GET"])
def get_latest_watchdog_version_route():
    """Returns the latest watchdog version."""
    latest_version = get_latest_watchdog_version()
    if latest_version:
        return jsonify({"latest_version": latest_version})
    else:
        return jsonify({"error": "Could not determine latest watchdog version"}), 404

@app.route("/api/watchdog/download/latest", methods=["GET"])
def download_latest_watchdog():
    """Downloads the latest watchdog executable."""
    latest_version = get_latest_watchdog_version()
    if not latest_version:
        return jsonify({"error": "Could not determine latest watchdog version"}), 404

    watchdog_file_path = os.path.join(os.path.dirname(__file__), 'Watchdog', latest_version, 'agent-watchdog.exe')

    if not os.path.exists(watchdog_file_path):
        log(f"Watchdog executable not found for version {latest_version} at {watchdog_file_path}", level=logging.ERROR)
        return jsonify({"error": f"Watchdog executable not found for version {latest_version}"}), 404

    try:
        # Serve the file for download
        return send_from_directory(
            directory=os.path.join(os.path.dirname(__file__), 'Watchdog', latest_version),
            path='agent_watchdog.exe',
            as_attachment=True,
            mimetype='application/octet-stream' # Generic binary file type
        )
    except Exception as e:
        log(f"Error serving watchdog executable: {e}", level=logging.ERROR)
        return jsonify({"error": "Could not serve watchdog executable"}), 500


# --- Placeholder for other API endpoints (e.g., control layout, games, etc.) ---
# These will need to be implemented to forward requests to the agents.

# Example: Forwarding control layout GET request
@app.route("/api/machines/<agent_id>/control-layout", methods=["GET"])
def get_agent_layout(agent_id):
    agent_url = get_agent_url(agent_id)
    if not agent_url:
        return jsonify(error="Agent not found or invalid config"), 404
    try:
        response = requests.get(f"{agent_url}/api/control-layout", timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify(error=f"Error fetching layout from agent: {e}"), 500

# Example: Forwarding control layout PUT request
@app.route("/api/machines/<agent_id>/control-layout", methods=["PUT"])
def update_agent_layout(agent_id):
    agent_url = get_agent_url(agent_id)
    if not agent_url:
        return jsonify(error="Agent not found or invalid config"), 404
    data = request.get_json()
    if not data:
        return jsonify(error="Invalid JSON data"), 400
    try:
        response = requests.put(f"{agent_url}/api/control-layout", json=data, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify(error=f"Error updating layout on agent: {e}"), 500

# Add more endpoints here to forward other agent API calls as needed...
# e.g., /api/machines/<agent_id>/launchbox/games, /api/machines/<agent_id>/launchbox/playlists, etc.

# Add more endpoints here to forward other agent API calls as needed...
# e.g., /api/machines/<agent_id>/launchbox/games, /api/machines/<agent_id>/launchbox/playlists, etc.

# --- Machine UI Proxy Route ---
@app.route("/machinename/<machine_name>/", defaults={'subpath': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/machinename/<machine_name>/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy_machine_ui(machine_name, subpath):
    """Proxies requests to the specified machine's web UI."""
    machines = load_machines()
    machine_host = None
    # First, check configured machines in machines.json
    for machine in machines:
        if machine.get('name') == machine_name:
            machine_host = machine.get('host')
            break

    # If not found in machines.json, check discovered machines
    if not machine_host:
        with machine_lock:
            print(f"Discovered machines keys: {discovered_machines.keys()}") # Log discovered machine keys
            if machine_name in discovered_machines:
                 print(f"Machine '{machine_name}' found in discovered machines.") # Log if machine found in discovered
            else:
                 print(f"Machine '{machine_name}' NOT found in discovered machines.") # Log if machine not found in discovered

            discovered_machine_data = discovered_machines.get(machine_name)
            if discovered_machine_data and (time.time() - discovered_machine_data.get("last_seen", 0) <= OFFLINE_THRESHOLD):
                machine_host = discovered_machine_data.get("payload", {}).get("hostname") # Assuming 'hostname' is in the UDP payload

    if not machine_host:
        return jsonify(error=f"Machine '{machine_name}' not found in configuration or discovered machines."), 404

    agent_url = f"http://{machine_host}:5151/{subpath}"
    print(f"Proxying request to: {agent_url}") # Log the target URL

    try:
        # Forward the request to the agent
        resp = requests.request(
            method=request.method,
            url=agent_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'}, # Exclude Host header
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)

        # Prepare the response to send back to the client
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]

        return resp.content, resp.status_code, headers

    except requests.exceptions.RequestException as e:
        return jsonify(error=f"Error communicating with agent '{machine_name}': {e}"), 500
    except Exception as e:
        return jsonify(error=f"An unexpected error occurred: {e}"), 500


if __name__ == "__main__":
    # Start UDP listener thread
    listener_thread = threading.Thread(target=udp_listener_thread, daemon=True)
    listener_thread.start()

    # Create a dummy machines.json if it doesn't exist (optional for this task, but good practice)
    if not os.path.exists(MACHINES_FILE):
        print(f"Creating dummy {MACHINES_FILE}")
        dummy_machines = [
            {"name": "ExampleArcade1", "host": "localhost", "type": "arcade"},
            # Add more dummy machines here if needed
        ]
        try:
            with open(MACHINES_FILE, 'w') as f:
                json.dump(dummy_machines, f, indent=2)
        except Exception as e:
            print(f"Error creating dummy {MACHINES_FILE}: {e}")

    # Create a dummy static/index.html for testing
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    dummy_index_path = os.path.join(static_dir, 'index.html')
    if not os.path.exists(dummy_index_path):
        print(f"Creating dummy {dummy_index_path}")
        dummy_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Arcade Web Controller</title>
        </head>
        <body>
            <h1>Arcade Web Controller</h1>
            <p>Web UI goes here. API endpoints are available.</p>
            <p>Check /api/machines for agent status.</p>
        </body>
        </html>
        """
        try:
            with open(dummy_index_path, 'w') as f:
                f.write(dummy_html)
        except Exception as e:
            print(f"Error creating dummy {dummy_index_path}: {e}")


    print("Starting Flask web controller on 0.0.0.0:5000")
    # Running on port 5000 to avoid conflict with agent on 5151
    app.run(host="0.0.0.0", port=5000, debug=True) # Use debug=False for production
