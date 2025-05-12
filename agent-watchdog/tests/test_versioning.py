import pytest
import subprocess
import sys
import os

# Define the path to the main watchdog script
WATCHDOG_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'agent_watchdog', 'main.py')

def test_version_flag():
    """
    Test that the --version flag prints the correct version and exits.
    """
    try:
        # Run the watchdog script with the --version flag
        result = subprocess.run(
            [sys.executable, WATCHDOG_SCRIPT, '--version'],
            capture_output=True,
            text=True,
            check=True
        )

        # Assert that the output contains the version string
        # We expect something like "Arcade Agent Watchdog 1.0.0\n"
        assert "Arcade Agent Watchdog 1.0.0" in result.stdout.strip()

        # Assert that there is no error output
        assert result.stderr == ""

    except subprocess.CalledProcessError as e:
        pytest.fail(f"Subprocess failed with exit code {e.returncode}. Stdout: {e.stdout}. Stderr: {e.stderr}")
    except FileNotFoundError:
        pytest.fail(f"Watchdog script not found at {WATCHDOG_SCRIPT}")

if __name__ == "__main__":
    test_version_flag()
    print("Test completed successfully.")