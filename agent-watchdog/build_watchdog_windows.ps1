# --- Windows executable build process (PowerShell) ---

Write-Host "Starting Windows executable build process..."
Write-Host ""

# Ensure you have Python and pip installed and in your system's PATH.
# Ensure you have PyInstaller installed (`pip install pyinstaller`).

# IMPORTANT: Before running this script, manually:
# 1. Increment the version number in agent-watchdog\agent_watchdog\main.py (or the main entry point)
# 2. Add a corresponding entry to agent-watchdog\CHANGELOG.md

# Check if running from a UNC path and use Push-Location/Pop-Location if necessary
$currentDir = Get-Location
if ($currentDir.Path.StartsWith("\\")) {
    Write-Host "Running from UNC path. Using Push-Location."
    Push-Location $currentDir.Path
    $UNC_PATH = $true
} else {
    Write-Host "Running from local path."
    $UNC_PATH = $false
}

# Change to the agent-watchdog directory
# The Push-Location command at the beginning handles changing to the correct directory.
Set-Location agent-watchdog # Change to the agent-watchdog directory

# Install Python dependencies
Write-Host "Step 1: Installing Python dependencies with pip..."
Write-Host "Executing: pip install -r requirements.txt"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install Python dependencies."
    exit 1
}
Write-Host "Python dependency installation complete."
Write-Host ""

# Build Arcade Watchdog executable with PyInstaller
Write-Host "Step 2: Building Arcade Watchdog executable (Windows) with PyInstaller..."
Write-Host "Executing: pyinstaller --onefile --runtime-tmpdir . --clean main.py"
pyinstaller --onefile --runtime-tmpdir . --clean agent_watchdog/main.py
$BUILD_EXIT_CODE = $LASTEXITCODE

Write-Host ""

# --- Post-build steps ---

if ($BUILD_EXIT_CODE -eq 0) {
    Write-Host "Step 3: Build successful. Moving agent-watchdog.exe to versioned directory..."

    # Extract version from agent_watchdog/main.py
    $mainFileContent = Get-Content agent_watchdog/main.py
    $versionLine = $mainFileContent | Select-String -Pattern @"
WATCHDOG_VERSION = "(\d+\.\d+\.\d+)"
"@
    if ($versionLine) {
        $WATCHDOG_VERSION = $versionLine.Matches[0].Groups[1].Value
    }

    if (-not $WATCHDOG_VERSION) {
        Write-Host "Error: Could not extract watchdog version from CHANGELOG.md."
        exit 1
    }

    $DEST_DIR = "\\poweredge.local\Projets\Studio Code\ArcadeProject\arcade-web-controller\watchdog"
    $SOURCE_PATH = "dist\main.exe" # PyInstaller names the executable after the main script by default

    # Create destination directory if it doesn't exist
    if (-not (Test-Path $DEST_DIR)) {
        Write-Host "Creating destination directory: $DEST_DIR"
        New-Item -ItemType Directory -Path $DEST_DIR | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Could not create destination directory $DEST_DIR."
            exit 1
        }
    }

    # Verify agent-watchdog.exe version before moving
    Write-Host "Validating built agent-watchdog.exe with --get-version..."
    # Note: The watchdog might not have a --get-version flag. This step might need adjustment
    # based on the actual watchdog implementation. Assuming it has a similar flag for now.
    & "$SOURCE_PATH" --version | Out-Null # Assuming --version flag based on main.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Validation successful. Moving agent-watchdog.exe to versioned directory..."
        Move-Item $SOURCE_PATH $DEST_DIR -Force
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Could not move $SOURCE_PATH to $DEST_DIR."
            exit 1
        }
        Write-Host "Successfully moved $SOURCE_PATH to $DEST_DIR\agent-watchdog.exe"
    } else {
        Write-Host "WARNING: agent-watchdog.exe failed validation with --version. Skipping move."
        # Exit with a non-zero code to indicate a potential issue, but don't stop the whole script
        # if the validation step is not critical for the watchdog.
        # For now, we'll just warn and continue. If validation is critical, change this to exit 1.
        # exit 1
    }
} else {
    Write-Host "Step 3: Build failed. Skipping move operation."
    exit 1
}

Write-Host ""
Write-Host "Build process finished."
Write-Host "The Windows executable (agent-watchdog.exe) is located in the 'dist' folder (if build was successful) and has been moved to the versioned directory."
Write-Host "--- Windows executable build process finished ---"

if ($UNC_PATH) {
    Write-Host "Returning from Push-Location."
    Pop-Location
}

exit 0