class SonarHttp:
    """HTTP checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the HTTP checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection

