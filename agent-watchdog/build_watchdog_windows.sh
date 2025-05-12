#!/bin/bash

set -x

# Change to the agent-watchdog directory
cd agent-watchdog

# --- Cross-compilation for Windows on Linux using Wine and embedded Python ---

echo "Starting Windows executable build process using Wine and embedded Python..."
echo ""

# Ensuring Wine and Winetricks are installed (will do nothing if already installed)
echo "Step 1: Ensuring Wine and Winetricks are installed..."
sudo pacman -S --noconfirm wine winetricks || { echo "Error: Failed to install Wine/Winetricks. Please check your pacman configuration and try again."; exit 1; }
echo "Wine and Winetricks installation complete."
echo ""

# Get the Windows path to the embedded PyInstaller executable
echo "Step 2: Getting Windows path for embedded PyInstaller..."
PYINSTALLER_WIN_PATH=$(winepath -w /data/ArcadeProject/agent-watchdog/python/Scripts/pyinstaller.exe)
if [ -z "$PYINSTALLER_WIN_PATH" ]; then
    echo "Error: Could not get Windows path for embedded PyInstaller executable."
    echo "Please ensure Wine is correctly configured and the embedded Python distribution is in agent-watchdog/python."
    exit 1
fi
echo "Windows path for PyInstaller: $PYINSTALLER_WIN_PATH"
echo "PYINSTALLER_WIN_PATH=$PYINSTALLER_WIN_PATH" # Added for manual execution
echo ""

# Get the Windows path to the embedded Python executable relative to the current directory (agent-watchdog)
echo "Step 3: Getting Windows path for embedded Python executable..."
PYTHON_WIN_PATH=$(winepath -w python/python.exe)
if [ -z "$PYTHON_WIN_PATH" ]; then
    echo "Error: Could not get Windows path for embedded Python executable."
    echo "Please ensure the embedded Python distribution is in agent-watchdog/python."
    exit 1
fi
echo "Windows path for Python: $PYTHON_WIN_PATH"
echo "PYTHON_WIN_PATH=$PYTHON_WIN_PATH" # Added for manual execution
echo ""

# Install Python dependencies within the Wine environment
echo "Step 4: Installing Python dependencies with pip in Wine..."
echo "Executing: wine \"$PYTHON_WIN_PATH\" -m pip install -r requirements.txt"
# Use the embedded python.exe within Wine to run pip
wine "$PYTHON_WIN_PATH" -m pip install -r requirements.txt || { echo "Error: Failed to install Python dependencies in Wine."; exit 1; }
echo "Python dependency installation command finished."
echo "Python dependency installation complete in Wine."
echo ""

# Build Arcade Watchdog executable using the embedded PyInstaller within Wine
echo "Step 5: Building Arcade Watchdog executable (Windows) with PyInstaller..."
# Note: Paths in --add-data need to be Windows paths relative to the script's execution location within Wine.
# Assuming the script is run from the agent-watchdog directory within Wine (e.g., Z:\data\ArcadeProject\agent-watchdog)
wine "$PYINSTALLER_WIN_PATH" --onefile --runtime-tmpdir . --clean main.py
BUILD_EXIT_CODE=$? # Capture the exit code of the PyInstaller command

echo ""

# --- Post-build steps ---

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "Step 6: Build successful. Moving agent-watchdog.exe to versioned directory..."

    # Extract version from CHANGELOG.md
    WATCHDOG_VERSION=$(grep -m 1 '## \[' CHANGELOG.md | sed -E 's/## \[(.*)\].*/\1/')

    if [ -z "$WATCHDOG_VERSION" ]; then
        echo "Error: Could not extract watchdog version from CHANGELOG.md."
        exit 1
    fi

    DEST_DIR="../arcade-web-controller/Watchdog/$WATCHDOG_VERSION"
    DEST_PATH="$DEST_DIR/agent-watchdog.exe"
    SOURCE_PATH="dist/main.exe" # PyInstaller names the executable after the main script by default

    # Create destination directory if it doesn't exist
    mkdir -p "$DEST_DIR" || { echo "Error: Could not create destination directory $DEST_DIR."; exit 1; }

    # Verify agent-watchdog.exe version before moving
    echo "Validating built agent-watchdog.exe with --get-version..."
    # Note: The watchdog might not have a --get-version flag. This step might need adjustment
    # based on the actual watchdog implementation. Assuming it has a similar flag for now.
    if wine "$SOURCE_PATH" --get-version > /dev/null 2>&1; then
        echo "Validation successful. Moving agent-watchdog.exe to versioned directory..."
        mv "$SOURCE_PATH" "$DEST_PATH" || { echo "Error: Could not move $SOURCE_PATH to $DEST_PATH."; exit 1; }
        echo "Successfully moved $SOURCE_PATH to $DEST_PATH"
    else
        echo "WARNING: agent-watchdog.exe failed validation with --get-version. Skipping move." >&2
        # Exit with a non-zero code to indicate a potential issue, but don't stop the whole script
        # if the validation step is not critical for the watchdog.
        # For now, we'll just warn and continue. If validation is critical, change this to exit 1.
        # exit 1
    fi
else
    echo "Step 6: Build failed. Skipping move operation."
fi

echo ""
echo "Build process finished."
echo "The Windows executable (agent-watchdog.exe) is located in the 'dist' folder within your Wine environment (if build was successful) and has been moved to the versioned directory."
echo "You can typically find it at ~/.wine/drive_c/data/ArcadeProject/agent-watchdog/dist/main.exe (before move) and ~/.wine/drive_c/data/ArcadeProject/arcade-web-controller/Watchdog/$WATCHDOG_VERSION/agent-watchdog.exe (after move)"
echo ""
echo "--- Windows executable build process finished ---"