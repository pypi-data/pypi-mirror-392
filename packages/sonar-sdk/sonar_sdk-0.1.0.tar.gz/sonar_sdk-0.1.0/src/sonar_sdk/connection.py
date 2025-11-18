import requests
import urllib3
import warnings
import time
import logging
import hmac
import hashlib
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logger = logging.getLogger("sonar-sdk")

class SonarConnection:
    def __init__(self, api_key, secret_key, base_url="https://api.sonar.constellix.com/rest/api", 
                 max_retries=3, retry_delay=1, connection_timeout=10, 
                 disable_connection_pooling=False):
        """
        Initialize the Sonar (Constellix) API connection client.

        :param api_key: The API key for authentication
        :param secret_key: The secret key for HMAC authentication
        :param base_url: The base URL of the Sonar API (defaults to "https://sonar.constellix.com")
        :param max_retries: Maximum number of retry attempts for failed requests
        :param retry_delay: Base delay in seconds between retries (will use exponential backoff)
        :param connection_timeout: Connection timeout in seconds
        :param disable_connection_pooling: If True, disable connection pooling to prevent connection reuse issues
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.secret_key = secret_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        self.disable_connection_pooling = disable_connection_pooling
        
        # Create a session for connection reuse
        self.session = requests.Session()
        
        # Configure retry adapter
        self._configure_retry_adapter()
        
        # Set timeout
        self.session.timeout = connection_timeout
    
    def _configure_retry_adapter(self):
        """Configure and mount the retry adapter for HTTP and HTTPS."""
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        # Configure adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=1 if self.disable_connection_pooling else 10,
            pool_maxsize=1 if self.disable_connection_pooling else 10
        )
        
        # Mount the adapter to both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_timeout(self, timeout):
        """
        Update the connection timeout.
        
        :param timeout: Connection timeout in seconds
        """
        self.connection_timeout = timeout
        self.session.timeout = timeout
    
    def set_retry_settings(self, max_retries=None, retry_delay=None):
        """
        Update retry settings and reconfigure the adapter.
        
        :param max_retries: Maximum number of retry attempts (optional)
        :param retry_delay: Base delay in seconds between retries (optional)
        """
        if max_retries is not None:
            self.max_retries = max_retries
        if retry_delay is not None:
            self.retry_delay = retry_delay
        
        # Reconfigure the adapter with new settings
        self._configure_retry_adapter()

    def _generate_hmac_token(self):
        """Generate HMAC authentication token for Sonar API.
        
        Returns the combined security token in the format: api_key:hmac:timestamp
        """
        # Get current timestamp in milliseconds
        timestamp = str(int(time.time() * 1000))
        
        # Calculate HMAC-SHA1 of timestamp using secret key
        hmac_digest = hmac.new(
            self.secret_key.encode('utf-8'),
            timestamp.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        # Base64 encode the HMAC
        hmac_b64 = base64.b64encode(hmac_digest).decode('utf-8')
        
        # Create combined security token
        security_token = f"{self.api_key}:{hmac_b64}:{timestamp}"
        
        return security_token

    def _get_headers(self):
        """Return headers including HMAC authentication and required Content-Type."""
        security_token = self._generate_hmac_token()
        
        return {
            "Content-Type": "application/json",
            "x-cns-security-token": security_token
        }

    def _do_call(self, method, endpoint, params=None, data=None, files=None, is_binary=False):
        """Internal method to send an authenticated request to the Sonar API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        # Convert dictionary to form-encoded string if sending multipart
        request_data = None if files else data
        form_data = data if files else None  # Ensure correct encoding

        try:
            logger.debug(f"Sending {method} request to {url}")
            if request_data:
                logger.debug(f"Request payload: {request_data}")
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=request_data,
                files=files,
                data=form_data,
                verify=False,
                timeout=self.connection_timeout
            )
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text[:500]}")

            # Handle 4xx responses - raise exception with error details
            if 400 <= response.status_code < 500:
                error_msg = f"HTTP {response.status_code}: {response.reason}"
                try:
                    error_data = response.json()
                    if error_data:
                        error_msg = f"{error_msg} - {error_data}"
                    logger.error(f"API error: {error_msg}")
                except requests.exceptions.JSONDecodeError:
                    error_msg = f"{error_msg} - {response.text}"
                    logger.error(f"API error: {error_msg}")
                raise Exception(error_msg)

            response.raise_for_status()

            # Handle 201 Created responses (typically empty body for POST)
            if response.status_code == 201:
                try:
                    if response.content.strip():
                        return response.json()
                    else:
                        # Empty 201 response - creation successful but no data returned
                        logger.debug("Created successfully (201) with empty response body")
                        return {"status": "created", "status_code": 201}
                except requests.exceptions.JSONDecodeError:
                    return {"status": "created", "status_code": 201}

            if is_binary:
                return response.content  # Return raw binary content (e.g., for file exports)

            if not response.content.strip():
                # Empty response - handle common HTTP status codes
                status_code = response.status_code
                if status_code == 200:
                    return {"status": "ok", "status_code": 200}
                elif status_code == 201:
                    return {"status": "created", "status_code": 201}
                elif status_code == 202:
                    return {"status": "accepted", "status_code": 202}
                elif status_code == 204:
                    return {"status": "no_content", "status_code": 204}
                elif 200 <= status_code < 300:
                    return {"status": "success", "status_code": status_code}
                else:
                    return {"status": "unknown", "status_code": status_code}

            try:
                return response.json()  # Attempt to parse JSON
            except requests.exceptions.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {response.text[:200]}")
                return response.text  # Return raw text as fallback
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request error: {str(e)}")

    def get(self, endpoint, params=None, is_binary=False):
        """Send a GET request."""
        return self._do_call("GET", endpoint, params=params, is_binary=is_binary)

    def post(self, endpoint, data=None, files=None):
        """Send a POST request."""
        return self._do_call("POST", endpoint, data=data, files=files)

    def put(self, endpoint, data=None):
        """Send a PUT request."""
        return self._do_call("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None, data=None):
        """Send a DELETE request."""
        return self._do_call("DELETE", endpoint, params=params, data=data)

    def patch(self, endpoint, data=None):
        """Send a PATCH request."""
        return self._do_call("PATCH", endpoint, data=data)
    
    def close(self):
        """Close the session and release connections."""
        self.session.close()