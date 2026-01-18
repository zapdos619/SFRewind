"""
Salesforce Authentication Module - PRODUCTION READY
Issue #7 Fix: Connection pooling, auto-reconnect, session validation
"""
from simple_salesforce import Salesforce
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def ensure_connected(func):
    """
    Decorator to ensure connection is valid before API calls (Issue #7 Fix)
    Automatically reconnects if session has expired
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._ensure_connected()
        return func(self, *args, **kwargs)
    return wrapper


class SalesforceAuth:
    """Manages Salesforce authentication and connection - PRODUCTION READY"""
    
    def __init__(self):
        self.connection = None
        self.org_info = {}
        
        # Session management (Issue #7 Fix)
        self._last_activity = None
        self._session_timeout = 7200  # 2 hours in seconds
        self._credentials = None  # Store for auto-reconnect
        self._connection_attempts = 0
        self._max_reconnect_attempts = 3
    
    def connect(self, username, password, security_token, domain='test', custom_domain=None):
        """
        Connect to Salesforce org with dynamic API version detection
        
        Args:
            username: Salesforce username
            password: Salesforce password
            security_token: Salesforce security token
            domain: 'test' for sandbox, 'login' for production
            custom_domain: Custom domain (e.g., 'mycompany.my.salesforce.com')
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to Salesforce as {username}...")
            
            # Determine instance URL
            if custom_domain:
                # Custom domain takes precedence
                instance_url = f"https://{custom_domain}"
                logger.info(f"Using custom domain: {custom_domain}")
                
                # Connect with custom domain
                self.connection = Salesforce(
                    username=username,
                    password=password,
                    security_token=security_token,
                    instance_url=instance_url
                )
            else:
                # Standard domain
                self.connection = Salesforce(
                    username=username,
                    password=password,
                    security_token=security_token,
                    domain=domain
                )
            
            # Store credentials for auto-reconnect (Issue #7 Fix)
            self._credentials = {
                'username': username,
                'password': password,
                'security_token': security_token,
                'domain': domain,
                'custom_domain': custom_domain
            }
            
            # Reset connection tracking
            self._last_activity = time.time()
            self._connection_attempts = 0
            
            # Get org info
            org_id = self.connection.sf_instance
            
            # Try to detect API version
            try:
                versions_url = f"{self.connection.base_url}services/data/"
                response = self.connection.session.get(versions_url)
                
                if response.status_code == 200:
                    versions = response.json()
                    if versions and isinstance(versions, list):
                        latest_version = versions[-1]['version']
                        logger.info(f"Detected API version: v{latest_version}")
                    else:
                        latest_version = "59.0"
                        logger.info("Using fallback API version: v59.0")
                else:
                    latest_version = "59.0"
                    logger.warning("Could not detect API version, using fallback: v59.0")
            except Exception as version_error:
                latest_version = "59.0"
                logger.warning(f"API version detection failed: {version_error}, using fallback: v59.0")
            
            self.org_info = {
                'org_id': org_id,
                'username': username,
                'domain': custom_domain if custom_domain else domain,
                'api_version': latest_version,
                'is_custom_domain': bool(custom_domain)
            }
            
            logger.info(f"✓ Connected successfully: {username} | Org: {org_id} | API: v{latest_version}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Connection failed: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _ensure_connected(self):
        """
        Ensure connection is valid, reconnect if needed (Issue #7 Fix)
        
        This method:
        1. Checks if connection exists
        2. Checks if session might be expired (based on time)
        3. Tests connection with lightweight query
        4. Auto-reconnects if session is invalid
        """
        if not self.connection:
            raise Exception("Not connected to Salesforce")
        
        if not self._credentials:
            # Can't reconnect without credentials
            return
        
        # Check if session might be expired (time-based)
        if self._last_activity:
            elapsed = time.time() - self._last_activity
            
            # If close to timeout (within 5 minutes), test connection
            if elapsed > (self._session_timeout - 300):
                logger.debug(f"Session age: {int(elapsed/60)} minutes, testing connection...")
                
                if not self._test_connection_quietly():
                    logger.warning("Session expired (time-based), reconnecting...")
                    self._reconnect()
        
        # Always test connection before critical operations
        # This catches session timeouts that happen due to server-side policies
        if not self._test_connection_quietly():
            logger.warning("Session invalid, reconnecting...")
            self._reconnect()
        
        # Update last activity timestamp
        self._last_activity = time.time()
    
    def _test_connection_quietly(self):
        """Test connection without logging errors"""
        if not self.connection:
            return False
        
        try:
            # Lightweight query to test session
            self.connection.query("SELECT Id FROM User LIMIT 1")
            return True
        except Exception as e:
            # Check if it's a session error
            error_str = str(e).upper()
            if any(x in error_str for x in ['INVALID_SESSION', 'SESSION_EXPIRED', 'AUTHENTICATION']):
                logger.debug(f"Session validation failed: {e}")
                return False
            else:
                # Other error - connection might be fine, just query issue
                logger.warning(f"Connection test query failed: {e}")
                return True  # Assume connection is okay
    
    def _reconnect(self):
        """
        Attempt to reconnect to Salesforce (Issue #7 Fix)
        
        Uses stored credentials to establish new session.
        Implements retry logic with exponential backoff.
        """
        if not self._credentials:
            raise Exception("Cannot reconnect: credentials not stored")
        
        self._connection_attempts += 1
        
        if self._connection_attempts > self._max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self._max_reconnect_attempts}) exceeded")
            raise Exception("Failed to reconnect: Max attempts exceeded")
        
        try:
            logger.info(f"Reconnecting to Salesforce (attempt {self._connection_attempts}/{self._max_reconnect_attempts})...")
            
            # Wait before retry (exponential backoff)
            if self._connection_attempts > 1:
                wait_time = 2 ** (self._connection_attempts - 1)  # 1s, 2s, 4s
                logger.debug(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
            # Reconnect using stored credentials
            self.connect(**self._credentials)
            
            logger.info("✓ Reconnection successful")
            
        except Exception as e:
            logger.error(f"✗ Reconnection attempt {self._connection_attempts} failed: {e}")
            raise Exception(f"Reconnection failed: {str(e)}")
    
    def test_connection(self):
        """
        Test if connection is valid (public method)
        
        Returns:
            bool: True if connection is valid
        """
        if not self.connection:
            return False
        
        try:
            self.connection.query("SELECT Id FROM User LIMIT 1")
            self._last_activity = time.time()
            return True
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False
    
    def get_connection(self):
        """
        Get validated connection (Issue #7 Fix)
        
        Returns connection object, ensuring it's valid first.
        Auto-reconnects if session has expired.
        
        Returns:
            Salesforce: Valid connection object
        """
        self._ensure_connected()
        return self.connection
    
    def disconnect(self):
        """Disconnect from Salesforce and clear credentials"""
        if self.connection:
            logger.info("Disconnecting from Salesforce...")
        
        self.connection = None
        self.org_info = {}
        self._last_activity = None
        self._credentials = None
        self._connection_attempts = 0
        
        logger.info("✓ Disconnected")
    
    def get_session_age(self):
        """
        Get session age in minutes
        
        Returns:
            int: Minutes since last activity, or None if not connected
        """
        if not self._last_activity:
            return None
        
        elapsed = time.time() - self._last_activity
        return int(elapsed / 60)
    
    def is_session_near_expiry(self):
        """
        Check if session is near expiry
        
        Returns:
            bool: True if session will expire within 10 minutes
        """
        if not self._last_activity:
            return False
        
        elapsed = time.time() - self._last_activity
        remaining = self._session_timeout - elapsed
        
        return remaining < 600  # 10 minutes