"""Tests for configuration management."""

import pytest
import json
import tempfile
from pathlib import Path

from aitronos_cli.config import Config


class TestConfig:
    """Test configuration management."""
    
    def test_get_set_config(self, tmp_path):
        """Test getting and setting configuration values."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        
        # Set value
        config.set('api_url', 'https://test.com')
        assert config.get('api_url') == 'https://test.com'
        
        # Verify file was created
        assert config.config_file.exists()
        
        # Load from file
        with open(config.config_file, 'r') as f:
            data = json.load(f)
        assert data['api_url'] == 'https://test.com'
    
    def test_get_default_value(self, tmp_path):
        """Test getting value with default."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        
        assert config.get('nonexistent', 'default') == 'default'
    
    def test_delete_config(self, tmp_path):
        """Test deleting configuration value."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        
        config.set('key', 'value')
        assert config.get('key') == 'value'
        
        config.delete('key')
        assert config.get('key') is None
    
    def test_list_all_config(self, tmp_path):
        """Test listing all configuration."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        
        config.set('key1', 'value1')
        config.set('key2', 'value2')
        
        all_config = config.list_all()
        assert all_config == {'key1': 'value1', 'key2': 'value2'}
    
    def test_auth_storage(self, tmp_path):
        """Test authentication data storage."""
        config = Config()
        config.config_dir = tmp_path
        config.auth_file = tmp_path / "auth.json"
        
        auth_data = {
            'access_token': 'token123',
            'user_id': 'usr_123'
        }
        
        config.save_auth(auth_data)
        assert config.auth_file.exists()
        
        loaded = config.load_auth()
        assert loaded == auth_data
        
        config.clear_auth()
        assert not config.auth_file.exists()

