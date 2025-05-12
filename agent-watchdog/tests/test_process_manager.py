import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Assuming process_manager.py is in the parent directory of tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process_manager import is_agent_running, start_agent, kill_agent

class TestProcessManager(unittest.TestCase):

    @patch('process_manager.subprocess.run')
    def test_is_agent_running_success(self, mock_run):
        # Mock a successful process listing that includes agent.exe
        mock_run.return_value = MagicMock(stdout="tasklist output including agent.exe", returncode=0)
        self.assertTrue(is_agent_running())
        mock_run.assert_called_once()

    @patch('process_manager.subprocess.run')
    def test_is_agent_running_not_running(self, mock_run):
        # Mock a successful process listing that does not include agent.exe
        mock_run.return_value = MagicMock(stdout="tasklist output without agent.exe", returncode=0)
        self.assertFalse(is_agent_running())
        mock_run.assert_called_once()

    @patch('process_manager.subprocess.run')
    def test_is_agent_running_error(self, mock_run):
        # Mock an error during process listing
        mock_run.return_value = MagicMock(stdout="", stderr="Error listing processes", returncode=1)
        self.assertFalse(is_agent_running())
        mock_run.assert_called_once()

    @patch('process_manager.subprocess.Popen')
    @patch('process_manager.os.path.exists', return_value=True)
    def test_start_agent_success(self, mock_exists, mock_popen):
        # Mock successful agent startup
        mock_popen.return_value = MagicMock() # Mock the Popen object
        self.assertTrue(start_agent())
        mock_exists.assert_called_once_with('agent.exe')
        mock_popen.assert_called_once_with(['agent.exe'], creationflags=unittest.mock.ANY) # Check for the command and flags

    @patch('process_manager.os.path.exists', return_value=False)
    def test_start_agent_not_found(self, mock_exists):
        # Mock agent.exe not found
        self.assertFalse(start_agent())
        mock_exists.assert_called_once_with('agent.exe')

    @patch('process_manager.subprocess.Popen')
    @patch('process_manager.os.path.exists', return_value=True)
    def test_start_agent_popen_error(self, mock_exists, mock_popen):
        # Mock an error during Popen call
        mock_popen.side_effect = Exception("Popen failed")
        self.assertFalse(start_agent())
        mock_exists.assert_called_once_with('agent.exe')
        mock_popen.assert_called_once_with(['agent.exe'], creationflags=unittest.mock.ANY)

    @patch('process_manager.subprocess.run')
    def test_kill_agent_success(self, mock_run):
        # Mock successful agent killing
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(kill_agent())
        mock_run.assert_called_once_with(['taskkill', '/F', '/IM', 'agent.exe'], capture_output=True, text=True)

    @patch('process_manager.subprocess.run')
    def test_kill_agent_not_running(self, mock_run):
        # Mock taskkill failing because process not found
        mock_run.return_value = MagicMock(returncode=1, stderr="ERROR: The process \"agent.exe\" not found.")
        self.assertFalse(kill_agent())
        mock_run.assert_called_once_with(['taskkill', '/F', '/IM', 'agent.exe'], capture_output=True, text=True)

    @patch('process_manager.subprocess.run')
    def test_kill_agent_error(self, mock_run):
        # Mock an unexpected error during taskkill
        mock_run.return_value = MagicMock(returncode=1, stderr="Some other error")
        self.assertFalse(kill_agent())
        mock_run.assert_called_once_with(['taskkill', '/F', '/IM', 'agent.exe'], capture_output=True, text=True)

if __name__ == '__main__':
    unittest.main()