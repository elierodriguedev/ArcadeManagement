import unittest
from PyQt6.QtCore import QObject, pyqtSignal

# Assuming watchdog_ui.py is in the parent directory of tests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from watchdog_ui import WatchdogSignals

class TestWatchdogSignals(unittest.TestCase):

    def test_signals_defined(self):
        """Test that the necessary signals are defined in WatchdogSignals."""
        signals = WatchdogSignals()

        self.assertTrue(hasattr(signals, 'agent_status_updated'))
        self.assertIsInstance(signals.agent_status_updated, pyqtSignal)

        self.assertTrue(hasattr(signals, 'current_version_updated'))
        self.assertIsInstance(signals.current_version_updated, pyqtSignal)

        self.assertTrue(hasattr(signals, 'latest_version_updated'))
        self.assertIsInstance(signals.latest_version_updated, pyqtSignal)

        self.assertTrue(hasattr(signals, 'last_check_updated'))
        self.assertIsInstance(signals.last_check_updated, pyqtSignal)

        self.assertTrue(hasattr(signals, 'error_occurred'))
        self.assertIsInstance(signals.error_occurred, pyqtSignal)

    # Note: Testing the emission and reception of signals typically requires
    # a running QApplication instance and event loop, which is beyond the
    # scope of simple unit tests without a GUI environment.
    # The primary testable aspect of WatchdogSignals is the definition of the signals themselves.

if __name__ == '__main__':
    unittest.main()