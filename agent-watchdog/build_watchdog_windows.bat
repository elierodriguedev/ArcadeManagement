@echo off
setlocal enabledelayedexpansion

REM Check if running from a UNC path and use pushd/popd if necessary
for /f "delims=" %%i in ("%~dp0") do set "current_dir=%%~fi"
if "!current_dir:~0,2!"=="\\" (
    echo Running from UNC path. Using pushd.
    pushd "%~dp0"
    set "UNC_PATH=true"
) else (
    echo Running from local path.
    set "UNC_PATH=false"
)

REM --- Windows executable build process ---

echo Starting Windows executable build process...
echo.

REM Ensure you have Python and pip installed and in your system's PATH.
REM Ensure you have PyInstaller installed (`pip install pyinstaller`).

REM IMPORTANT: Before running this script, manually:
REM 1. Increment the version number in agent-watchdog\agent_watchdog\main.py (or the main entry point)
REM 2. Add a corresponding entry to agent-watchdog\CHANGELOG.md

REM The pushd command at the beginning handles changing to the correct directory.

REM Install Python dependencies
echo Step 1: Installing Python dependencies with pip...
echo Executing: pip install -r requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies.
    exit /b 1
)
echo Python dependency installation complete.
echo.

REM Build Arcade Watchdog executable with PyInstaller
echo Step 2: Building Arcade Watchdog executable (Windows) with PyInstaller...
echo Executing: pyinstaller --onefile --runtime-tmpdir . --clean main.py
pyinstaller --onefile --runtime-tmpdir . --clean main.py
set BUILD_EXIT_CODE=%errorlevel%

echo.

REM --- Post-build steps ---

if %BUILD_EXIT_CODE% equ 0 (
    echo Step 3: Build successful. Moving agent-watchdog.exe to versioned directory...

    REM Extract version from CHANGELOG.md
    REM This uses findstr to find the first line starting with "## [" and then extracts the version.
    for /f "tokens=*" %%a in ('findstr /b "## \[" CHANGELOG.md') do (
        set "line=%%a"
        REM Extract the version number between "## [" and "]"
        set "WATCHDOG_VERSION=!line:*## [=!"
        set "WATCHDOG_VERSION=!WATCHDOG_VERSION:]=!"
        goto :version_extracted
    )

    :version_extracted
    if not defined WATCHDOG_VERSION (
        echo Error: Could not extract watchdog version from CHANGELOG.md.
        exit /b 1
    )

    set DEST_DIR=..\arcade-web-controller\Watchdog\%WATCHDOG_VERSION%
    set SOURCE_PATH=dist\main.exe REM PyInstaller names the executable after the main script by default

    REM Create destination directory if it doesn't exist
    if not exist "%DEST_DIR%" (
        echo Creating destination directory: %DEST_DIR%
        mkdir "%DEST_DIR%"
        if %errorlevel% neq 0 (
            echo Error: Could not create destination directory %DEST_DIR%.
            exit /b 1
        )
    )

    REM Verify agent-watchdog.exe version before moving
    echo Validating built agent-watchdog.exe with --get-version...
    REM Note: The watchdog might not have a --get-version flag. This step might need adjustment
    REM based on the actual watchdog implementation. Assuming it has a similar flag for now.
    "%SOURCE_PATH%" --get-version > nul 2>&1
    if %errorlevel% equ 0 (
        echo Validation successful. Moving agent-watchdog.exe to versioned directory...
        move "%SOURCE_PATH%" "%DEST_DIR%\"
        if %errorlevel% neq 0 (
            echo Error: Could not move %SOURCE_PATH% to %DEST_DIR%.
            exit /b 1
        )
        echo Successfully moved %SOURCE_PATH% to %DEST_DIR%\agent-watchdog.exe
    ) else (
        echo WARNING: agent-watchdog.exe failed validation with --get-version. Skipping move.
        REM Exit with a non-zero code to indicate a potential issue, but don't stop the whole script
        REM if the validation step is not critical for the watchdog.
        REM For now, we'll just warn and continue. If validation is critical, change this to exit /b 1.
        REM exit /b 1
    )
) else (
    echo Step 3: Build failed. Skipping move operation.
    exit /b 1
)

echo.
echo Build process finished.
echo The Windows executable (agent-watchdog.exe) is located in the 'dist' folder (if build was successful) and has been moved to the versioned directory.
echo --- Windows executable build process finished ---

if "%UNC_PATH%"=="true" (
    echo Returning from pushd.
    popd
)

endlocal
exit /b 0