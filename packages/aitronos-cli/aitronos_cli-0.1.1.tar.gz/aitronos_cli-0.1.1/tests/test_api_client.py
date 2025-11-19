"""Tests for API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

from aitronos_cli.api_client import AitronosAPIClient


class TestAitronosAPIClient:
    """Test API client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = AitronosAPIClient('https://api.test.com', 'token123')
        assert client.base_url == 'https://api.test.com'
        assert client.auth_token == 'token123'
        assert 'Authorization' in client.session.headers
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_login(self, mock_request):
        """Test login request."""
        mock_response = Mock()
        mock_response.json.return_value = {'verification_key': 'key123'}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = AitronosAPIClient('https://api.test.com')
        result = client.login('user@test.com', 'password')
        
        assert result['verification_key'] == 'key123'
        mock_request.assert_called_once()
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_get_project_templates(self, mock_request):
        """Test fetching project templates."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'templates': {
                'config.freddy.json': {'content': '...'}
            }
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = AitronosAPIClient('https://api.test.com', 'token')
        result = client.get_project_templates()
        
        assert 'templates' in result
        assert 'config.freddy.json' in result['templates']
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_list_automations(self, mock_request):
        """Test listing automations."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'automations': [
                {'id': 'sauto_123', 'name': 'Test Automation'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = AitronosAPIClient('https://api.test.com', 'token')
        result = client.list_automations('org_123')
        
        assert len(result['automations']) == 1
        assert result['automations'][0]['id'] == 'sauto_123'
    
    @patch('aitronos_cli.api_client.requests.Session.request')
    def test_execute_automation(self, mock_request):
        """Test executing automation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'execution_id': 'sexec_123',
            'status': 'running'
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = AitronosAPIClient('https://api.test.com', 'token')
        result = client.execute_automation('sauto_123', {'param': 'value'})
        
        assert result['execution_id'] == 'sexec_123'
        assert result['status'] == 'running'

