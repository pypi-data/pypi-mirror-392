class SonarTcp:
    """TCP checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the TCP checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection

