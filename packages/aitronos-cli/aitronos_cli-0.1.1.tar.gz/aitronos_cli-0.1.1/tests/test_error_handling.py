"""Tests for API client error handling."""

import pytest
from unittest.mock import Mock, patch
import requests

from aitronos_cli.api_client import AitronosAPIClient, AuthenticationError, AuthorizationError


class TestErrorHandling:
    """Test error handling in API client."""
    
    @pytest.fixture
    def client(self):
        """Create API client instance."""
        return AitronosAPIClient('https://api.test.com', 'test_token')
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_401_raises_authentication_error(self, mock_request, client):
        """Test that 401 responses raise AuthenticationError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': {
                'system_message': 'Invalid token: user not found',
                'message': 'Your session is invalid'
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.list_automations('org_123')
        
        assert 'Invalid token: user not found' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_401_with_token_type_mismatch(self, mock_request, client):
        """Test that 401 with token type mismatch is caught."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': {
                'code': 'TOKEN_INVALID',
                'system_message': 'Invalid token type: expected access token',
                'message': 'Your session is invalid. Please sign in again.',
                'details': {'token_type': 'refresh'}
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.get_project_templates()
        
        assert 'expected access token' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_403_raises_authorization_error(self, mock_request, client):
        """Test that 403 responses raise AuthorizationError."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'error': {
                'system_message': 'Insufficient permissions',
                'message': 'Access denied'
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthorizationError) as exc_info:
            client.upload_automation(Mock(), 'test', 'org_123')
        
        assert 'Insufficient permissions' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_401_without_json_response(self, mock_request, client):
        """Test 401 handling when response is not JSON."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.side_effect = ValueError("Not JSON")
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.list_automations('org_123')
        
        # Should use default message when JSON parsing fails
        assert 'Authentication failed' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_other_http_errors_not_converted(self, mock_request, client):
        """Test that non-401/403 errors are not converted to custom exceptions."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            'error': {
                'system_message': 'Internal server error'
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        # Should raise HTTPError, not AuthenticationError or AuthorizationError
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            client.list_automations('org_123')
        
        assert 'Internal server error' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_error_message_extraction(self, mock_request, client):
        """Test that error messages are properly extracted from backend responses."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'success': False,
            'error': {
                'code': 'TOKEN_INVALID',
                'message': 'Your session is invalid. Please sign in again.',
                'system_message': 'Invalid token type: expected access token',
                'type': 'authentication_error',
                'status': 401,
                'details': {'token_type': 'refresh'},
                'trace_id': 'abc-123',
                'timestamp': '2025-11-17T05:30:36Z'
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.list_automations('org_123')
        
        # Should extract system_message first
        assert 'Invalid token type: expected access token' in str(exc_info.value)
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_fallback_to_message_field(self, mock_request, client):
        """Test fallback to 'message' field when 'system_message' is not present."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': {
                'message': 'Your session is invalid'
                # No system_message field
            }
        }
        
        mock_error = requests.exceptions.HTTPError(response=mock_response)
        mock_request.side_effect = mock_error
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.list_automations('org_123')
        
        assert 'Your session is invalid' in str(exc_info.value)
    
    def test_update_auth_token(self, client):
        """Test that auth token can be updated."""
        new_token = 'new_token_123'
        client.update_auth_token(new_token)
        
        assert client.auth_token == new_token
        assert client.session.headers['Authorization'] == f'Bearer {new_token}'
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_successful_request_after_token_update(self, mock_request, client):
        """Test that requests work after updating token."""
        mock_response = Mock()
        mock_response.json.return_value = {'automations': []}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Update token
        client.update_auth_token('new_token')
        
        # Make request
        result = client.list_automations('org_123')
        
        # Verify request was made with new token
        assert result == {'automations': []}
        call_kwargs = mock_request.call_args[1]
        # The Authorization header should be in the session headers
        assert 'Authorization' in client.session.headers
        assert client.session.headers['Authorization'] == 'Bearer new_token'


class TestAuthenticationErrorException:
    """Test AuthenticationError exception class."""
    
    def test_authentication_error_creation(self):
        """Test creating AuthenticationError."""
        error = AuthenticationError("Test error message")
        assert str(error) == "Test error message"
        assert error.response is None
    
    def test_authentication_error_with_response(self):
        """Test creating AuthenticationError with response."""
        mock_response = Mock()
        error = AuthenticationError("Test error", response=mock_response)
        assert str(error) == "Test error"
        assert error.response == mock_response


class TestAuthorizationErrorException:
    """Test AuthorizationError exception class."""
    
    def test_authorization_error_creation(self):
        """Test creating AuthorizationError."""
        error = AuthorizationError("Access denied")
        assert str(error) == "Access denied"
        assert error.response is None
    
    def test_authorization_error_with_response(self):
        """Test creating AuthorizationError with response."""
        mock_response = Mock()
        error = AuthorizationError("Access denied", response=mock_response)
        assert str(error) == "Access denied"
        assert error.response == mock_response

