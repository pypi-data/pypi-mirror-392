from .http import SonarHttp
from .icmp import SonarIcmp
from .dns import SonarDns
from .tcp import SonarTcp
from .sslcert import SonarSslcert

class SonarChecks:
    """Checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the Checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection
        
        # Attach check submodules
        self.http = SonarHttp(self.connection)
        self.icmp = SonarIcmp(self.connection)
        self.dns = SonarDns(self.connection)
        self.tcp = SonarTcp(self.connection)
        self.sslcert = SonarSslcert(self.connection)

