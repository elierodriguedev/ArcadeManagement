# Remove build directory if it exists
$buildDir = Join-Path $PSScriptRoot "build"
if (Test-Path $buildDir) {
    Write-Host "Removing existing build directory: $buildDir"
    Remove-Item $buildDir -Recurse -Force
}
# --- Windows executable build process (PowerShell) ---

Write-Host "Starting Windows executable build process..."
Write-Host ""

# Ensure you have Python and pip installed and in your system's PATH.
# Ensure you have Node.js and npm installed and in your system's PATH.
# Ensure you have PyInstaller installed (`pip install pyinstaller`).

# IMPORTANT: Before running this script, manually:
# 1. Increment the version number in arcade-agent\agent.py
# 2. Add a corresponding entry to arcade-agent\CHANGELOG.md

# Check if running from a UNC path and use Push-Location/Pop-Location if necessary
# Use $PSScriptRoot to get the actual script directory, even if the initial working directory is different
$scriptDir = $PSScriptRoot
if ($scriptDir.StartsWith("\\")) {
    Write-Host "Running from UNC path. Using Push-Location."
    Push-Location $scriptDir
    $UNC_PATH = $true
} else {
    Write-Host "Running from local path."
    $UNC_PATH = $false
}

# Change to the arcade-agent directory
# The Push-Location command at the beginning handles changing to the correct directory.
# Set-Location arcade-agent # Removed as Push-Location handles this

# Build React UI
Write-Host "Step 1: Building React UI..."
if ($UNC_PATH) {
    Write-Host "Running from UNC path, skipping React UI build. Ensure React UI is built separately from a local path."
    $REACT_BUILD_EXIT_CODE = 0
} else {
    Write-Host "Executing: npm run build in react-ui directory"
    Push-Location (Join-Path $PSScriptRoot "react-ui")
    npm run build
    $REACT_BUILD_EXIT_CODE = $LASTEXITCODE
    Pop-Location
    Write-Host "React UI build command finished with exit code $REACT_BUILD_EXIT_CODE."
    Write-Host "React UI build complete."
    Write-Host ""
}

# Check if React build was successful
if ($REACT_BUILD_EXIT_CODE -eq 0) {
    Write-Host "React UI build successful. Proceeding with Python dependencies and PyInstaller build."
    Write-Host ""

    # Install Python dependencies
    Write-Host "Step 2: Installing Python dependencies with pip..."
    Write-Host "Executing: pip install -r requirements.txt"
    pip install -r (Join-Path $PSScriptRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install Python dependencies."
        exit 1
    }
    Write-Host "Python dependency installation complete."
    Write-Host ""

    # Build Arcade Agent executable with PyInstaller
    Write-Host "Step 3: Building Arcade Agent executable (Windows) with PyInstaller..."
    # Note: Paths in --add-data need to be Windows paths relative to the script's execution location.
    Write-Host "Executing: pyinstaller --onefile --add-data 'templates;templates' --add-data 'build\react_ui_dist;static\react' --runtime-tmpdir . --clean agent.py"
    pyinstaller --onefile --hidden-import api_routes --add-data (Join-Path $PSScriptRoot "build\react_ui_dist;static\react") --runtime-tmpdir . --clean --distpath (Join-Path $PSScriptRoot "dist") --workpath (Join-Path $PSScriptRoot "build") (Join-Path $PSScriptRoot "agent.py")
    $BUILD_EXIT_CODE = $LASTEXITCODE

    Write-Host ""

    # --- Post-build steps ---

    if ($BUILD_EXIT_CODE -eq 0) {
        Write-Host "Step 4: Build successful. Moving agent.exe to versioned directory..."

        # Extract version from CHANGELOG.md
        # This uses Select-String to find the first line starting with "## [" and then extracts the version.
        $line = Get-Content (Join-Path $PSScriptRoot "CHANGELOG.md") | Select-String -Pattern "## \[" | Select-Object -First 1
        if ($line) {
            $AGENT_VERSION = $line.ToString() -replace ".*## \[(.*)\].*", '$1'
        }

        if (-not $AGENT_VERSION) {
            Write-Host "Error: Could not extract agent version from CHANGELOG.md."
            exit 1
        }

        $DEST_DIR = "\\poweredge.local\Projets\Studio Code\ArcadeProject\arcade-web-controller\agent\$AGENT_VERSION"
        $SOURCE_PATH = Join-Path $PSScriptRoot "dist\agent.exe"

        # Create destination directory if it doesn't exist
        if (-not (Test-Path $DEST_DIR)) {
            Write-Host "Creating destination directory: $DEST_DIR"
            New-Item -ItemType Directory -Path $DEST_DIR | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error: Could not create destination directory $DEST_DIR."
                exit 1
            }
        }

        # Verify agent.exe version before moving
        Write-Host "Validating built agent.exe with --get-version..."
        & "$SOURCE_PATH" --get-version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Validation successful. Moving agent.exe to versioned directory..."
            Move-Item $SOURCE_PATH $DEST_DIR -Force
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error: Could not move $SOURCE_PATH to $DEST_DIR."
                exit 1
            }
            Write-Host "Successfully moved $SOURCE_PATH to $DEST_DIR\agent.exe"
        } else {
            Write-Host "ERROR: agent.exe failed validation with --get-version. Skipping move."
            exit 1
        }
    } else {
        Write-Host "Step 4: Build failed. Skipping move operation."
        exit 1
    }

    Write-Host ""
    Write-Host "Build process finished."
    Write-Host "The Windows executable (agent.exe) is located in the 'dist' folder (if build was successful) and has been moved to the versioned directory."
    Write-Host "--- Windows executable build process finished ---"
} else {
    Write-Host "React UI build failed. Skipping Python dependencies and PyInstaller build."
    exit 1
}

if ($UNC_PATH) {
    Write-Host "Returning from Push-Location."
    Pop-Location
}

exit 0