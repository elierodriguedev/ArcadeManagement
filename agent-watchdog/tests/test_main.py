import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import time

# Import the main script
import agent_watchdog.main as main

# Mock the necessary dependencies for WatchdogWorker
# Mock the necessary dependencies for WatchdogWorker
# Patching directly on the imported module 'main'
patch_watchdog_worker_dependencies = patch.multiple(
    'agent_watchdog.main',
    is_agent_running=MagicMock(),
    get_installed_agent_version=MagicMock(),
    get_latest_online_version=MagicMock(),
    trigger_update_sequence=MagicMock(),
    time=MagicMock(spec=time) # Mock time to control sleep
)

class TestWatchdogWorker(unittest.TestCase):

    def setUp(self):
        # Mock signals and config for the worker
        self.mock_signals = MagicMock()
        self.mock_config = MagicMock()
        self.worker = main.WatchdogWorker(self.mock_signals, self.mock_config)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_basic(self, is_agent_running, get_installed_agent_version,
                                   get_latest_online_version, trigger_update_sequence, time):
        # Configure mocks for a single loop iteration
        is_agent_running.return_value = True
        get_installed_agent_version.return_value = "1.0.0"
        get_latest_online_version.return_value = "1.0.0" # No update
        self.mock_config.get_agent_version_check_url.return_value = "http://testurl"

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert that the correct functions were called
        is_agent_running.assert_called_once()
        self.mock_signals.agent_status_updated.emit.assert_called_once_with(True)
        get_installed_agent_version.assert_called_once()
        self.mock_signals.current_version_updated.emit.assert_called_once_with("1.0.0")
        get_latest_online_version.assert_called_once_with("http://testurl")
        self.mock_signals.latest_version_updated.emit.assert_called_once_with("1.0.0")
        trigger_update_sequence.assert_not_called() # No update needed
        self.mock_signals.last_check_updated.emit.assert_called_once() # Check that emit was called, value is QDateTime
        time.sleep.assert_called_once_with(60)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_update_available(self, is_agent_running, get_installed_agent_version,
                                             get_latest_online_version, trigger_update_sequence, time):
        # Configure mocks for a single loop iteration with update
        is_agent_running.return_value = True
        get_installed_agent_version.return_value = "1.0.0"
        get_latest_online_version.return_value = "1.1.0" # Update available
        self.mock_config.get_agent_version_check_url.return_value = "http://testurl"

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert that the update sequence was triggered
        trigger_update_sequence.assert_called_once()
        time.sleep.assert_called_once_with(60)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_agent_not_running(self, is_agent_running, get_installed_agent_version,
                                              get_latest_online_version, trigger_update_sequence, time):
        # Configure mocks for agent not running
        is_agent_running.return_value = False
        get_installed_agent_version.return_value = "1.0.0"
        get_latest_online_version.return_value = "1.0.0"
        self.mock_config.get_agent_version_check_url.return_value = "http://testurl"

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert agent status signal was emitted correctly
        self.mock_signals.agent_status_updated.emit.assert_called_once_with(False)
        time.sleep.assert_called_once_with(60)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_get_installed_version_fails(self, is_agent_running, get_installed_agent_version,
                                                        get_latest_online_version, trigger_update_sequence, time):
        # Configure mocks for get_installed_agent_version failing
        is_agent_running.return_value = True
        get_installed_agent_version.return_value = None
        get_latest_online_version.return_value = "1.0.0"
        self.mock_config.get_agent_version_check_url.return_value = "http://testurl"

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert current version signal reflects unknown
        self.mock_signals.current_version_updated.emit.assert_called_once_with("Unknown")
        trigger_update_sequence.assert_not_called() # Cannot update if installed version is unknown
        time.sleep.assert_called_once_with(60)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_get_latest_version_fails(self, is_agent_running, get_installed_agent_version,
                                                     get_latest_online_version, trigger_update_sequence, time):
        # Configure mocks for get_latest_online_version failing
        is_agent_running.return_value = True
        get_installed_agent_version.return_value = "1.0.0"
        get_latest_online_version.return_value = None
        self.mock_config.get_agent_version_check_url.return_value = "http://testurl"

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert latest version signal reflects unknown
        self.mock_signals.latest_version_updated.emit.assert_called_once_with("Unknown")
        trigger_update_sequence.assert_not_called() # Cannot update if latest version is unknown
        time.sleep.assert_called_once_with(60)

    @patch_watchdog_worker_dependencies
    def test_worker_run_loop_exception_handling(self, is_agent_running, get_installed_agent_version,
                                               get_latest_online_version, trigger_update_sequence, time):
        # Configure mock to raise an exception
        is_agent_running.side_effect = Exception("Test Exception")

        # Set _is_running to False after the first sleep to exit the loop
        time.sleep.side_effect = lambda x: setattr(self.worker, '_is_running', False)

        self.worker.run()

        # Assert error signal was emitted
        self.mock_signals.error_occurred.emit.assert_called_once_with("Watchdog error: Test Exception")
        time.sleep.assert_called_once_with(60)

    def test_worker_stop(self):
        self.worker.stop()
        self.assertFalse(self.worker._is_running)

    # Note: Testing the main() function directly with unit tests is difficult
    # due to its reliance on QApplication and the GUI event loop.
    # Testing the WatchdogWorker class covers the core background logic.
    # Command-line argument parsing for --version is handled by agent.exe itself,
    # not the watchdog, so it's tested implicitly via get_installed_agent_version.

if __name__ == '__main__':
    unittest.main()