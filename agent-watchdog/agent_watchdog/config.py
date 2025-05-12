import os

class Config:
    """
    Configuration class for the Agent Watchdog.
    Loads settings from environment variables or a configuration file.
    """
    def __init__(self):
        # TDD Anchor: Add test for loading configuration from environment variables
        self.agent_download_url = os.getenv("AGENT_DOWNLOAD_URL", "https://arcade.elierodrigue.cloud/api/agent/download/latest")
        self.agent_version_check_url = os.getenv("AGENT_VERSION_CHECK_URL", "https://arcade.elierodrigue.cloud/api/agent/latest_version")
        # TDD Anchor: Add test for loading configuration from a file (if implemented)

    def get_agent_download_url(self):
        """Returns the URL for downloading the agent."""
        return self.agent_download_url

    def get_agent_version_check_url(self):
        """Returns the URL for checking the latest agent version."""
        return self.agent_version_check_url

# Example usage (for testing purposes)
if __name__ == "__main__":
    config = Config()
    print(f"Agent Download URL: {config.get_agent_download_url()}")
    print(f"Agent Version Check URL: {config.get_agent_version_check_url()}")