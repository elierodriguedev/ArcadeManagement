import os
import logging
from datetime import datetime

# --- Configuration (These might need to be passed in or read from a config) ---
# For now, hardcoding based on original agent.py
USER_HOME = os.path.expanduser("~")
LAUNCHBOX_PATH = os.path.join(USER_HOME, "LaunchBox")
TEMP_IMAGE_DIR = "temp_images"
script_dir = os.path.dirname(__file__) # Assuming this file is in the agent directory
temp_image_path = os.path.join(script_dir, TEMP_IMAGE_DIR)


# --- Logging Setup (Assuming basic logging is configured in the main agent.py) ---
# Need to ensure logging is configured before these functions are called
def log(msg, level=logging.INFO):
    logging.log(level, msg)

# --- Filesystem Path Validation ---
def is_path_safe(requested_path):
    """Validates if a path is safe and within the LAUNCHBOX_PATH boundary."""
    if not requested_path:
        log("Path validation failed: No path provided.", level=logging.WARNING)
        return None, "No path provided"

    # Resolve the absolute path
    try:
        abs_path = os.path.abspath(requested_path)
    except Exception as e:
         log(f"Path validation failed: Cannot resolve path '{requested_path}': {e}", level=logging.WARNING)
         return None, f"Invalid path format: {e}"

    # Check if the resolved path is within the allowed base directory
    # Use os.path.normpath to handle potential separator differences
    normalized_base = os.path.normpath(LAUNCHBOX_PATH)
    normalized_abs_path = os.path.normpath(abs_path)

    # Ensure the path starts with the base path and doesn't try to escape
    if os.path.commonpath([normalized_base, normalized_abs_path]) != normalized_base:
        log(f"Path validation failed: Path '{abs_path}' is outside allowed directory '{LAUNCHBOX_PATH}'.", level=logging.WARNING)
        return None, "Access denied: Path is outside allowed directory."

    # Check for directory traversal components like '..' within the part *after* the base path
    relative_part = os.path.relpath(normalized_abs_path, normalized_base)
    if '..' in relative_part.split(os.path.sep):
         log(f"Path validation failed: Path '{abs_path}' contains traversal components.", level=logging.WARNING)
         return None, "Access denied: Invalid path components."

    # Check if the path actually exists
    if not os.path.exists(abs_path):
         log(f"Path validation failed: Path '{abs_path}' does not exist.", level=logging.WARNING)
         return None, "Path not found."

    log(f"Path validation successful for: {abs_path}", level=logging.DEBUG)
    return abs_path, None # Return validated absolute path and no error

# --- Filesystem Path Validation for Temporary Images ---
def is_temp_image_path_safe(requested_path):
    """Validates if a path is safe and within the temporary image directory."""
    if not requested_path:
        log("Temporary image path validation failed: No path provided.", level=logging.WARNING)
        return None, "No path provided"

    # Resolve the absolute path
    try:
        abs_path = os.path.abspath(requested_path)
    except Exception as e:
         log(f"Temporary image path validation failed: Cannot resolve path '{requested_path}': {e}", level=logging.WARNING)
         return None, f"Invalid path format: {e}"

    # Check if the resolved path is within the allowed temporary image directory
    normalized_base = os.path.normpath(temp_image_path)
    normalized_abs_path = os.path.normpath(abs_path)

    if os.path.commonpath([normalized_base, normalized_abs_path]) != normalized_base:
        log(f"Temporary image path validation failed: Path '{abs_path}' is outside allowed directory '{temp_image_path}'.", level=logging.WARNING)
        return None, "Access denied: Path is outside allowed temporary directory."

    # Check for directory traversal components
    relative_part = os.path.relpath(normalized_abs_path, normalized_base)
    if '..' in relative_part.split(os.path.sep):
         log(f"Temporary image path validation failed: Path '{abs_path}' contains traversal components.", level=logging.WARNING)
         return None, "Access denied: Invalid path components."

    # Check if the path actually exists and is a file
    if not os.path.isfile(abs_path):
         log(f"Temporary image path validation failed: Path '{abs_path}' does not exist or is not a file.", level=logging.WARNING)
         return None, "File not found or is not a file."

    log(f"Temporary image path validation successful for: {abs_path}", level=logging.DEBUG)
    return abs_path, None # Return validated absolute path and no error

def list_directory_contents(requested_path):
    """Lists files and directories within a validated path."""
    log(f"Attempting to list directory contents for path: {requested_path}", level=logging.DEBUG)

    validated_path, error = is_path_safe(requested_path)
    if error:
        return None, error # Return None for items and the error message

    if not os.path.isdir(validated_path):
         return None, "Path is not a directory"

    items = []
    try:
        for item_name in os.listdir(validated_path):
            item_path = os.path.join(validated_path, item_name)
            try:
                is_dir = os.path.isdir(item_path)
                # Skip items we can't determine type for (e.g., junctions without perms)
                if not is_dir and not os.path.isfile(item_path):
                    log(f"Skipping item with unknown type: {item_path}", level=logging.DEBUG)
                    continue

                item_info = {
                    "name": item_name,
                    "path": item_path, # Send back absolute path
                    "is_dir": is_dir,
                    "size": os.path.getsize(item_path) if not is_dir else 0,
                    "modified": datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat() if os.path.exists(item_path) else None
                }
                items.append(item_info)
            except OSError as e:
                log(f"Permission or other OS error accessing item {item_path}: {e}", level=logging.WARNING)
                # Optionally include an error marker for this item in the response
            except Exception as e:
                 log(f"Unexpected error processing item {item_path}: {e}", level=logging.ERROR)

        # Sort directories first, then files, alphabetically
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return items, None # Return items and no error

    except PermissionError:
        log(f"Permission denied listing directory: {validated_path}", level=logging.WARNING)
        return None, "Permission denied"
    except Exception as e:
        log(f"Error listing directory {validated_path}: {e}", level=logging.ERROR)
        return None, f"Error listing directory: {e}"

def get_file_content(requested_path):
    """Gets the content of a validated file path."""
    log(f"Attempting to get file content for path: {requested_path}", level=logging.DEBUG)

    validated_path, error = is_path_safe(requested_path)
    if error:
        return None, error # Return None for content and the error message

    if not os.path.isfile(validated_path):
         return None, "Path is not a file"

    # Basic check for potentially readable text extensions
    allowed_extensions = ('.txt', '.log', '.xml', '.ini', '.cfg', '.conf', '.json', '.yaml', '.yml', '.md')
    if not validated_path.lower().endswith(allowed_extensions):
         log(f"File content request denied for non-allowed extension: {validated_path}", level=logging.WARNING)
         return None, "File type not allowed for viewing."

    try:
        with open(validated_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Limit reading size? For now, read whole file.
            content = f.read()
        return content, None # Return content and no error
    except PermissionError:
        log(f"Permission denied reading file: {validated_path}", level=logging.WARNING)
        return None, "Permission denied"
    except Exception as e:
        log(f"Error reading file {validated_path}: {e}", level=logging.ERROR)
        return None, f"Error reading file: {e}"

def get_launchbox_base_path():
    """Returns the configured LaunchBox base path."""
    log("Getting LaunchBox base path", level=logging.DEBUG)
    return LAUNCHBOX_PATH

def create_temp_image_directory():
    """Creates the temporary image directory if it doesn't exist."""
    if not os.path.exists(temp_image_path):
        try:
            os.makedirs(temp_image_path)
            log(f"Created temporary image directory: {temp_image_path}")
        except OSError as e:
            log(f"Error creating temporary image directory {temp_image_path}: {e}", level=logging.ERROR)
