"""Authentication management for Aitronos CLI."""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import jwt

from aitronos_cli.config import config
from aitronos_cli.api_client import AitronosAPIClient
from aitronos_cli.utils.colors import log_ok, log_error, log_info, log_warn


class AuthManager:
    """Manage authentication with Freddy Backend."""
    
    def __init__(self):
        self.config = config
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid token."""
        auth_data = self.config.load_auth()
        if not auth_data:
            return False
        
        access_token = auth_data.get('access_token')
        if not access_token:
            return False
        
        # Check if token is expired
        try:
            decoded = jwt.decode(
                access_token,
                options={"verify_signature": False}
            )
            exp = decoded.get('exp')
            if exp:
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
                if datetime.now(timezone.utc) >= exp_dt:
                    return False
            return True
        except jwt.DecodeError:
            return False
    
    def get_access_token(self, auto_refresh: bool = True) -> Optional[str]:
        """
        Get current access token, automatically refreshing if expired.
        
        Args:
            auto_refresh: If True, automatically refresh expired tokens
            
        Returns:
            Valid access token or None
        """
        auth_data = self.config.load_auth()
        if not auth_data:
            return None
        
        access_token = auth_data.get('access_token')
        if not access_token:
            return None
        
        # Check if token is expired or about to expire (within 5 minutes)
        try:
            decoded = jwt.decode(
                access_token,
                options={"verify_signature": False}
            )
            exp = decoded.get('exp')
            if exp:
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                # Refresh if expired or expiring within 5 minutes
                if now >= exp_dt - timedelta(minutes=5):
                    if auto_refresh and self.refresh_access_token():
                        # Get the new token after refresh
                        auth_data = self.config.load_auth()
                        if auth_data:
                            return auth_data.get('access_token')
                    return None
        except jwt.DecodeError:
            return None
        
        return access_token
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get stored user information."""
        auth_data = self.config.load_auth()
        if auth_data:
            return {
                'user_id': auth_data.get('user_id'),
                'email': auth_data.get('email'),
                'organization_id': auth_data.get('organization_id')
            }
        return None
    
    def get_organization_id(self) -> Optional[str]:
        """Get current organization ID."""
        auth_data = self.config.load_auth()
        if auth_data:
            return auth_data.get('organization_id')
        return None
    
    def set_organization_id(self, org_id: str):
        """Set current organization ID."""
        auth_data = self.config.load_auth()
        if auth_data:
            auth_data['organization_id'] = org_id
            self.config.save_auth(auth_data)
            log_ok(f"Organization set to: {org_id}")
        else:
            log_error("Not authenticated")
    
    def login(self, email_or_username: str, password: str) -> bool:
        """
        Perform login with 2FA.
        
        Args:
            email_or_username: User email or username
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        api_url = self.config.get_api_url()
        client = AitronosAPIClient(api_url)
        
        try:
            # Step 1: Initiate login (sends 2FA code)
            log_info("Initiating login...")
            try:
                login_response = client.login(email_or_username, password)
            except Exception as e:
                # Extract the error message from the exception
                error_msg = str(e)
                # If it's an HTTPError, the message is in args[0]
                if hasattr(e, 'args') and e.args:
                    error_msg = e.args[0]
                log_error(f"Login failed: {error_msg}")
                return False
            
            # Backend returns 'email_key' not 'verification_key'
            verification_key = login_response.get('email_key') or login_response.get('verification_key')
            if not verification_key:
                log_error("Login failed: No verification key received")
                return False
            
            log_ok("2FA code sent to your email")
            
            # Step 2: Get 2FA code from user
            code = input("Enter verification code: ").strip()
            if not code:
                log_error("Verification code required")
                return False
            
            # Step 3: Verify code and complete login
            log_info("Verifying code...")
            try:
                verify_response = client.verify_login(verification_key, code)
            except Exception as e:
                # Extract the error message from the exception
                error_msg = str(e)
                # If it's an HTTPError, the message is in args[0]
                if hasattr(e, 'args') and e.args:
                    error_msg = e.args[0]
                log_error(f"Verification failed: {error_msg}")
                return False
            
            # Extract tokens and user info (backend returns camelCase)
            access_token = verify_response.get('token') or verify_response.get('access_token')
            refresh_token = verify_response.get('refreshToken') or verify_response.get('refresh_token')
            user_data = verify_response.get('user', {})
            
            if not access_token or not refresh_token:
                log_error("Login failed: No tokens received")
                return False
            
            # Verify token types to prevent swapping
            try:
                access_decoded = jwt.decode(access_token, options={"verify_signature": False})
                refresh_decoded = jwt.decode(refresh_token, options={"verify_signature": False})
                
                # Check token types
                access_type = access_decoded.get('type', 'access')
                refresh_type = refresh_decoded.get('type', 'refresh')
                
                if access_type != 'access':
                    log_error(f"Warning: access_token has wrong type: {access_type}")
                    # Swap if needed
                    if refresh_type == 'access':
                        log_warn("Tokens were swapped, correcting...")
                        access_token, refresh_token = refresh_token, access_token
                        access_decoded, refresh_decoded = refresh_decoded, access_decoded
                
                exp = access_decoded.get('exp')
                expires_at = None
                if exp:
                    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
            except jwt.DecodeError as e:
                log_error(f"Failed to decode tokens: {e}")
                return False
            
            # Save auth data (without organization_id for now)
            auth_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id': user_data.get('id'),
                'email': user_data.get('email'),
                'expires_at': expires_at
            }
            self.config.save_auth(auth_data)
            
            log_ok(f"Successfully logged in as {user_data.get('email')}")
            return True
            
        except Exception as e:
            log_error(f"Login failed: {str(e)}")
            return False
    
    def logout(self):
        """Logout and clear stored tokens."""
        self.config.clear_auth()
        log_ok("Successfully logged out")
    
    def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        auth_data = self.config.load_auth()
        if not auth_data:
            return False
        
        refresh_token = auth_data.get('refresh_token')
        if not refresh_token:
            return False
        
        api_url = self.config.get_api_url()
        client = AitronosAPIClient(api_url)
        
        try:
            refresh_response = client.refresh_token(refresh_token)
            new_access_token = refresh_response.get('token') or refresh_response.get('access_token')
            
            if not new_access_token:
                return False
            
            # Update auth data with new token
            auth_data['access_token'] = new_access_token
            
            # Update expiration
            decoded = jwt.decode(
                new_access_token,
                options={"verify_signature": False}
            )
            exp = decoded.get('exp')
            if exp:
                auth_data['expires_at'] = datetime.fromtimestamp(
                    exp, tz=timezone.utc
                ).isoformat()
            
            self.config.save_auth(auth_data)
            return True
            
        except Exception:
            return False
    
    def show_status(self):
        """Display authentication status."""
        if not self.is_authenticated():
            log_warn("Not authenticated")
            log_info("Run 'aitronos auth login' to authenticate")
            return
        
        user_info = self.get_user_info()
        if user_info:
            log_ok("Authenticated")
            print(f"  Email: {user_info.get('email')}")
            print(f"  User ID: {user_info.get('user_id')}")
            print(f"  Organization: {user_info.get('organization_id')}")
            
            auth_data = self.config.load_auth()
            if auth_data and auth_data.get('expires_at'):
                print(f"  Token expires: {auth_data.get('expires_at')}")


# Global auth manager instance
auth_manager = AuthManager()

