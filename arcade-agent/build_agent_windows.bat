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
REM Ensure you have Node.js and npm installed and in your system's PATH.
REM Ensure you have PyInstaller installed (`pip install pyinstaller`).

REM IMPORTANT: Before running this script, manually:
REM 1. Increment the version number in arcade-agent\agent.py
REM 2. Add a corresponding entry to arcade-agent\CHANGELOG.md

REM The pushd command at the beginning handles changing to the correct directory.

REM Build React UI
echo Step 1: Building React UI...
if "%UNC_PATH%"=="true" (
    echo Running from UNC path, skipping React UI build. Ensure React UI is built separately from a local path.
    set REACT_BUILD_EXIT_CODE=0
) else (
    echo Executing: cd react-ui && npm run build
    pushd "%~dp0\react-ui"
    npm run build
    set REACT_BUILD_EXIT_CODE=%errorlevel%
    popd
    echo React UI build command finished with exit code %REACT_BUILD_EXIT_CODE%.
    echo React UI build complete.
    echo.

    REM Check if React build was successful
    if %REACT_BUILD_EXIT_CODE% equ 0 (
    echo React UI build successful. Proceeding with Python dependencies and PyInstaller build.
    echo.

    REM Install Python dependencies
    echo Step 2: Installing Python dependencies with pip...
    echo Executing: pip install -r requirements.txt
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install Python dependencies.
        exit /b 1
    )
    echo Python dependency installation complete.
    echo.

    REM Build Arcade Agent executable with PyInstaller
    echo Step 3: Building Arcade Agent executable (Windows) with PyInstaller...
    REM Note: Paths in --add-data need to be Windows paths relative to the script's execution location.
    echo Executing: pyinstaller --onefile --add-data "templates;templates" --add-data "build\react_ui_dist;static\react" --runtime-tmpdir . --clean agent.py
    pyinstaller --onefile --add-data "templates;templates" --add-data "build\react_ui_dist;static\react" --runtime-tmpdir . --clean agent.py
    set BUILD_EXIT_CODE=%errorlevel%

    echo.

    REM --- Post-build steps ---

    if %BUILD_EXIT_CODE% equ 0 (
        echo Step 4: Build successful. Moving agent.exe to versioned directory...

        REM Extract version from CHANGELOG.md
        REM This uses findstr to find the first line starting with "## [" and then extracts the version.
        for /f "tokens=*" %%a in ('findstr /b "## \[" CHANGELOG.md') do (
            set "line=%%a"
            REM Extract the version number between "## [" and "]"
            set "AGENT_VERSION=!line:*## [=!"
            set "AGENT_VERSION=!AGENT_VERSION:]=!"
            goto :version_extracted
        )

        :version_extracted
        if not defined AGENT_VERSION (
            echo Error: Could not extract agent version from CHANGELOG.md.
            exit /b 1
        )

        set DEST_DIR=..\arcade-web-controller\Agent\%AGENT_VERSION%
        set SOURCE_PATH=dist\agent.exe

        REM Create destination directory if it doesn't exist
        if not exist "%DEST_DIR%" (
            echo Creating destination directory: %DEST_DIR%
            mkdir "%DEST_DIR%"
            if %errorlevel% neq 0 (
                echo Error: Could not create destination directory %DEST_DIR%.
                exit /b 1
            )
        )

        REM Verify agent.exe version before moving
        echo Validating built agent.exe with --get-version...
        "%SOURCE_PATH%" --get-version > nul 2>&1
        if %errorlevel% equ 0 (
            echo Validation successful. Moving agent.exe to versioned directory...
            move "%SOURCE_PATH%" "%DEST_DIR%\"
            if %errorlevel% neq 0 (
                echo Error: Could not move %SOURCE_PATH% to %DEST_DIR%.
                exit /b 1
            )
            echo Successfully moved %SOURCE_PATH% to %DEST_DIR%\agent.exe
        ) else (
            echo ERROR: agent.exe failed validation with --get-version. Skipping move.
            exit /b 1
        )
    ) else (
        echo Step 4: Build failed. Skipping move operation.
        exit /b 1
    )

    echo.
    echo Build process finished.
    echo The Windows executable (agent.exe) is located in the 'dist' folder (if build was successful) and has been moved to the versioned directory.
    echo --- Windows executable build process finished ---
) else (
    echo React UI build failed. Skipping Python dependencies and PyInstaller build.
    exit /b 1
)

if "%UNC_PATH%"=="true" (
    echo Returning from pushd.
    popd
)

endlocal
exit /b 0