import unittest
from unittest.mock import patch, mock_open
import os

# Assuming config.py is in the parent directory of tests
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        # Ensure no config file exists before each test
        if os.path.exists('config.json'):
            os.remove('config.json')

    def tearDown(self):
        # Clean up any created config file after each test
        if os.path.exists('config.json'):
            os.remove('config.json')

    # The Config class loads from environment variables, not a file directly in __init__
    # This test needs to be updated to reflect the actual Config class behavior
    # It should test loading from environment variables.
    @patch.dict(os.environ, {'AGENT_DOWNLOAD_URL': 'http://env_agent', 'AGENT_VERSION_CHECK_URL': 'http://env_controller'})
    def test_config_loads_from_env(self):
        config = Config()
        self.assertEqual(config.get_agent_download_url(), "http://env_agent")
        self.assertEqual(config.get_agent_version_check_url(), "http://env_controller")

    # This test is no longer relevant as Config loads from env vars, not a file
    pass

    # Update test to use the Config class and its methods
    @patch.dict(os.environ, {'AGENT_DOWNLOAD_URL': 'http://env_agent'})
    def test_get_agent_download_url_from_env(self):
        config = Config()
        url = config.get_agent_download_url()
        self.assertEqual(url, "http://env_agent")

    # Update test to use the Config class and its methods
    @patch.dict(os.environ, {'AGENT_VERSION_CHECK_URL': 'http://env_controller'})
    def test_get_agent_version_check_url_from_env(self):
        config = Config()
        url = config.get_agent_version_check_url()
        self.assertEqual(url, "http://env_controller")

    # Update test to use the Config class and its methods
    @patch.dict(os.environ, {}, clear=True) # Ensure env vars are clear
    def test_get_agent_version_check_url_default(self):
        config = Config()
        url = config.get_agent_version_check_url()
        self.assertEqual(url, "https://arcade.elierodrigue.cloud/Agent/latest/version.txt")

    # Update test to use the Config class and its methods
    @patch.dict(os.environ, {}, clear=True) # Ensure env vars are clear
    def test_get_agent_download_url_default(self):
        config = Config()
        url = config.get_agent_download_url()
        self.assertEqual(url, "https://arcade.elierodrigue.cloud/api/agent/download/latest")

    # This test is no longer relevant as Config loads from env vars, not a file
    pass

    # This test is no longer relevant as Config loads from env vars, not a file
    pass

if __name__ == '__main__':
    unittest.main()