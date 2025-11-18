class SonarIcmp:
    """ICMP checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the ICMP checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection

