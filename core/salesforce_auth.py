"""
Salesforce Authentication Module - Fixed API Version Detection
Handles connection to Salesforce orgs
"""
from simple_salesforce import Salesforce
import logging

logger = logging.getLogger(__name__)

class SalesforceAuth:
    """Manages Salesforce authentication and connection"""
    
    def __init__(self):
        self.connection = None
        self.org_info = {}
    
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
            # Determine instance URL
            if custom_domain:
                # Custom domain takes precedence
                instance_url = f"https://{custom_domain}"
                logger.info(f"Connecting to custom domain: {custom_domain}")
                
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
            
            # Get org info
            org_id = self.connection.sf_instance
            
            # Try to detect API version, but don't fail if it doesn't work
            try:
                # Get available API versions using the correct endpoint
                # Use the base_url and call versions endpoint directly
                versions_url = f"{self.connection.base_url}services/data/"
                response = self.connection.session.get(versions_url)
                
                if response.status_code == 200:
                    versions = response.json()
                    if versions and isinstance(versions, list):
                        # Use the latest available API version
                        latest_version = versions[-1]['version']
                        logger.info(f"Detected latest API version: {latest_version}")
                    else:
                        latest_version = "59.0"  # Fallback
                        logger.info("Using fallback API version: 59.0")
                else:
                    latest_version = "59.0"  # Fallback
                    logger.info("Could not detect API version, using fallback: 59.0")
            except Exception as version_error:
                latest_version = "59.0"  # Fallback
                logger.warning(f"Failed to detect API version, using fallback: {str(version_error)}")
            
            self.org_info = {
                'org_id': org_id,
                'username': username,
                'domain': custom_domain if custom_domain else domain,
                'api_version': latest_version,
                'is_custom_domain': bool(custom_domain)
            }
            
            logger.info(f"Successfully connected to Salesforce: {username} (API v{latest_version})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    def test_connection(self):
        """Test if connection is valid"""
        if not self.connection:
            return False
        
        try:
            # Simple query to test connection
            self.connection.query("SELECT Id FROM User LIMIT 1")
            return True
        except:
            return False
    
    def disconnect(self):
        """Disconnect from Salesforce"""
        self.connection = None
        self.org_info = {}
        logger.info("Disconnected from Salesforce")