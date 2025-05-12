import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Assuming update_checker.py is in the parent directory of tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from update_checker import get_installed_version, get_latest_online_version, is_update_available, trigger_update_sequence

class TestUpdateChecker(unittest.TestCase):

    @patch('update_checker.subprocess.run')
    def test_get_installed_version_success(self, mock_run):
        # Mock a successful command execution returning a version
        mock_run.return_value = MagicMock(stdout="2.1.0\n", returncode=0)
        version = get_installed_version()
        self.assertEqual(version, "2.1.0")
        mock_run.assert_called_once_with(['agent.exe', '--version'], capture_output=True, text=True)

    @patch('update_checker.subprocess.run')
    def test_get_installed_version_agent_not_found(self, mock_run):
        # Mock command execution failing (e.g., agent.exe not found)
        mock_run.side_effect = FileNotFoundError
        version = get_installed_version()
        self.assertIsNone(version)
        mock_run.assert_called_once_with(['agent.exe', '--version'], capture_output=True, text=True)

    @patch('update_checker.subprocess.run')
    def test_get_installed_version_command_error(self, mock_run):
        # Mock command execution returning an error code
        mock_run.return_value = MagicMock(stdout="", stderr="Error executing command", returncode=1)
        version = get_installed_version()
        self.assertIsNone(version)
        mock_run.assert_called_once_with(['agent.exe', '--version'], capture_output=True, text=True)

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_get_latest_online_version_success(self, mock_get_controller_url, mock_requests_get):
        # Mock a successful API call returning a version
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"latest_version": "2.2.0"}
        mock_requests_get.return_value = mock_response

        version = get_latest_online_version()
        self.assertEqual(version, "2.2.0")
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/latest_agent_version")

    @patch('update_checker.get_controller_url', return_value=None)
    def test_get_latest_online_version_no_controller_url(self, mock_get_controller_url):
        # Mock no controller URL being available
        version = get_latest_online_version()
        self.assertIsNone(version)
        mock_get_controller_url.assert_called_once()

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_get_latest_online_version_api_error(self, mock_get_controller_url, mock_requests_get):
        # Mock an error during the API call
        mock_requests_get.side_effect = Exception("Network error")
        version = get_latest_online_version()
        self.assertIsNone(version)
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/latest_agent_version")

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_get_latest_online_version_api_non_200(self, mock_get_controller_url, mock_requests_get):
        # Mock API returning a non-200 status code
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        version = get_latest_online_version()
        self.assertIsNone(version)
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/latest_agent_version")

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_get_latest_online_version_api_invalid_json(self, mock_get_controller_url, mock_requests_get):
        # Mock API returning invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_requests_get.return_value = mock_response

        version = get_latest_online_version()
        self.assertIsNone(version)
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/latest_agent_version")

    def test_is_update_available_true(self):
        self.assertTrue(is_update_available("2.1.0", "2.2.0"))

    def test_is_update_available_false_same_version(self):
        self.assertFalse(is_update_available("2.1.0", "2.1.0"))

    def test_is_update_available_false_newer_installed(self):
        self.assertFalse(is_update_available("2.2.0", "2.1.0"))

    def test_is_update_available_false_invalid_installed(self):
        self.assertFalse(is_update_available("invalid", "2.2.0"))

    def test_is_update_available_false_invalid_latest(self):
        self.assertFalse(is_update_available("2.1.0", "invalid"))

    def test_is_update_available_false_none_installed(self):
        self.assertFalse(is_update_available(None, "2.2.0"))

    def test_is_update_available_false_none_latest(self):
        self.assertFalse(is_update_available("2.1.0", None))

    @patch('update_checker.kill_agent', return_value=True)
    @patch('update_checker.download_latest_agent', return_value=True)
    @patch('update_checker.start_agent', return_value=True)
    def test_trigger_update_sequence_success(self, mock_start_agent, mock_download, mock_kill_agent):
        self.assertTrue(trigger_update_sequence())
        mock_kill_agent.assert_called_once()
        mock_download.assert_called_once()
        mock_start_agent.assert_called_once()

    @patch('update_checker.kill_agent', return_value=False)
    @patch('update_checker.download_latest_agent')
    @patch('update_checker.start_agent')
    def test_trigger_update_sequence_kill_failed(self, mock_start_agent, mock_download, mock_kill_agent):
        self.assertFalse(trigger_update_sequence())
        mock_kill_agent.assert_called_once()
        mock_download.assert_not_called()
        mock_start_agent.assert_not_called()

    @patch('update_checker.kill_agent', return_value=True)
    @patch('update_checker.download_latest_agent', return_value=False)
    @patch('update_checker.start_agent')
    def test_trigger_update_sequence_download_failed(self, mock_start_agent, mock_download, mock_kill_agent):
        self.assertFalse(trigger_update_sequence())
        mock_kill_agent.assert_called_once()
        mock_download.assert_called_once()
        mock_start_agent.assert_not_called()

    @patch('update_checker.kill_agent', return_value=True)
    @patch('update_checker.download_latest_agent', return_value=True)
    @patch('update_checker.start_agent', return_value=False)
    def test_trigger_update_sequence_start_failed(self, mock_start_agent, mock_download, mock_kill_agent):
        self.assertFalse(trigger_update_sequence())
        mock_kill_agent.assert_called_once()
        mock_download.assert_called_once()
        mock_start_agent.assert_called_once()

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    @patch('update_checker.open', new_callable=mock_open)
    @patch('update_checker.os.rename')
    @patch('update_checker.os.remove')
    @patch('update_checker.os.path.exists', side_effect=[True, True]) # agent.exe exists, agent.exe.temp exists
    def test_download_latest_agent_success(self, mock_exists, mock_remove, mock_rename, mock_file, mock_get_controller_url, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake agent executable content"
        mock_requests_get.return_value = mock_response

        self.assertTrue(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)
        mock_file.assert_called_once_with('agent.exe.temp', 'wb')
        mock_file().write.assert_called_once_with(b"fake agent executable content")
        mock_exists.assert_any_call('agent.exe')
        mock_exists.assert_any_call('agent.exe.temp')
        mock_remove.assert_called_once_with('agent.exe')
        mock_rename.assert_called_once_with('agent.exe.temp', 'agent.exe')

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    @patch('update_checker.open', new_callable=mock_open)
    @patch('update_checker.os.rename')
    @patch('update_checker.os.remove')
    @patch('update_checker.os.path.exists', side_effect=[True, False]) # agent.exe exists, agent.exe.temp does not exist initially
    def test_download_latest_agent_success_no_temp_initially(self, mock_exists, mock_remove, mock_rename, mock_file, mock_get_controller_url, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake agent executable content"
        mock_requests_get.return_value = mock_response

        self.assertTrue(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)
        mock_file.assert_called_once_with('agent.exe.temp', 'wb')
        mock_file().write.assert_called_once_with(b"fake agent executable content")
        mock_exists.assert_any_call('agent.exe')
        mock_exists.assert_any_call('agent.exe.temp')
        mock_remove.assert_called_once_with('agent.exe')
        mock_rename.assert_called_once_with('agent.exe.temp', 'agent.exe')


    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value=None)
    def test_download_latest_agent_no_controller_url(self, mock_get_controller_url, mock_requests_get):
        self.assertFalse(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_not_called()

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_download_latest_agent_api_error(self, mock_get_controller_url, mock_requests_get):
        mock_requests_get.side_effect = Exception("Network error")
        self.assertFalse(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    def test_download_latest_agent_api_non_200(self, mock_get_controller_url, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        self.assertFalse(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    @patch('update_checker.open', new_callable=mock_open)
    @patch('update_checker.os.rename')
    @patch('update_checker.os.remove')
    @patch('update_checker.os.path.exists', side_effect=[True, True]) # agent.exe exists, agent.exe.temp exists
    def test_download_latest_agent_write_error(self, mock_exists, mock_remove, mock_rename, mock_file, mock_get_controller_url, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake agent executable content"
        mock_requests_get.return_value = mock_response
        mock_file.side_effect = Exception("Write error")

        self.assertFalse(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)
        mock_file.assert_called_once_with('agent.exe.temp', 'wb')
        mock_remove.assert_not_called()
        mock_rename.assert_not_called()

    @patch('update_checker.requests.get')
    @patch('update_checker.get_controller_url', return_value="http://localhost:8000")
    @patch('update_checker.open', new_callable=mock_open)
    @patch('update_checker.os.rename')
    @patch('update_checker.os.remove')
    @patch('update_checker.os.path.exists', side_effect=[True, True]) # agent.exe exists, agent.exe.temp exists
    def test_download_latest_agent_rename_error(self, mock_exists, mock_remove, mock_rename, mock_file, mock_get_controller_url, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake agent executable content"
        mock_requests_get.return_value = mock_response
        mock_rename.side_effect = Exception("Rename error")

        self.assertFalse(trigger_update_sequence()) # trigger_update_sequence calls download_latest_agent
        mock_get_controller_url.assert_called_once()
        mock_requests_get.assert_called_once_with("http://localhost:8000/download_latest_agent", stream=True)
        mock_file.assert_called_once_with('agent.exe.temp', 'wb')
        mock_file().write.assert_called_once_with(b"fake agent executable content")
        mock_exists.assert_any_call('agent.exe')
        mock_exists.assert_any_call('agent.exe.temp')
        mock_remove.assert_called_once_with('agent.exe')
        mock_rename.assert_called_once_with('agent.exe.temp', 'agent.exe')


if __name__ == '__main__':
    unittest.main()