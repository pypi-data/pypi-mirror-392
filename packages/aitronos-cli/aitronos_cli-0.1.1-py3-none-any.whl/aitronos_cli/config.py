"""Configuration management for Aitronos CLI."""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """CLI configuration manager."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".aitronos"
        self.config_file = self.config_dir / "config.json"
        self.auth_file = self.config_dir / "auth.json"
        self._load_env_files()
        self.config = self._load_config()
    
    def _load_env_files(self):
        """Load environment variables from .env files."""
        # Check current directory
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Check home directory
        home_env = self.config_dir / ".env"
        if home_env.exists():
            load_dotenv(home_env)
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: str):
        """Set configuration value."""
        self.config[key] = value
        self._save_config()
    
    def delete(self, key: str):
        """Delete configuration value."""
        if key in self.config:
            del self.config[key]
            self._save_config()
    
    def list_all(self) -> dict:
        """Get all configuration values."""
        return self.config.copy()
    
    def get_api_url(self) -> str:
        """Get API URL (Freddy Backend)."""
        # Priority: ENV VAR > config file > default
        return (
            os.getenv('AITRONOS_API_URL') or
            self.get('api_url') or
            'https://api.aitronos.com'
        )
    
    def load_auth(self) -> Optional[dict]:
        """Load authentication data."""
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def save_auth(self, auth_data: dict):
        """Save authentication data."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
        # Set restrictive permissions (owner read/write only)
        self.auth_file.chmod(0o600)
    
    def clear_auth(self):
        """Clear authentication data."""
        if self.auth_file.exists():
            self.auth_file.unlink()


# Global config instance
config = Config()

