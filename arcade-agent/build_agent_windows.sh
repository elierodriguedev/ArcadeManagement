#!/bin/bash

set -x

# Change to the arcade-agent directory
cd arcade-agent

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
PYINSTALLER_WIN_PATH=$(winepath -w /data/ArcadeProject/arcade-agent/python/Scripts/pyinstaller.exe)
if [ -z "$PYINSTALLER_WIN_PATH" ]; then
    echo "Error: Could not get Windows path for embedded PyInstaller executable."
    echo "Please ensure Wine is correctly configured and the embedded Python distribution is in arcade-agent/python."
    exit 1
fi
echo "Windows path for PyInstaller: $PYINSTALLER_WIN_PATH"
echo "PYINSTALLER_WIN_PATH=$PYINSTALLER_WIN_PATH" # Added for manual execution
echo ""

# Get the Windows path to the embedded Python executable relative to the current directory (arcade-agent)
echo "Step 3: Getting Windows path for embedded Python executable..."
PYTHON_WIN_PATH=$(winepath -w python/python.exe)
if [ -z "$PYTHON_WIN_PATH" ]; then
    echo "Error: Could not get Windows path for embedded Python executable."
    echo "Please ensure the embedded Python distribution is in arcade-agent/python."
    exit 1
fi
echo "Windows path for Python: $PYTHON_WIN_PATH"
echo "PYTHON_WIN_PATH=$PYTHON_WIN_PATH" # Added for manual execution
echo ""

# Build React UI
echo "Step 4: Building React UI..."
echo "Executing: cd react-ui && npm run build"
cd react-ui
npm run build
REACT_BUILD_EXIT_CODE=$?
cd ..
echo "React UI build command finished with exit code $REACT_BUILD_EXIT_CODE."
echo "React UI build complete."
echo ""

# Check if React build was successful
if [ $REACT_BUILD_EXIT_CODE -eq 0 ]; then
    echo "React UI build successful. Proceeding with Python dependencies and PyInstaller build."
    echo ""

    # Install Python dependencies within the Wine environment
    echo "Step 5: Installing Python dependencies with pip in Wine..."
    echo "Executing: wine \"$PYTHON_WIN_PATH\" -m pip install -r requirements.txt"
    # Use the embedded python.exe within Wine to run pip
    wine "$PYTHON_WIN_PATH" -m pip install -r requirements.txt || { echo "Error: Failed to install Python dependencies in Wine."; exit 1; }
    echo "Python dependency installation command finished."
    echo "Python dependency installation complete in Wine."
    echo ""

    # Build Arcade Agent executable using the embedded PyInstaller within Wine
    echo "Step 6: Building Arcade Agent executable (Windows) with PyInstaller..."
    # Note: Paths in --add-data need to be Windows paths relative to the script's execution location within Wine.
    # Assuming the script is run from the arcade-agent directory within Wine (e.g., Z:\data\ArcadeProject\arcade-agent)
    wine "$PYINSTALLER_WIN_PATH" --onefile --add-data "templates;templates" --add-data "build/react_ui_dist;static/react" --runtime-tmpdir . --clean agent.py
    BUILD_EXIT_CODE=$? # Capture the exit code of the PyInstaller command

    echo ""

    # --- Post-build steps ---

    if [ $BUILD_EXIT_CODE -eq 0 ]; then
        echo "Step 7: Build successful. Moving agent.exe to versioned directory..."

        # Extract version from CHANGELOG.md
        AGENT_VERSION=$(grep -m 1 '## \[' CHANGELOG.md | sed -E 's/## \[(.*)\].*/\1/')

        if [ -z "$AGENT_VERSION" ]; then
            echo "Error: Could not extract agent version from CHANGELOG.md."
            exit 1
        fi

        DEST_DIR="../arcade-web-controller/Agent/$AGENT_VERSION"
        DEST_PATH="$DEST_DIR/agent.exe"
        SOURCE_PATH="dist/agent.exe"

        # Create destination directory if it doesn't exist
        mkdir -p "$DEST_DIR" || { echo "Error: Could not create destination directory $DEST_DIR."; exit 1; }

        # Verify agent.exe version before moving
        echo "Validating built agent.exe with --get-version..."
        if wine "$SOURCE_PATH" --get-version > /dev/null 2>&1; then
            echo "Validation successful. Moving agent.exe to versioned directory..."
            mv "$SOURCE_PATH" "$DEST_PATH" || { echo "Error: Could not move $SOURCE_PATH to $DEST_PATH."; exit 1; }
            echo "Successfully moved $SOURCE_PATH to $DEST_PATH"
        else
            echo "ERROR: agent.exe failed validation with --get-version. Skipping move." >&2
            exit 1
        fi
    else
        echo "Step 7: Build failed. Skipping move operation."
    fi

    echo ""
    echo "Build process finished."
    echo "The Windows executable (agent.exe) is located in the 'dist' folder within your Wine environment (if build was successful) and has been moved to the versioned directory."
    echo "You can typically find it at ~/.wine/drive_c/data/ArcadeProject/arcade-agent/dist/agent.exe (before move) and ~/.wine/drive_c/data/ArcadeProject/arcade-web-controller/Agent/$AGENT_VERSION/agent.exe (after move)"
    echo ""
    echo "--- Windows executable build process finished ---"
fi
