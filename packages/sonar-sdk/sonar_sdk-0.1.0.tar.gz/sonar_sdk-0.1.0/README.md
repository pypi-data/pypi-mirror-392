# Sonar SDK

Python API Client for Sonar (Constellix) API.

## Installation

From repository root:

```bash
pip install -e .
```

## Usage

```python
from sonar_sdk import SonarClient

# Create a client
client = SonarClient(api_key="your-api-key", secret_key="your-secret-key")

# System operations
sites = client.system.sites()

# DNS check operations
# Get all DNS checks
all_dns_checks = client.checks.dns.get_all()

# Get a specific DNS check
dns_check = client.checks.dns.get(dnsv2_check_id=123)

# Create a DNS check
new_check = client.checks.dns.create(
    name="My DNS Check",
    fqdn="example.com",
    record_type="A"
)

# Delete a DNS check
client.checks.dns.delete(dnsv2_check_id=123)

# Get version information
version_info = client.version()

# Modify connection settings
client.connection.set_timeout(30)  # Increase timeout to 30 seconds
client.connection.set_retry_settings(max_retries=5, retry_delay=2)  # Update retry settings

# Clean up
client.close_session()
```

## License

MIT

