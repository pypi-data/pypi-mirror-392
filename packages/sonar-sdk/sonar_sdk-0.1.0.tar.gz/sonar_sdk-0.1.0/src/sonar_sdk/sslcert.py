class SonarSslcert:
    """SSL Certificate checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the SSL Certificate checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection

