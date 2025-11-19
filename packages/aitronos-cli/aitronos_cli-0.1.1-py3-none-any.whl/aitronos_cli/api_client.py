"""API client for Freddy Backend communication."""

import requests
from typing import Optional, Dict, Any
from pathlib import Path


class AitronosAPIClient:
    """
    API client for Freddy Backend (middleware to all services).
    
    IMPORTANT: This client ONLY communicates with Freddy Backend.
    No direct communication with Streamline or other services.
    """
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Freddy Backend base URL (e.g., https://api.aitronos.com)
            auth_token: JWT access token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def update_auth_token(self, token: str):
        """Update the authorization token for subsequent requests."""
        self.auth_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request to Freddy Backend.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: On request failure
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            # Try to parse a more specific error from the backend response
            try:
                error_data = err.response.json()
                system_message = error_data.get("error", {}).get("system_message")
                if system_message:
                    # Re-raise with a more informative message
                    raise requests.exceptions.HTTPError(
                        f"{system_message}", 
                        response=err.response
                    ) from err
            except (ValueError, AttributeError):
                # Response was not JSON or didn't have expected structure
                pass
            raise err
    
    # Authentication endpoints
    
    def login(self, email_or_username: str, password: str) -> Dict[str, Any]:
        """
        Initiate login (sends 2FA code).
        
        Args:
            email_or_username: User email or username
            password: User password
            
        Returns:
            Login response with verification_key
        """
        import platform
        
        device_info = {
            "device": "Aitronos CLI",
            "platform": "cli",
            "operating_system": f"{platform.system()} {platform.release()}",
            "device_id": "cli-device",
            "location": "Unknown",
            "latitude": "0",
            "longitude": "0"
        }
        
        response = self._make_request(
            'POST',
            '/v1/auth/login',
            json={
                'email_or_username': email_or_username,
                'password': password,
                'device_info': device_info
            }
        )
        return response.json()
    
    def verify_login(self, verification_key: str, code: str) -> Dict[str, Any]:
        """
        Verify 2FA code and complete login.
        
        Args:
            verification_key: Verification key (email_key) from login
            code: 2FA verification code
            
        Returns:
            Auth tokens and user info
        """
        response = self._make_request(
            'POST',
            '/v1/auth/verify',
            json={
                'email_key': verification_key,
                'verification_code': code
            }
        )
        return response.json()
    
    def list_organizations(self) -> Dict[str, Any]:
        """
        List all organizations for the authenticated user.
        
        Returns:
            List of organizations
        """
        response = self._make_request(
            'GET',
            '/v1/organizations'
        )
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token
        """
        response = self._make_request(
            'POST',
            '/v1/auth/refresh',
            json={'refresh_token': refresh_token}
        )
        return response.json()
    
    # Streamline endpoints (via Freddy Backend proxy)
    
    def get_project_templates(self) -> Dict[str, Any]:
        """
        Get Streamline project templates.
        
        Flow: CLI → Freddy Backend → Streamline
        
        Returns:
            Template files with placeholders
        """
        response = self._make_request(
            'GET',
            '/v1/streamline/templates/project'
        )
        return response.json()
    
    def upload_automation(
        self,
        zip_file_path: Path,
        automation_name: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Upload automation to Streamline (via Freddy Backend).
        
        Flow: CLI → Freddy Backend → Streamline
        
        Args:
            zip_file_path: Path to ZIP file
            automation_name: Name of automation
            organization_id: Organization ID
            
        Returns:
            Upload response with automation_id
        """
        with open(zip_file_path, 'rb') as f:
            files = {
                'file': (zip_file_path.name, f, 'application/zip')
            }
            data = {
                'automation_name': automation_name,
                'organization_id': organization_id
            }
            response = self._make_request(
                'POST',
                '/v1/streamline/automations/upload',
                files=files,
                data=data
            )
        return response.json()
    
    def link_github_repo(
        self,
        repository_url: str,
        branch: str,
        github_token: str,
        automation_name: str
    ) -> Dict[str, Any]:
        """
        Link GitHub repository for auto-sync (via Freddy Backend).
        
        Flow: CLI → Freddy Backend → Streamline (+ GitHub API)
        
        Args:
            repository_url: GitHub repository URL
            branch: Branch name
            github_token: GitHub personal access token
            automation_name: Automation name
            
        Returns:
            Link response with automation_id and webhook info
        """
        response = self._make_request(
            'POST',
            '/v1/streamline/automations/github/link',
            json={
                'repository_url': repository_url,
                'branch': branch,
                'github_token': github_token,
                'automation_name': automation_name
            }
        )
        return response.json()
    
    def list_automations(self, organization_id: str) -> Dict[str, Any]:
        """
        List automations (via Freddy Backend).
        
        Flow: CLI → Freddy Backend → Streamline
        
        Args:
            organization_id: Organization ID
            
        Returns:
            List of automations
        """
        response = self._make_request(
            'GET',
            '/v1/streamline/automations',
            params={'organization_id': organization_id}
        )
        return response.json()
    
    def execute_automation(
        self,
        automation_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute automation (via Freddy Backend).
        
        Flow: CLI → Freddy Backend → Streamline
        
        Args:
            automation_id: Automation ID
            parameters: Execution parameters
            
        Returns:
            Execution response with execution_id
        """
        response = self._make_request(
            'POST',
            f'/v1/streamline/automations/{automation_id}/execute',
            json={'parameters': parameters or {}}
        )
        return response.json()
    
    def get_execution_logs(self, execution_id: str) -> Dict[str, Any]:
        """
        Get execution logs (via Freddy Backend).
        
        Flow: CLI → Freddy Backend → Streamline
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution status, logs, and results
        """
        response = self._make_request(
            'GET',
            f'/v1/streamline/executions/{execution_id}'
        )
        return response.json()
    
    # Configuration endpoints
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        response = self._make_request(
            'GET',
            '/api/v1/users/me'
        )
        return response.json()

