class SonarSystem:
    """System resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the System resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection
    
    def sites(self):
        """
        Get system sites.
        
        :return: API response containing system sites
        """
        return self.connection.get("/system/sites")

