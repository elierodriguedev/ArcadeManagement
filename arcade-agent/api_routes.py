from flask import Flask, jsonify, request, Response, render_template, send_file, make_response, send_from_directory
import logging
import traceback
import urllib.parse
import os
import psutil
import time
import json
import uuid
import shutil
import socket # Added missing import
import subprocess # Added missing import
import re # Added missing import
import glob # Added missing import

# Import functions from other refactored files
from launchbox_utils import (
    get_all_games,
    get_playlists_data,
    find_orphaned_games,
    add_games_to_playlist,
    delete_playlist,
    get_game_details,
    apply_playlist_banner_image,
    get_playlist_banner_image_path
)
from filesystem_utils import (
    is_path_safe,
    is_temp_image_path_safe,
    list_directory_contents,
    get_file_content,
    get_launchbox_base_path
)
from image_utils import (
    generate_image_gemini,
    generate_image_openai,
    improve_prompt_gemini,
    capture_screenshot,
    TEMP_IMAGE_DIR # Need to access this config
)

# --- Configuration (These might need to be passed in or read from a config) ---
# For now, hardcoding based on original agent.py
LAYOUT_FILE = "control-layout.json"
LOG_FILE = "agent.log"
BIGBOX_EXE_PATH = os.path.join(os.path.expanduser("~"), "LaunchBox", "BigBox.exe") # Define BigBox path
DEFAULT_LAYOUT = {
    "players": 2,
    "joysticks": 2,
    "buttonsPerPlayer": 6,
    "spinners": 0,
    "trackballs": 0,
    "lightguns": 0,
    "steeringWheels": 0,
    "pedalSets": 0
}
# Need access to the temporary image path defined in filesystem_utils or main agent
# For now, recalculating based on assumed structure
script_dir = os.path.dirname(__file__) # Assuming this file is in the agent directory
temp_image_path = os.path.join(script_dir, TEMP_IMAGE_DIR)


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

def get_ping_payload():
    """Gathers all data required for the ping response."""
    log("Executing get_ping_payload", level=logging.DEBUG)
    disk_total_gb, disk_free_gb = "N/A", "N/A"
    cpu_percent, ram_percent = "N/A", "N/A"
    hostname = socket.gethostname() # Need to import socket

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

    # Need AGENT_VERSION from main agent.py or a config
    from agent import AGENT_VERSION
    MACHINE_TYPE = "arcade"

    return {
        "status": "online", # Agents sending UDP are considered online
        "type": MACHINE_TYPE,
        "hostname": hostname,
        "version": AGENT_VERSION,
        "disk_total_gb": disk_total_gb,
        "disk_free_gb": disk_free_gb,
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "bigbox_running": bigbox_running
    }


# --- API Routes ---

# Need a way to register these routes with the Flask app in agent.py
# This can be done by passing the app instance or using Blueprints.
# For now, defining the functions.

def ping_api():
    """HTTP endpoint to get current status."""
    log("/api/ping requested", level=logging.DEBUG)
    try:
        payload = get_ping_payload()
        log(f"/api/ping response payload: {payload}", level=logging.DEBUG)
        return jsonify(payload)
    except Exception as e:
        log(f"Error in ping_api: {e}", level=logging.ERROR)
        return jsonify(error="Internal Server Error", message=str(e)), 500

def get_layout_api():
    log("/api/control-layout [GET]")
    if os.path.exists(LAYOUT_FILE):
        try:
            with open(LAYOUT_FILE, "r") as f:
                layout = json.load(f)
                for key in DEFAULT_LAYOUT:
                    layout.setdefault(key, DEFAULT_LAYOUT[key])
                return jsonify(layout)
        except json.JSONDecodeError as e:
             log(f"Error decoding {LAYOUT_FILE}: {e}", level=logging.ERROR)
             return jsonify(DEFAULT_LAYOUT)
        except Exception as e:
             log(f"Error reading {LAYOUT_FILE}: {e}", level=logging.ERROR)
             return jsonify(error=f"Error reading layout file: {e}"), 500
    else:
        try:
            with open(LAYOUT_FILE, "w") as f:
                json.dump(DEFAULT_LAYOUT, f, indent=2)
            return jsonify(DEFAULT_LAYOUT)
        except Exception as e:
            log(f"Error creating default {LAYOUT_FILE}: {e}", level=logging.ERROR)
            return jsonify(error=f"Error creating default layout file: {e}"), 500

def update_layout_api():
    data = request.get_json()
    if not data:
        return jsonify(error="Invalid JSON data"), 400
    log(f"/api/control-layout [PUT] {data}")
    try:
        with open(LAYOUT_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "saved"})
    except Exception as e:
        log(f"Error writing {LAYOUT_FILE}: {e}", level=logging.ERROR)
        return jsonify(error=f"Error saving layout file: {e}"), 500

def start_bigbox_api():
    log("Received request to start BigBox")
    if not os.path.exists(BIGBOX_EXE_PATH):
        log(f"BigBox.exe not found at expected path: {BIGBOX_EXE_PATH}", level=logging.ERROR)
        return jsonify(error="BigBox.exe not found"), 404

    if is_process_running("BigBox.exe"):
        log("BigBox is already running.")
        return jsonify(status="BigBox already running"), 200

    try:
        log(f"Attempting to start BigBox: {BIGBOX_EXE_PATH}")
        subprocess.Popen(f'start "" "{BIGBOX_EXE_PATH}"', shell=True) # Need to import subprocess
        log("BigBox start command issued.")
        return jsonify(status="BigBox start initiated")
    except Exception as e:
        log(f"Failed to start BigBox: {e}", level=logging.ERROR)
        return jsonify(error=f"Failed to start BigBox: {e}"), 500

def stop_bigbox_api():
    log("Received request to stop BigBox")
    process_name_lower = "bigbox.exe"
    pids_terminated = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name_lower in proc.info['name'].lower():
                try:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate() # Send SIGTERM
                    pids_terminated.append(proc.info['pid'])
                    log(f"Sent terminate signal to BigBox process PID: {proc.info['pid']}")
                except psutil.NoSuchProcess:
                    log(f"Process {proc.info['pid']} already terminated.", level=logging.DEBUG)
                except psutil.AccessDenied:
                    log(f"Access denied trying to terminate BigBox PID: {proc.info['pid']}", level=logging.ERROR)
                except Exception as e:
                    log(f"Error terminating BigBox PID {proc.info['pid']}: {e}", level=logging.ERROR)

        if pids_terminated:
            return jsonify(status=f"Termination signal sent to BigBox process(es): {pids_terminated}")
        else:
            log("BigBox process not found running.")
            return jsonify(status="BigBox not running"), 200

    except Exception as e:
        log(f"Error iterating processes to stop BigBox: {e}", level=logging.ERROR)
        return jsonify(error=f"Error stopping BigBox: {e}"), 500

def get_games_api():
    log("/api/launchbox/games")
    games = get_all_games()
    log(f"Returned {len(games)} total games from all platform XML files.")
    return jsonify(games)

def get_playlists_api():
    log("/api/launchbox/playlists")
    playlists = get_playlists_data()
    return jsonify(playlists)

def get_orphaned_games_api():
    log("/api/launchbox/orphaned_games")
    orphaned = find_orphaned_games()
    return jsonify(orphaned)

def get_game_details_api():
    """Fetches full details for a list of provided game IDs."""
    data = request.get_json()
    game_ids_to_find = data.get("ids", [])
    log(f"Received request for game details for {len(game_ids_to_find)} IDs: {game_ids_to_find[:10]}...", level=logging.DEBUG)

    if not game_ids_to_find:
        return jsonify([]) # Return empty list if no IDs provided

    found_games = get_game_details(game_ids_to_find)

    log(f"Returning details for {len(found_games)} games.", level=logging.DEBUG)
    return jsonify(found_games)

def add_to_playlist_api():
    data = request.get_json()
    playlist_name = data.get("playlist")
    game_ids = data.get("games", [])
    log(f"/api/launchbox/playlists/add {playlist_name} <- {len(game_ids)} games")

    if not playlist_name or not game_ids:
        return jsonify(error="Invalid input"), 400

    result = add_games_to_playlist(playlist_name, game_ids)

    if result.get("status") == "playlist not found":
        return jsonify(result), 404
    elif result.get("status") == "error":
        return jsonify(result), 500
    else:
        return jsonify(result)

def delete_playlist_api(playlist_name):
    decoded_name = urllib.parse.unquote(playlist_name)
    log(f"Received request to DELETE playlist: {decoded_name}")

    result = delete_playlist(decoded_name)

    if result.get("status") == "playlist not found":
        return jsonify(result), 404
    elif result.get("status") == "error":
        return jsonify(result), 500
    else:
        return jsonify(result)

# --- Image Generation API ---
def generate_image_api():
    log("/api/generate-image requested", level=logging.DEBUG)
    prompt = request.args.get("prompt")

    if not prompt:
        log("Image generation request missing prompt URL parameter", level=logging.WARNING)
        return jsonify(error="Prompt URL parameter is required"), 400

    result = generate_image_gemini(prompt, temp_image_path) # Pass temp_image_path

    if result.get("status") == "success":
        return jsonify({"temp_image_url": result.get("temp_image_url")})
    else:
        return jsonify(error=result.get("message")), result.get("status_code", 500)


# --- OpenAI Image Generation API ---
def generate_image_gpt_api():
    log("/api/generate-image-gpt requested", level=logging.DEBUG)
    prompt = request.args.get("prompt")
    size = request.args.get("size", "1024x1024") # Default size to 1024x1024

    if not prompt:
        log("OpenAI image generation request missing prompt URL parameter", level=logging.WARNING)
        return jsonify({"error": "Prompt parameter is required"}), 400

    result = generate_image_openai(prompt, size, temp_image_path) # Pass temp_image_path

    if result.get("status") == "success":
        return jsonify({"temp_image_url": result.get("temp_image_url")})
    else:
        return jsonify(error=result.get("message")), result.get("status_code", 500)


# --- Prompt Improvement API ---
def improve_prompt_api():
    log("/api/improve-prompt requested", level=logging.DEBUG)
    prompt = request.args.get("prompt")

    if not prompt:
        log("Prompt improvement request missing 'prompt' in request body", level=logging.WARNING)
        return jsonify(error="'prompt' field in request body is required"), 400

    result = improve_prompt_gemini(prompt)

    if result.get("status") == "success":
        return jsonify(improved_prompt=result.get("improved_prompt"))
    else:
        return jsonify(error=result.get("message")), result.get("status_code", 500)


# --- Apply Playlist Banner Image ---
def apply_playlist_banner_api():
    data = request.get_json()
    playlist_name = data.get("playlist_name")
    temp_image_url = data.get("temp_image_url")
    log(f"Received request to apply banner for playlist '{playlist_name}' from temporary URL: {temp_image_url}", level=logging.DEBUG)

    if not playlist_name or not temp_image_url:
        return jsonify(error="Missing playlist_name or temp_image_url"), 400

    # Extract filename from the temporary image URL
    temp_filename = os.path.basename(urllib.parse.urlparse(temp_image_url).path)
    temp_file_path = os.path.join(temp_image_path, temp_filename)

    # Validate the temporary file path using filesystem_utils
    validated_temp_path, temp_error = is_temp_image_path_safe(temp_file_path)
    if temp_error:
        log(f"Temporary image path validation failed for '{temp_image_url}': {temp_error}", level=logging.WARNING)
        return jsonify(error=f"Invalid temporary image path: {temp_error}"), 400 # Use 400 for bad request data

    # Get LaunchBox base path using filesystem_utils
    launchbox_base_path = get_launchbox_base_path()

    result = apply_playlist_banner_image(playlist_name, validated_temp_path, launchbox_base_path)

    if result.get("status") == "success":
        # Optionally, delete the temporary file after successful copy
        try:
            os.remove(validated_temp_path)
            log(f"Deleted temporary image file: {validated_temp_path}", level=logging.DEBUG)
        except OSError as e:
            log(f"Error deleting temporary image file {validated_temp_path}: {e}", level=logging.WARNING)
        except Exception as e:
            log(f"Unexpected error deleting temporary image file {validated_temp_path}: {e}", level=logging.WARNING)

        return jsonify(result)
    else:
        return jsonify(result), result.get("status_code", 500)


# --- Playlist Image Serving ---
def serve_playlist_banner_api(playlist_name):
    decoded_name = urllib.parse.unquote(playlist_name)
    log(f"Received request to serve banner for playlist: {decoded_name}", level=logging.DEBUG)

    # Get LaunchBox base path using filesystem_utils
    launchbox_base_path = get_launchbox_base_path()

    banner_image_path = get_playlist_banner_image_path(decoded_name, launchbox_base_path)

    if not banner_image_path:
        return "", 404 # Not Found if the file doesn't exist

    # Validate the path to ensure it's within the allowed directory using filesystem_utils
    validated_path, error = is_path_safe(banner_image_path)

    if error:
        log(f"Path validation failed for playlist banner '{decoded_name}': {error}", level=logging.WARNING)
        return jsonify(error=error), 403 # Use 403 for access denied/validation issues

    try:
        log(f"Serving playlist banner image from: {validated_path}", level=logging.DEBUG)
        return send_file(validated_path, mimetype='image/png', as_attachment=False, download_name='screenshot.png') # Assuming PNG format
    except Exception as e:
        log(f"Error serving playlist banner image {validated_path}: {e}", level=logging.ERROR)
        return jsonify(error=f"Error serving image: {e}"), 500


# --- Filesystem API Routes ---

def get_launchbox_basepath_api():
    """Returns the configured LaunchBox base path."""
    log("/api/launchbox/basepath requested", level=logging.DEBUG)
    basepath = get_launchbox_base_path()
    return jsonify({"basepath": basepath})

def delete_cache_api():
    """Deletes all files and subfolders in LaunchBox\\Images\\Cache-BB folder."""
    log("Received request to delete LaunchBox BigBox image cache")
    basepath = get_launchbox_base_path()
    cache_path = os.path.join(basepath, "Images", "Cache-BB")

    if not os.path.exists(cache_path):
        log(f"Cache path does not exist: {cache_path}", level=logging.WARNING)
        return jsonify({"status": "Cache folder does not exist"}), 404

    try:
        # Delete all files and subfolders in cache_path
        for root, dirs, files in os.walk(cache_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                log(f"Deleted file: {file_path}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                shutil.rmtree(dir_path)
                log(f"Deleted directory: {dir_path}")
        return jsonify({"status": "Cache deleted successfully"})
    except Exception as e:
        log(f"Error deleting cache: {e}", level=logging.ERROR)
        return jsonify({"error": f"Failed to delete cache: {e}"}), 500

def list_directory_api():
    """Lists files and directories within a validated path."""
    requested_path = request.args.get('path')
    log(f"/api/filesystem/list requested for path: {requested_path}", level=logging.DEBUG)

    items, error = list_directory_contents(requested_path)

    if error:
        # Distinguish between not a directory and other errors
        if error == "Path is not a directory":
            return jsonify(error=error), 400
        else:
            return jsonify(error=error), 403 # Use 403 for access denied/validation issues

    return jsonify(items)


def get_file_content_api():
    """Gets the content of a validated file path."""
    requested_path = request.args.get('path')
    log(f"/api/filesystem/content requested for path: {requested_path}", level=logging.DEBUG)

    content, error = get_file_content(requested_path)

    if error:
        # Distinguish between not found, not a file, and other errors
        if error == "Path not found.":
             return jsonify(error=error), 404
        elif error == "Path is not a file":
             return jsonify(error=error), 400
        else:
             return jsonify(error=error), 403

    return jsonify(content=content)


def screenshot_api():
    """Capture and return the current screen as a PNG image."""
    result = capture_screenshot() # Assuming capture_screenshot is in image_utils

    if result.get("status") == "success":
        # The result should contain the BytesIO object
        buf = result.get("image_buffer")

# --- Reboot API ---
from reboot_handler import initiate_reboot # Import the reboot function

def reboot_agent_api():
    """HTTP endpoint to initiate agent reboot."""
    log("/api/reboot requested", level=logging.DEBUG)

    # Basic authorization check (replace with a more secure method in production)
    auth_header = request.headers.get('X-Agent-Auth')
    if auth_header != 'your_secret_token': # Replace with a secure token/method
        log("Unauthorized reboot attempt", level=logging.WARNING)
        return jsonify(error="Unauthorized"), 401

    try:
        # In a real application, you might want to check if the agent is busy here
        # before initiating the reboot.
        initiate_reboot()
        return jsonify(status="Reboot initiated")
    except Exception as e:
        log(f"Error initiating reboot: {e}", level=logging.ERROR)
        return jsonify(error=f"Failed to initiate reboot: {e}"), 500
        if buf:
             buf.seek(0) # Ensure the buffer is at the start
             return send_file(buf, mimetype='image/png', as_attachment=False, download_name='screenshot.png')
        else:
             log("Screenshot capture succeeded but returned no image buffer.", level=logging.ERROR)
             return jsonify(error="Screenshot failed: No image data."), 500
    else:
        return jsonify(error=result.get("message")), result.get("status_code", 500)

# --- Log Streaming ---
def stream_logs_api():
    def tail_log():
        try:
            with open(LOG_FILE, "r") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        # SSE format: data: message\n\n
                        yield f"data: {line.strip()}\\n\\n" # Ensure proper SSE format
                    else:
                        # Yield a keep-alive SSE comment every 2 seconds if no new log line
                        yield ": keep-alive\n\n"
                        time.sleep(2)
        except FileNotFoundError:
             yield "data: Log file not found.\\n\\n"
        except Exception as e:
             yield f"data: Error reading log file: {e}\\n\\n"
    # Set headers for SSE
    response = Response(tail_log(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no' # Useful for Nginx buffering issues
    return response

# --- Web UI Routes (React App) ---
# These might need to be handled in agent.py or a separate file depending on Flask setup
# For now, defining the functions here.

def index_route(react_static_folder):
    """Serves the main index.html for the React application."""
    log("Serving React app root (index.html)")
    index_path = os.path.join(react_static_folder, 'index.html')
    if not os.path.exists(index_path):
        log(f"React index.html not found at: {index_path}", level=logging.ERROR)
        # Provide a more helpful error message if the build is missing
        if not getattr(sys, 'frozen', False) and not os.path.isdir(react_static_folder): # Need to import sys
             return "React build folder not found. Please run 'npm run build' in the 'react-ui' directory.", 503 # Service Unavailable
        return "React application index.html not found.", 404
    # Use send_from_directory to correctly handle MIME types and caching
    return send_from_directory(react_static_folder, 'index.html')

def serve_react_static_files_route(path, react_static_folder):
    """Serves static files (JS, CSS, images) for the React application."""
    # send_from_directory handles security (prevents path traversal)
    # It also handles setting appropriate MIME types
    # Assets are located in a subdirectory named 'assets' within the react_static_folder
    return send_from_directory(os.path.join(react_static_folder, 'assets'), path)

# --- Image Serving ---
def serve_game_image_route(platform, title, launchbox_path):
    safe_platform = urllib.parse.unquote(platform)
    original_title = urllib.parse.unquote(title)
    import re # Need to import re
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', original_title) # Sanitize

    base_path = os.path.join(launchbox_path, "Images", safe_platform, "Clear Logo")
    preferred_pattern = os.path.join(base_path, f"{safe_title}-01.png")
    fallback_pattern = os.path.join(base_path, f"{safe_title}*.png")

    import glob # Need to import glob
    matches = glob.glob(preferred_pattern)
    if not matches:
        matches = glob.glob(fallback_pattern)

    if matches:
        # log(f"Logo found: {matches[0]}") # Reduce log spam
        return send_file(matches[0], mimetype='image/png')
    else:
        log(f"Logo not found for: {safe_title} in {safe_platform} (searched in {base_path})")
        return "", 404

def serve_temp_image_route(filename):
    """Serves a temporary image file."""
    log(f"Request to serve temporary image: {filename}", level=logging.DEBUG)
    # Construct the full path to the temporary file
    temp_file_path = os.path.join(temp_image_path, filename)

    # Validate the path to ensure it's within the temporary directory using filesystem_utils
    validated_path, error = is_temp_image_path_safe(temp_file_path)

    if error:
        log(f"Temporary image serving failed for '{filename}': {error}", level=logging.WARNING)
        return jsonify(error=error), 403 # Use 403 for access denied/validation issues

    try:
        log(f"Serving temporary image from: {validated_path}", level=logging.DEBUG)
        # Use send_file to serve the image
        return send_file(validated_path, mimetype='image/png', as_attachment=False) # Assuming PNG format for generated images
    except FileNotFoundError:
        log(f"Temporary image file not found: {validated_path}", level=logging.WARNING)
        return jsonify(error="Temporary image file not found"), 404
    except Exception as e:
        log(f"Error serving temporary image {validated_path}: {e}", level=logging.ERROR)
        return jsonify(error=f"Error serving temporary image: {e}"), 500
