import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
import logging
import re
import urllib.parse

# --- Configuration (These might need to be passed in or read from a config) ---
# For now, hardcoding based on original agent.py
USER_HOME = os.path.expanduser("~")
LAUNCHBOX_PATH = os.path.join(USER_HOME, "LaunchBox")
PLATFORMS_PATH = os.path.join(LAUNCHBOX_PATH, "Data", "Platforms")
PLAYLISTS_PATH = os.path.join(LAUNCHBOX_PATH, "Data", "Playlists")

# --- Logging Setup (Assuming basic logging is configured in the main agent.py) ---
# Need to ensure logging is configured before these functions are called
def log(msg, level=logging.INFO):
    logging.log(level, msg)

# --- Helper Functions ---

def get_all_games():
    games = []
    if not os.path.isdir(PLATFORMS_PATH):
        log(f"Platforms path missing: {PLATFORMS_PATH}")
        return games

    xml_files = [f for f in os.listdir(PLATFORMS_PATH) if f.endswith(".xml")]
    log(f"Found {len(xml_files)} platform XML files in: {PLATFORMS_PATH}")

    for filename in xml_files:
        filepath = os.path.join(PLATFORMS_PATH, filename)
        count = 0
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            platform_name = os.path.splitext(filename)[0]
            for game in root.findall("Game"):
                game_data = {
                    "title": game.findtext("Title", ""),
                    "id": game.findtext("ID", ""),
                    "platform": game.findtext("Platform", platform_name),
                    "path": game.findtext("ApplicationPath", "")
                }
                # DEBUG: Log a sample game ID
                if game_data["title"] == "Donkey Kong":
                    log(f"DEBUG: Extracted Donkey Kong ID: {game_data['id']}", level=logging.DEBUG)
                games.append(game_data)
                count += 1
            log(f"Parsed {count} games from {filename}")
        except ET.ParseError as e:
            log(f"XML parse error in platform file {filename}: {e}", level=logging.ERROR)
        except Exception as e:
            log(f"Unexpected error parsing platform file {filename}: {str(e)}", level=logging.ERROR)

    return sorted(games, key=lambda x: x.get('title', '')) # Sort safely

def get_playlists_data():
    log("Reading playlists...")
    playlists = []
    if not os.path.isdir(PLAYLISTS_PATH):
        log(f"Playlists path missing: {PLAYLISTS_PATH}", level=logging.WARNING)
        return playlists

    # Define the base path for playlist images
    PLAYLIST_IMAGES_BASE_PATH = os.path.join(LAUNCHBOX_PATH, "Images", "Playlists")

    for filename in os.listdir(PLAYLISTS_PATH):
        if filename.endswith(".xml"):
            path = os.path.join(PLAYLISTS_PATH, filename)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                playlist_element = root.find("Playlist")
                if playlist_element is None:
                    log(f"Could not find <Playlist> element in {filename}", level=logging.WARNING)
                    continue
                name = playlist_element.findtext("Name", "")
                game_ids = [g.text for g in root.findall("PlaylistGame/GameId") if g.text] # Ensure g.text is not None
                # DEBUG: Log sample playlist IDs
                if name == "1 Player _ Turn base":
                     log(f"DEBUG: Extracted Game IDs for '{name}': {game_ids[:5]}...", level=logging.DEBUG) # Log first 5
                playlist_data = {"name": name, "gameIds": game_ids, "game_count": len(game_ids)}

                # Construct and check for banner image path
                # Sanitize playlist name for path construction
                safe_playlist_name = re.sub(r'[<>:"/\\|?*]', '_', name)
                banner_image_path = os.path.join(PLAYLIST_IMAGES_BASE_PATH, safe_playlist_name, "Clear Logo", f"{safe_playlist_name}.png")

                if os.path.exists(banner_image_path):
                    # Include the path in the data, potentially relative to LAUNCHBOX_PATH or absolute
                    # Sending absolute path for now, can adjust if needed for frontend
                    playlist_data["bannerImagePath"] = banner_image_path
                    log(f"Found banner image for playlist '{name}': {banner_image_path}", level=logging.DEBUG)
                else:
                    log(f"No banner image found for playlist '{name}' at expected path: {banner_image_path}", level=logging.DEBUG)


                playlists.append(playlist_data)
                log(f"Parsed playlist '{name}' with {len(game_ids)} games from {filename}")

                # --- Repair Check (even if parsing succeeded, check for malformed structure) ---
                # Read the raw content to check for the specific broken pattern
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Simple check for the pattern </Playlist><PlaylistGame>
                # This is a basic check and might need refinement depending on variations
                if "</Playlist><PlaylistGame>" in content:
                    log(f"Detected potentially malformed XML in {filename}. Attempting repair.", level=logging.WARNING)
                    # Re-parse and pretty-print to fix formatting
                    try:
                        repaired_xml_string = ET.tostring(root, encoding='utf-8')
                        dom = xml.dom.minidom.parseString(repaired_xml_string)
                        pretty_xml_string = dom.toprettyxml(indent="  ", encoding="utf-8")

                        with open(path, "wb") as f:
                            f.write(pretty_xml_string)
                        log(f"Successfully repaired and pretty-printed {filename}.")
                    except Exception as repair_e:
                        log(f"Failed to repair {filename} after detecting malformed structure: {repair_e}", level=logging.ERROR)


            except ET.ParseError as e:
                log(f"XML parse error in playlist {filename}: {e}. Attempting repair.", level=logging.ERROR)
                # --- Repair Logic for Parse Errors ---
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Attempt to fix the specific broken pattern: insert newline and indent after </Playlist>
                    # This regex looks for </Playlist> immediately followed by <PlaylistGame>
                    repaired_content = re.sub(r"</Playlist>(<PlaylistGame>)", r"</Playlist>\n  \1", content)

                    # Try parsing the repaired content
                    repaired_root = ET.fromstring(repaired_content)

                    # If parsing is successful, pretty-print and save
                    repaired_xml_string = ET.tostring(repaired_root, encoding='utf-8')
                    dom = xml.dom.minidom.parseString(repaired_xml_string)
                    pretty_xml_string = dom.toprettyxml(indent="  ", encoding="utf-8") # Use 2 spaces for indent

                    with open(path, "wb") as f: # Open in binary mode for writing bytes
                        f.write(pretty_xml_string)

                    log(f"Successfully repaired and re-saved {filename} after parse error.")

                    # Re-parse the repaired file to add to the playlists list
                    tree = ET.parse(path)
                    root = tree.getroot()
                    playlist_element = root.find("Playlist")
                    if playlist_element is not None:
                        name = playlist_element.findtext("Name", "")
                        game_ids = [g.text for g in root.findall("PlaylistGame/GameId") if g.text]
                        playlist_data = {"name": name, "gameIds": game_ids, "game_count": len(game_ids)}

                        # Construct and check for banner image path for repaired file
                        safe_playlist_name = re.sub(r'[<>:"/\\|?*]', '_', name)
                        banner_image_path = os.path.join(PLAYLIST_IMAGES_BASE_PATH, safe_playlist_name, "Clear Logo", f"{safe_playlist_name}.png")

                        if os.path.exists(banner_image_path):
                            playlist_data["bannerImagePath"] = banner_image_path
                            log(f"Found banner image for repaired playlist '{name}': {banner_image_path}", level=logging.DEBUG)
                        else:
                            log(f"No banner image found for repaired playlist '{name}' at expected path: {banner_image_path}", level=logging.DEBUG)

                        playlists.append(playlist_data)
                        log(f"Parsed repaired playlist '{name}' with {len(game_ids)} games from {filename}")
                    else:
                         log(f"Repaired file {filename} still missing <Playlist> element.", level=logging.WARNING)


                except Exception as repair_e:
                    log(f"Failed to repair {filename} after parse error: {repair_e}", level=logging.ERROR)
                    # If repair fails, skip this playlist
                    continue

            except Exception as e:
                 log(f"Unexpected error parsing playlist {filename}: {str(e)}", level=logging.ERROR)
                 continue # Skip this playlist on unexpected errors
    return playlists

def find_orphaned_games():
    log("Finding orphaned games...")
    all_games = get_all_games()
    playlists_data = get_playlists_data()

    playlist_game_ids = set()
    for playlist in playlists_data:
        ids = playlist.get("gameIds")
        if isinstance(ids, list):
             playlist_game_ids.update(ids)
        else:
            log(f"Playlist '{playlist.get('name', 'Unknown')}' has invalid or missing 'gameIds'", level=logging.WARNING)

    orphaned_games = [
        game for game in all_games
        if game.get("id") and game.get("id") not in playlist_game_ids
    ]
    log(f"Found {len(orphaned_games)} orphaned games.")
    return orphaned_games

def add_games_to_playlist(playlist_name, game_ids):
    log(f"Attempting to add {len(game_ids)} games to playlist: {playlist_name}")

    if not playlist_name or not game_ids:
        log("Invalid input for add_games_to_playlist", level=logging.WARNING)
        return {"status": "error", "message": "Invalid input"}

    playlist_found = False
    for filename in os.listdir(PLAYLISTS_PATH):
        if filename.endswith(".xml"):
            path = os.path.join(PLAYLISTS_PATH, filename)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                playlist_element = root.find("Playlist")
                if playlist_element is not None and playlist_element.findtext("Name", "") == playlist_name:
                    playlist_found = True
                    existing_ids = {g.text for g in root.findall("PlaylistGame/GameId")}
                    added_count = 0
                    for gid in game_ids:
                        if gid not in existing_ids:
                            pg_node = ET.Element("PlaylistGame")
                            gid_node = ET.SubElement(pg_node, "GameId")
                            gid_node.text = gid
                            root.append(pg_node)
                            added_count += 1
                            existing_ids.add(gid)

                    if added_count > 0:
                        # Use minidom for pretty printing
                        xml_string = ET.tostring(root, encoding='utf-8')
                        dom = xml.dom.minidom.parseString(xml_string)
                        pretty_xml_string = dom.toprettyxml(indent="  ", encoding="utf-8") # Use 2 spaces for indent

                        with open(path, "wb") as f: # Open in binary mode for writing bytes
                            f.write(pretty_xml_string)

                        log(f"Updated playlist '{playlist_name}' with {added_count} new games and pretty-printed.")
                        return {"status": "updated", "added": added_count}
                    else:
                        log(f"No new games to add to playlist '{playlist_name}'.")
                        return {"status": "no changes", "added": 0}

            except ET.ParseError as e:
                log(f"Failed to parse playlist {filename} for update: {e}", level=logging.ERROR)
                return {"status": "error", "message": f"Failed to parse playlist file: {e}"}
            except Exception as e:
                log(f"Error updating playlist {filename}: {e}", level=logging.ERROR)
                return {"status": "error", "message": f"Error updating playlist file: {e}"}

    if not playlist_found:
        log(f"Playlist '{playlist_name}' not found for updating.", level=logging.WARNING)
        return {"status": "playlist not found"}
    else:
        # This path might not be reachable if playlist_found was True but update failed
        log(f"Update failed for playlist '{playlist_name}', but file was found.", level=logging.ERROR)
        return {"status": "error", "message": "Failed to update playlist file"}

def delete_playlist(playlist_name):
    log(f"Attempting to delete playlist: {playlist_name}")

    if not playlist_name:
        log("Invalid input for delete_playlist", level=logging.WARNING)
        return {"status": "error", "message": "Invalid input"}

    playlist_filename = f"{playlist_name}.xml"
    playlist_path = os.path.join(PLAYLISTS_PATH, playlist_filename)

    if not os.path.exists(playlist_path):
        log(f"Playlist file not found for deletion: {playlist_path}", level=logging.WARNING)
        return {"status": "playlist not found"}

    try:
        os.remove(playlist_path)
        log(f"Successfully deleted playlist file: {playlist_path}")
        return {"status": "deleted"}
    except OSError as e:
        log(f"Error deleting playlist file {playlist_path}: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Failed to delete playlist file: {e}"}
    except Exception as e:
        log(f"Unexpected error deleting playlist {playlist_path}: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Unexpected error: {e}"}

def get_game_details(game_ids_to_find):
    log(f"Received request for game details for {len(game_ids_to_find)} IDs: {game_ids_to_find[:10]}...", level=logging.DEBUG)

    if not game_ids_to_find:
        return [] # Return empty list if no IDs provided

    all_games = get_all_games()
    # Create a lookup map for faster searching
    games_map = {game.get("id"): game for game in all_games if game.get("id")}

    found_games = []
    for game_id in game_ids_to_find:
        if game_id in games_map:
            found_games.append(games_map[game_id])
        else:
             log(f"Game ID {game_id} requested but not found in platform data.", level=logging.WARNING)

    log(f"Returning details for {len(found_games)} games.", level=logging.DEBUG)
    return found_games

def apply_playlist_banner_image(playlist_name, temp_image_path, launchbox_path):
    log(f"Attempting to apply banner for playlist '{playlist_name}' from temporary path: {temp_image_path}", level=logging.DEBUG)

    if not playlist_name or not temp_image_path or not launchbox_path:
        log("Invalid input for apply_playlist_banner_image", level=logging.WARNING)
        return {"status": "error", "message": "Invalid input"}

    # Construct the permanent destination path
    PLAYLIST_IMAGES_BASE_PATH = os.path.join(launchbox_path, "Images", "Playlists")
    safe_playlist_name = re.sub(r'[<>:"/\\|?*]', '_', playlist_name)
    dest_dir = os.path.join(PLAYLIST_IMAGES_BASE_PATH, safe_playlist_name, "Clear Logo")
    dest_path = os.path.join(dest_dir, f"{safe_playlist_name}.png")

    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy the temporary file to the permanent location
        import shutil
        shutil.copy2(temp_image_path, dest_path)
        log(f"Successfully copied temporary image '{temp_image_path}' to permanent location: '{dest_path}'", level=logging.DEBUG)

        return {"status": "success", "message": "Playlist banner image applied successfully"}

    except FileNotFoundError:
        log(f"Apply banner failed: Temporary file not found at {temp_image_path}", level=logging.ERROR)
        return {"status": "error", "message": "Temporary image file not found"}
    except PermissionError:
        log(f"Apply banner failed: Permission denied to write to {dest_path}", level=logging.ERROR)
        return {"status": "error", "message": "Permission denied to save image"}
    except Exception as e:
        log(f"Error applying playlist banner image: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Failed to apply playlist banner image: {e}"}

def get_playlist_banner_image_path(playlist_name, launchbox_path):
    log(f"Attempting to get banner path for playlist: {playlist_name}", level=logging.DEBUG)

    if not playlist_name or not launchbox_path:
        log("Invalid input for get_playlist_banner_image_path", level=logging.WARNING)
        return None

    # Sanitize playlist name for path construction
    safe_playlist_name = re.sub(r'[<>:"/\\|?*]', '_', playlist_name)
    # Construct the expected banner image path
    banner_image_path = os.path.join(launchbox_path, "Images", "Playlists", safe_playlist_name, "Clear Logo", f"{safe_playlist_name}.png")

    if os.path.isfile(banner_image_path):
        log(f"Found playlist banner file at: {banner_image_path}", level=logging.DEBUG)
        return banner_image_path
    else:
        log(f"Playlist banner file not found at: {banner_image_path}", level=logging.WARNING)
        return None
