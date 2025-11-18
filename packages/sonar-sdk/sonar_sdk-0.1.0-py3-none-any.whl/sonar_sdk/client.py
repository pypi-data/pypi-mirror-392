from .connection import SonarConnection
from .system import SonarSystem
from .checks import SonarChecks
import importlib.metadata

class SonarClient:
    def __init__(self, api_key, secret_key):
        """
        Initialize the Sonar client wrapper.

        :param api_key: Sonar API key
        :param secret_key: Sonar secret key
        """
        self.connection = SonarConnection(api_key, secret_key)

        # Attach API Modules
        self.system = SonarSystem(self.connection)
        self.checks = SonarChecks(self.connection)
    
    def close_session(self):
        """Close the Sonar session by closing the connection."""
        return self.connection.close()

    def version(self):
        """
        Get the project information from package metadata.
        
        :return: Dictionary containing version, description, and project URL
        """
        metadata = importlib.metadata.metadata("sonar-sdk")
        
        return {
            "version": metadata["Version"],
            "description": metadata["Summary"],
            "project_url": metadata.get("Project-URL", "")
        }
