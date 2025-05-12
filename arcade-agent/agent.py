from flask import Flask, jsonify, request, Response, send_file, send_from_directory
import logging
import traceback
import os
import threading
import subprocess
import time
import argparse
import sys
import ctypes # Import ctypes for Windows API interaction

# Import functions and configurations from refactored files
from launchbox_utils import (
    get_all_games,
    get_playlists_data,
    find_orphaned_games,
    add_games_to_playlist,
    delete_playlist,
    get_game_details,
    apply_playlist_banner_image,
    get_playlist_banner_image_path,
    LAUNCHBOX_PATH # Import LAUNCHBOX_PATH
)
from filesystem_utils import (
    is_path_safe,
    is_temp_image_path_safe,
    list_directory_contents,
    get_file_content,
    get_launchbox_base_path,
    create_temp_image_directory, # Import the function to create the directory
    TEMP_IMAGE_DIR # Import TEMP_IMAGE_DIR
)
from image_utils import (
    generate_image_gemini,
    generate_image_openai,
    improve_prompt_gemini,
    capture_screenshot
)
from udp_broadcast import udp_broadcast_loop # Import the broadcast loop function
# --- Configuration ---
AGENT_VERSION = "2.1.69"
MACHINE_TYPE = "arcade"
LAYOUT_FILE = "control-layout.json" # Keep config needed in this file
LOG_FILE = "agent.log" # Keep config needed in this file
AGENT_PORT = 5151 # Keep config needed in this file

# --- Dynamic Paths (Support PyInstaller) ---
if getattr(sys, 'frozen', False):
    # Running as executable
    script_dir = os.path.dirname(sys.executable)
    # Path to bundled templates (if still needed for anything else)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    # Path to bundled React static files (mapped from build/react_ui_dist)
    react_static_folder = os.path.join(sys._MEIPASS, 'static/react')
else:
    # Running as script
    script_dir = os.path.dirname(__file__)
    template_folder = os.path.join(script_dir, 'templates')
    # Path to React build output when running as script
    react_static_folder = os.path.join(script_dir, 'build', 'react_ui_dist')

# --- Logging Setup ---
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
def log(msg, level=logging.INFO):
    logging.log(level, msg)

log(f"--- Starting Arcade Agent v{AGENT_VERSION} ---")
log(f"Python version: {sys.version}")
log(f"Script directory: {script_dir}")
log(f"React static folder path: {react_static_folder}")
if getattr(sys, 'frozen', False):
    log(f"Running as executable: {sys.executable}")
    if not os.path.isdir(react_static_folder):
         log(f"CRITICAL: Bundled React static folder not found at expected path: {react_static_folder}", level=logging.ERROR)
elif not os.path.isdir(react_static_folder):
    log(f"WARNING: React build directory not found at expected path for script mode: {react_static_folder}. Run 'npm run build' in 'react-ui'.", level=logging.WARNING)


# --- Global Error Handler ---
def handle_exception(e):
    tb_str = traceback.format_exc()
    log(f"Unhandled Flask exception: {e}\n{tb_str}", level=logging.ERROR)
    response = jsonify(error="Internal Server Error", message=str(e))
    response.status_code = 500
    return response


if __name__ == "__main__":
    # Hide the console window if running as a bundled executable
    if getattr(sys, 'frozen', False):
        try:
            # Get the handle of the console window
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                # Hide the window
                ctypes.windll.user32.ShowWindow(hwnd, 0) # SW_HIDE = 0
        except Exception as e:
            # Log any errors, but don't stop the agent from running
            log(f"Error hiding console window: {e}", level=logging.ERROR)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description=f"Arcade Agent v{AGENT_VERSION}")
    parser.add_argument('--get-version', action='store_true', help='Print agent version and exit.')
    args = parser.parse_args()

    if args.get_version:
        print(AGENT_VERSION)
        sys.exit(0)

    # If not just getting the version, import API routes and initialize Flask app
    from flask import Flask, jsonify, request, Response, send_file, send_from_directory
    from api_routes import ( # Import API route functions
        ping_api,
        get_layout_api,
        update_layout_api,
        start_bigbox_api,
        stop_bigbox_api,
        get_games_api,
        get_playlists_api,
        get_orphaned_games_api,
        get_game_details_api,
        add_to_playlist_api,
        check_update_api,
        trigger_update_api,
        delete_playlist_api,
        delete_cache_api,
        generate_image_api,
        generate_image_gpt_api,
        improve_prompt_api,
        apply_playlist_banner_api,
        serve_playlist_banner_api,
        get_launchbox_basepath_api,
        list_directory_api,
        get_file_content_api,
        screenshot_api,
        stream_logs_api,
        index_route, # Import web UI routes
        serve_react_static_files_route,
        serve_game_image_route,
        serve_temp_image_route
    )

    # Initialize Flask App
    app = Flask(__name__, template_folder=template_folder)

    # --- Global Error Handler ---
    @app.errorhandler(Exception)
    def handle_exception(e):
        tb_str = traceback.format_exc()
        log(f"Unhandled Flask exception: {e}\n{tb_str}", level=logging.ERROR)
        response = jsonify(error="Internal Server Error", message=str(e))
        response.status_code = 500
        return response

    # --- Register API Routes ---
    # Use the imported functions from api_routes.py
    app.route("/api/ping", methods=["GET"])(ping_api)
    app.route("/api/control-layout", methods=["GET"])(get_layout_api)
    app.route("/api/control-layout", methods=["PUT"])(update_layout_api)
    app.route("/api/launchbox/start_bigbox", methods=["POST"])(start_bigbox_api)
    app.route("/api/launchbox/stop_bigbox", methods=["POST"])(stop_bigbox_api)
    app.route("/api/launchbox/games", methods=["GET"])(get_games_api)
    app.route("/api/launchbox/playlists", methods=["GET"])(get_playlists_api)
    app.route("/api/launchbox/orphaned_games", methods=["GET"])(get_orphaned_games_api)
    app.route("/api/launchbox/games/details", methods=["POST"])(get_game_details_api)
    app.route("/api/launchbox/playlists/add", methods=["POST"])(add_to_playlist_api)
    app.route("/api/launchbox/playlists/<path:playlist_name>", methods=["DELETE"])(delete_playlist_api)
    app.route("/api/launchbox/delete_cache", methods=["POST"])(delete_cache_api)
    app.route("/api/generate-image", methods=["GET"])(generate_image_api)
    app.route("/api/generate-image-gpt", methods=["GET"])(generate_image_gpt_api)
    app.route("/api/improve-prompt", methods=["GET"])(improve_prompt_api)
    app.route("/api/launchbox/playlists/apply_banner", methods=["POST"])(apply_playlist_banner_api)
    app.route("/api/launchbox/playlists/banner/<path:playlist_name>", methods=["GET"])(serve_playlist_banner_api)
    app.route("/api/launchbox/basepath", methods=["GET"])(get_launchbox_basepath_api)
    app.route("/api/filesystem/list", methods=["GET"])(list_directory_api)
    app.route("/api/filesystem/content", methods=["GET"])(get_file_content_api)
    app.route("/api/screenshot", methods=["GET"])(screenshot_api)
    app.route("/log")(stream_logs_api) # SSE endpoint

    # --- Register Web UI Routes ---
    app.route("/", endpoint='index_route')(lambda: index_route(react_static_folder))
    app.route("/assets/<path:path>", endpoint='serve_react_static_files_route')(lambda path: serve_react_static_files_route(path, react_static_folder))
    app.route("/img/<platform>/<title>", endpoint='serve_game_image_route')(lambda platform, title: serve_game_image_route(platform, title, LAUNCHBOX_PATH))
    app.route(f"/{TEMP_IMAGE_DIR}/<filename>", methods=["GET"], endpoint='serve_temp_image_route')(serve_temp_image_route)


    # --- Create temporary image directory ---
    create_temp_image_directory()

    # --- Startup Check for Update Batch File ---
    update_batch_file = "update.bat"
    if os.path.exists(update_batch_file):
        log(f"Found existing update batch file: {update_batch_file}. This indicates a previous update attempt may have occurred.")
        # We no longer delete it here, as per user request for debugging.

    # Start the UDP broadcast thread
    broadcast_thread = threading.Thread(target=udp_broadcast_loop, args=(AGENT_VERSION,), daemon=True)
    broadcast_thread.start()
    log("UDP broadcast thread started.")

    # Start the Flask web server
    log(f"Attempting to start Flask server on 0.0.0.0:{AGENT_PORT}")
    try:
        # Note: Running Flask in development mode (debug=True) can cause threads to start twice.
        # Ensure debug=False and use_reloader=False for production/deployment.
        app.run(host="0.0.0.0", port=AGENT_PORT, debug=False, use_reloader=False)
        log("Flask server stopped.")
    except Exception as e:
        log(f"Error starting or running Flask server: {e}", level=logging.ERROR)
