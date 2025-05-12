import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog # Added simpledialog
from datetime import datetime
import hashlib
import threading
import time
import socket # Added for UDP
import os # Added for checking file existence
import webbrowser # Added for opening URLs
import queue # Added for thread-safe communication

# --- Global Variables ---
MACHINES_JSON_FILE = "machines.json"
known_machines_config = {} # Dictionary to store config {hostname: {"type": "arcade", ...}} (Loaded from JSON)
discovered_machines = {} # Dictionary to store real-time data {hostname: {payload: {...}, last_seen: timestamp}}
machine_lock = threading.Lock() # Lock for accessing BOTH dictionaries
# config_dirty flag removed
UDP_LISTEN_PORT = 5152
OFFLINE_THRESHOLD = 10 # Seconds before marking a machine as offline
REFRESH_INTERVAL_MS = 3000 # How often to refresh the UI (milliseconds)

# --- JSON Handling ---
def load_machines():
    """Loads machine configurations from JSON file."""
    global known_machines_config
    if not os.path.exists(MACHINES_JSON_FILE):
        print(f"{MACHINES_JSON_FILE} not found. Starting with empty config.")
        return {} # Return empty dict if file doesn't exist
    try:
        with open(MACHINES_JSON_FILE, "r") as f:
            data = json.load(f)
            # Convert list of dicts to dict keyed by hostname
            config = {m['hostname']: m for m in data if 'hostname' in m}
            print(f"Loaded {len(config)} machines from {MACHINES_JSON_FILE}")
            return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {MACHINES_JSON_FILE}: {e}. Starting with empty config.")
        messagebox.showerror("Config Error", f"Could not load or parse {MACHINES_JSON_FILE}.\n{e}")
        return {}

def save_machines():
    """Saves the current known_machines_config back to JSON file."""
    global known_machines_config, machine_lock # Removed config_dirty
    machines_to_save = []
    with machine_lock: # Lock only while reading the config
        # Convert back to list of dicts for saving
        # Make a deep copy? For simple dicts like this, list() is probably fine.
        machines_to_save = list(known_machines_config.values())
        # config_dirty flag removed

    if not machines_to_save: # Don't save if list is empty (e.g., error during load)
        print("Skipping save, no machine configurations loaded.")
        return

    try:
        # Perform file I/O outside the lock
        with open(MACHINES_JSON_FILE, "w") as f:
            json.dump(machines_to_save, f, indent=2)
        print(f"Saved {len(machines_to_save)} machines to {MACHINES_JSON_FILE}") # Corrected variable name
    except IOError as e:
        messagebox.showerror("Config Error", f"Could not save {MACHINES_JSON_FILE}.\n{e}")

# --- Queue Checking Function (Moved Before run_ui) ---
def check_update_queue():
    """Checks the update queue and updates the UI."""
    global update_queue, update_status_var, update_progress_var, update_selected_button, root
    try:
        while True: # Process all messages currently in the queue
            message = update_queue.get_nowait()
            msg_type = message[0]
            msg_data = message[1]

            if msg_type == 'status':
                update_status_var.set(msg_data)
            elif msg_type == 'progress':
                update_progress_var.set(msg_data)
            elif msg_type == 'complete':
                failed_updates = msg_data
                if failed_updates:
                    messagebox.showerror("Update Failures", "Failed to update the following selected machines:\n- " + "\n- ".join(failed_updates))
                    update_status_var.set("Update Selected process completed with failures.")
                else:
                    update_status_var.set("Update Selected process completed successfully.")
                # Re-enable button and reset progress
                if 'update_selected_button' in globals() and update_selected_button: # Check if button exists
                    update_selected_button.config(state=tk.NORMAL)
                if update_progress_var: # Check if var exists
                    update_progress_var.set(0)
                return # Stop checking queue once complete message is received
            else:
                 print(f"Unknown message type in update queue: {msg_type}")

            if root: # Check if root exists before updating idletasks
                 root.update_idletasks() # Update UI

    except queue.Empty:
        # Queue is empty, schedule next check only if button is still disabled (update in progress)
        if 'update_selected_button' in globals() and update_selected_button and update_selected_button['state'] == tk.DISABLED:
             if root: # Check if root exists before scheduling
                  root.after(100, check_update_queue) # Check again in 100ms
    except Exception as e:
        print(f"Error in check_update_queue: {e}")
        # Attempt to re-enable button in case of unexpected error
        if 'update_selected_button' in globals() and update_selected_button:
             update_selected_button.config(state=tk.NORMAL)


# --- Global Tkinter Variables (for cross-thread updates) ---
update_progress_var = None
update_status_var = None
update_queue = queue.Queue() # Queue for update thread communication

# --- Helper Functions ---
def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- HTTP Ping Function (Restored) ---
def ping_machine(hostname):
    """Performs an HTTP ping to a specific hostname."""
    try:
        url = f"http://{hostname}:5151/api/ping"
        r = requests.get(url, timeout=2)
        r.raise_for_status()
        data = r.json()
        print(f"HTTP Ping success for {hostname}")
        return data # Return the raw payload from the agent
    except requests.exceptions.RequestException as e:
        print(f"HTTP Ping failed for {hostname}: {e}")
        return None # Indicate failure

# --- API Interaction Functions (take hostname string) ---
def get_layout(hostname):
    try:
        response = requests.get(f"http://{hostname}:5151/api/control-layout", timeout=2)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting layout for {hostname}: {e}")
        return None

def get_games(hostname):
    try:
        r = requests.get(f"http://{hostname}:5151/api/launchbox/games", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error getting games for {hostname}: {e}")
        return []

def get_playlists(hostname):
    try:
        r = requests.get(f"http://{hostname}:5151/api/launchbox/playlists", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error getting playlists for {hostname}: {e}")
        return []

def save_layout(hostname, layout):
    try:
        response = requests.put(
            f"http://{hostname}:5151/api/control-layout",
            json=layout,
            timeout=2
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error saving layout for {hostname}: {e}")
        return False

# --- UI Functions ---

# Removed update_all_agents function

def update_selected_agents_start(hostnames, filepath):
    """Starts the background thread for updating selected agents."""
    global root, update_status_var, update_progress_var, update_selected_button # Need button ref

    if not hostnames:
        messagebox.showerror("Error", "No machine(s) selected.")
        return
    if not filepath:
        return

    if not messagebox.askyesno("Confirmation", f"Attempt to update agent on {len(hostnames)} selected machine(s)?\n(Will attempt even if shown as Offline)"):
        return

    # Disable button, reset progress/status
    update_selected_button.config(state=tk.DISABLED)
    update_status_var.set("Starting update process...")
    update_progress_var.set(0)
    root.update_idletasks()

    # Start background thread
    thread = threading.Thread(target=_update_thread_func, args=(list(hostnames), filepath, update_queue), daemon=True)
    thread.start()
    # Start checking the queue
    root.after(100, check_update_queue) # Check queue shortly after starting

def _update_thread_func(hostnames, filepath, q):
    """Background thread function to perform updates and put results in queue."""
    total_machines = len(hostnames)
    updated_count = 0
    failed_updates = []

    for hostname in hostnames:
        # Put status update in queue
        q.put(('status', f"Attempting update on {hostname}..."))

        success = attempt_single_update(hostname, filepath) # This function now only returns True/False
        if not success:
            failed_updates.append(hostname)
        else:
            # Optionally put success status per machine
             q.put(('status', f"Successfully updated {hostname}"))


        updated_count += 1
        progress = int((updated_count / total_machines) * 100)
        # Put progress update in queue
        q.put(('progress', progress))

    # Signal completion via queue
    q.put(('complete', failed_updates))


def attempt_single_update(hostname, filepath):
    """Handles the actual update request for one machine. Returns True on success, False on failure."""
    # Removed global status_label - status updated via events now
    """Handles the actual update request for one machine. Returns True on success, False on failure."""
    # global status_label # Allow updating status label on error - No longer needed
    try:
        sha256_hash = calculate_sha256(filepath)
        with open(filepath, "rb") as f:
            files_payload = {'file': f}
            data_payload = {'sha256': sha256_hash}
            url = f"http://{hostname}:5151/api/update-agent"
            response = requests.post(url, files=files_payload, data=data_payload, timeout=15) # Longer timeout for update
            response.raise_for_status() # Check for HTTP errors
            return True
    except requests.exceptions.Timeout:
        print(f"Update timeout for {hostname}")
        # Status update handled by caller via queue
        return False
    except requests.exceptions.RequestException as e:
         print(f"Update network error for {hostname}: {e}")
         # Status update handled by caller via queue
         return False
    except Exception as e:
        print(f"Update failed for {hostname}: {e}")
        # Status update handled by caller via queue
        return False


def show_editor(hostname):
    if not hostname:
        messagebox.showerror("Error", "No machine selected.")
        return

    layout = get_layout(hostname) # Use hostname
    if layout is None:
        messagebox.showerror("Error", f"Cannot retrieve layout from {hostname}")
        return

    editor = tk.Toplevel()
    editor.title(f"Edit Controls – {hostname}")
    entries = {}
    # Ensure layout is a dictionary before iterating
    if isinstance(layout, dict):
        for idx, (key, value) in enumerate(layout.items()):
            tk.Label(editor, text=key).grid(row=idx, column=0, sticky='e', padx=5, pady=2)
            var = tk.StringVar(value=str(value))
            entries[key] = var
            tk.Entry(editor, textvariable=var, width=6).grid(row=idx, column=1, padx=5, pady=2)
    else:
        tk.Label(editor, text="Invalid layout data received.").grid(row=0, column=0, columnspan=2)
        return # Don't show save button if layout is bad

    def save_action():
        try:
            new_layout = {
                key: int(val.get()) if val.get().isdigit() else 0
                for key, val in entries.items()
            }
            if save_layout(hostname, new_layout): # Use hostname
                messagebox.showinfo("Saved", "Layout updated successfully")
                editor.destroy()
            else:
                messagebox.showerror("Error", "Failed to save layout")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    tk.Button(editor, text="Save", command=save_action).grid(
        row=len(entries), column=0, columnspan=2, pady=10 # Use len(entries)
    )

def show_games_ui(hostname):
    if not hostname:
        messagebox.showerror("Error", "No machine selected.")
        return

    games = get_games(hostname) # Use hostname
    playlists = get_playlists(hostname) # Use hostname

    if not games:
        messagebox.showerror("Error", f"No game data available from {hostname}")
        return

    assigned_game_ids = set()
    for p in playlists:
        assigned_game_ids.update(p.get("gameIds", []))

    unassigned = [g for g in games if g.get("id") not in assigned_game_ids]

    window = tk.Toplevel()
    window.title(f"LaunchBox – {hostname}")

    label = tk.Label(window, text=f"Orphan Games ({len(unassigned)} not in a playlist)")
    label.pack(pady=5)

    listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, width=60, height=20)
    for g in unassigned:
        listbox.insert(tk.END, f"{g['title']} ({g['platform']})")
    listbox.pack(padx=10, pady=5)

    def add_to_playlist_action():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No games selected.")
            return

        playlist_names = [p['name'] for p in playlists if 'name' in p] # Ensure name exists
        if not playlist_names:
            messagebox.showinfo("Info", "No playlists available.")
            return

        # Use simpledialog which was imported
        playlist_name = simpledialog.askstring("Add to Playlist", f"Enter playlist name ({', '.join(playlist_names)}):", parent=window)
        if not playlist_name:
            return

        selected_ids = [unassigned[i]["id"] for i in selected_indices if i < len(unassigned) and "id" in unassigned[i]]

        if not selected_ids:
             messagebox.showwarning("Warning", "Selected games have no IDs.")
             return

        try:
            url = f"http://{hostname}:5151/api/launchbox/playlists/add" # Use hostname
            r = requests.post(url, json={"playlist": playlist_name, "games": selected_ids}, timeout=5)
            r.raise_for_status() # Check for HTTP errors
            result = r.json()
            messagebox.showinfo("Success", f"Added {result.get('added', 0)} game(s) to {playlist_name}")
            window.destroy() # Close on success
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(window, text="Add to Playlist", command=add_to_playlist_action).pack(pady=5)


# --- UDP Listener ---
def udp_listener_thread():
    global discovered_machines, known_machines_config, machine_lock # Removed config_dirty
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse if needed
    try:
        udp_socket.bind(("0.0.0.0", UDP_LISTEN_PORT))
        print(f"UDP Listener started on port {UDP_LISTEN_PORT}")
    except Exception as e:
        print(f"FATAL: Could not bind UDP listener to port {UDP_LISTEN_PORT}: {e}")
        messagebox.showerror("Network Error", f"Could not bind UDP listener to port {UDP_LISTEN_PORT}.\nIs another instance running?\n\n{e}")
        return # Exit thread if bind fails

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024) # buffer size is 1024 bytes
            payload = json.loads(data.decode('utf-8'))
            hostname = payload.get("hostname")
            machine_type = payload.get("type", "unknown") # Get type from payload

            if hostname:
                # print(f"UDP Received from {hostname} ({addr[0]})") # Verbose Debug
                with machine_lock:
                    # Update real-time data
                    discovered_machines[hostname] = {
                        "payload": payload,
                        "last_seen": time.time()
                    }
                    # Check if known, add if new
                    needs_save = False
                    if hostname not in known_machines_config:
                        print(f"Discovered new machine via UDP: {hostname}")
                        known_machines_config[hostname] = {"hostname": hostname, "type": machine_type}
                        needs_save = True # Flag that we need to save *after* releasing lock

                # Save immediately after releasing lock if a new machine was added
                if needs_save:
                    save_machines()

        except json.JSONDecodeError:
            print(f"Received invalid JSON UDP packet from {addr[0]}")
        except OSError as e:
             # Handle specific errors like socket closed during shutdown
             print(f"UDP socket error: {e}")
             break # Exit loop if socket is closed
        except Exception as e:
            print(f"Error in UDP listener: {type(e).__name__}: {e}")
            time.sleep(1) # Avoid busy-looping on errors

# --- Main UI Setup ---
def run_ui():
    # Make Tkinter variables global for cross-thread updates via events
    global progress_bar, status_label, root, tree, known_machines_config
    global update_progress_var, update_status_var, update_selected_button

    # Load initial config
    known_machines_config = load_machines()

    root = tk.Tk()
    root.title("Arcade Controller")

    # Define columns
    columns = ("Hostname", "Type", "Status", "Last Seen", "Version", "Disk Total (GB)", "Disk Free (GB)", "CPU %", "RAM %", "BigBox")
    tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended") # Allow extended selection
    for col in columns:
        tree.heading(col, text=col)
        width = 75 if col in ["CPU %", "RAM %", "BigBox", "Status", "Type"] else 110
        if col == "Hostname": width = 140
        if col == "Last Seen": width = 130
        if col == "Version": width = 80
        tree.column(col, anchor="center", width=width, stretch=False) # Prevent stretching initially

    tree.grid(row=0, column=0, columnspan=6, padx=10, pady=10, sticky="nsew") # Span 6 columns now
    root.grid_rowconfigure(0, weight=1) # Allow treeview row to expand
    root.grid_columnconfigure(0, weight=1) # Allow treeview column to expand (needed for columnspan)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)
    root.grid_columnconfigure(4, weight=1)
    root.grid_columnconfigure(5, weight=1)

    # --- Initial UI Population ---
    def populate_initial_list():
        """Inserts machines from loaded config into the treeview initially."""
        global known_machines_config, tree
        with machine_lock: # Access config safely
            for hostname, config_data in known_machines_config.items():
                 # Initial state is unknown/offline until UDP or ping confirms
                 values = (
                     hostname,
                     config_data.get("type", "N/A"),
                     "Offline", # Initial status
                     "Never",   # Initial last seen
                     "—",       # Initial version
                     "—", "—", "—", "—", "—" # Placeholder data
                 )
                 if not tree.exists(hostname): # Avoid error if somehow already exists
                      tree.insert("", "end", iid=hostname, values=values, tags=('offline',))
        # Configure tag styles (e.g., grey text for offline)
        tree.tag_configure('offline', foreground='grey')


    # --- Refresh UI Function (Called by root.after) ---
    def refresh_ui():
        global known_machines_config, discovered_machines, machine_lock, tree # Removed config_dirty
        # Removed check for config_dirty

        current_time = time.time()
        # Use IIDs (hostnames) stored in the tree for checking existence
        existing_tree_items = tree.get_children()
        existing_hostnames_in_tree = set(existing_tree_items) # iid is hostname

        with machine_lock:
            # Iterate over known machines from config
            for hostname, config_data in known_machines_config.items():
                # Get real-time data if available
                discovered_data = discovered_machines.get(hostname, {})
                payload = discovered_data.get("payload", {})
                last_seen_time = discovered_data.get("last_seen", 0)
                time_since_seen = current_time - last_seen_time

                # Determine status based on UDP data
                if time_since_seen <= OFFLINE_THRESHOLD:
                    status = "Online"
                    last_seen_str = datetime.fromtimestamp(last_seen_time).strftime("%H:%M:%S")
                    # Use payload data if online
                    version = payload.get("version", "N/A")
                    disk_total = payload.get("disk_total_gb", "N/A")
                    disk_free = payload.get("disk_free_gb", "N/A")
                    cpu = payload.get("cpu_percent", "N/A")
                    ram = payload.get("ram_percent", "N/A")
                    bb_running = payload.get("bigbox_running", None)
                    bb_display = "Running" if bb_running else ("Stopped" if bb_running is False else "N/A")
                    machine_type = payload.get("type", config_data.get("type", "N/A")) # Prefer payload type
                else:
                    status = "Offline"
                    last_seen_str = datetime.fromtimestamp(last_seen_time).strftime("%H:%M:%S") + " (Offline)" if last_seen_time > 0 else "Never"
                    # Use placeholder data if offline
                    version = config_data.get("version", "—") # Maybe store last known version?
                    disk_total, disk_free, cpu, ram, bb_display = "—", "—", "—", "—", "—"
                    machine_type = config_data.get("type", "N/A")

                values = (
                    hostname, machine_type, status, last_seen_str, version,
                    disk_total, disk_free, cpu, ram, bb_display
                )

                # Update or insert item in Treeview
                if hostname in existing_hostnames_in_tree:
                    tree.item(hostname, values=values, tags=('offline',) if status == "Offline" else ())
                else:
                    # Insert new item using hostname as IID
                    tree.insert("", "end", iid=hostname, values=values, tags=('offline',) if status == "Offline" else ())

            # Optional: Remove items from tree if they are no longer in known_machines_config
            # (e.g., if manually removed from JSON - requires reloading JSON periodically or on signal)
            current_known_hostnames = set(known_machines_config.keys())
            for item_id in existing_tree_items:
                 if item_id not in current_known_hostnames:
                      try:
                           tree.delete(item_id)
                      except tk.TclError:
                           print(f"Warning: Tried to delete already deleted tree item {item_id}")

        # Configure tag styles (e.g., grey text for offline)
        tree.tag_configure('offline', foreground='grey')

        # Schedule next refresh
        root.after(REFRESH_INTERVAL_MS, refresh_ui)

    # --- Helper to get selected hostnames ---
    def get_selected_hostnames(): # Renamed and returns list
        return tree.selection() # selection() returns a tuple of item IDs (hostnames)

    # --- Double Click Handler ---
    def open_agent_ui(event):
        """Opens the agent web UI in browser on double-click."""
        item_id = tree.identify_row(event.y)
        if item_id: # Check if click was on a valid row
            hostname = item_id # IID is the hostname
            url = f"http://{hostname}:5151/"
            print(f"Opening {url} for {hostname}")
            webbrowser.open_new_tab(url)

    # --- Manual Ping All Function ---
    def manual_ping_all():
        global known_machines_config, tree, status_label
        print("Manual Ping All triggered")
        status_label.config(text="Performing manual ping...")
        root.update()
        items_to_update = tree.get_children() # Get all items currently in the tree (hostnames)
        ping_results = {}

        # Perform pings in background thread to avoid blocking UI
        def ping_thread_func():
            threads = []
            for hostname in items_to_update:
                 thread = threading.Thread(target=lambda h=hostname: ping_results.update({h: ping_machine(h)}), daemon=True)
                 threads.append(thread)
                 thread.start()
            for thread in threads:
                 thread.join(timeout=3) # Wait max 3s per thread

            # Update UI from main thread after pings are done
            root.after(0, update_ui_after_ping)

        def update_ui_after_ping():
             for hostname, result in ping_results.items():
                  try:
                       if result: # Ping successful, update relevant columns
                            values = list(tree.item(hostname, 'values')) # Get current values
                            values[2] = "Online (Pinged)" # Status
                            values[3] = datetime.now().strftime("%H:%M:%S") # Last Seen (now)
                            values[4] = result.get("version", values[4])
                            values[5] = result.get("disk_total_gb", values[5])
                            values[6] = result.get("disk_free_gb", values[6])
                            values[7] = result.get("cpu_percent", values[7])
                            values[8] = result.get("ram_percent", values[8])
                            bb_running = result.get("bigbox_running", None)
                            values[9] = "Running" if bb_running else ("Stopped" if bb_running is False else "N/A")
                            tree.item(hostname, values=tuple(values), tags=()) # Update item, clear tags
                       else: # Ping failed
                            values = list(tree.item(hostname, 'values'))
                            values[2] = "Offline (Ping Fail)"
                            # Don't update other fields on ping fail
                            tree.item(hostname, values=tuple(values), tags=('offline',)) # Keep offline tag
                  except tk.TclError:
                       print(f"Manual Ping: Item {hostname} disappeared from tree before update.")
             status_label.config(text="Manual ping complete.")

        # Start the pinging thread
        threading.Thread(target=ping_thread_func, daemon=True).start()


    # --- Button Actions ---
    def select_agent_file_for_update(update_func):
        """Prompts for file and starts the background update."""
        hostnames = get_selected_hostnames() # Get list of selected hostnames
        if not hostnames:
             messagebox.showerror("Error", "No machine(s) selected for 'Update Selected'.")
             return

        filepath = filedialog.askopenfilename(
            title="Select updated agent.exe",
            filetypes=[("Executable", "*.exe")]
        )
        if filepath:
            # Call the function that starts the background thread
            update_selected_agents_start(hostnames, filepath)


    # --- Buttons Layout (Removed Update All) ---
    button_frame = ttk.Frame(root)
    button_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

    tk.Button(button_frame, text="Refresh (Manual Ping)", command=manual_ping_all).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Layout", command=lambda: show_editor(get_selected_hostnames()[0] if get_selected_hostnames() else None)).pack(side=tk.LEFT, padx=5) # Pass first selected
    # Assign button to global var so it can be disabled/enabled
    update_selected_button = tk.Button(button_frame, text="Update Selected", command=lambda: select_agent_file_for_update(update_selected_agents_start))
    update_selected_button.pack(side=tk.LEFT, padx=5)
    # Removed "Update All Agents" button
    tk.Button(button_frame, text="View Games", command=lambda: show_games_ui(get_selected_hostnames()[0] if get_selected_hostnames() else None)).pack(side=tk.LEFT, padx=5) # Pass first selected
    tk.Button(button_frame, text="Quit", command=root.destroy).pack(side=tk.RIGHT, padx=5) # Quit on the right

    # Progress bar and status label using Tkinter variables
    update_progress_var = tk.IntVar(value=0)
    update_status_var = tk.StringVar(value="Controller started. Loading config and listening for agents...")

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=update_progress_var)
    progress_bar.grid(row=2, column=0, columnspan=6, padx=10, pady=5, sticky="ew")
    status_label = tk.Label(root, textvariable=update_status_var) # Use textvariable
    status_label.grid(row=3, column=0, columnspan=6, padx=10, pady=5, sticky="ew")

    # --- Start Threads ---
    # Start UDP listener thread
    listener = threading.Thread(target=udp_listener_thread, daemon=True)
    listener.start()

    # Populate the list initially from the loaded config
    populate_initial_list()

    # Bind double-click event after tree is created
    tree.bind("<Double-1>", open_agent_ui)

    # Start the first periodic refresh
    root.after(REFRESH_INTERVAL_MS, refresh_ui)

    root.mainloop()

if __name__ == "__main__":
    run_ui()

