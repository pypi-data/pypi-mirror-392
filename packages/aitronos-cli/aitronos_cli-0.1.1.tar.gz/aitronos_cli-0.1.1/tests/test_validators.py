"""Tests for validation utilities."""

import pytest
from pathlib import Path
import json
import tempfile

from aitronos_cli.utils.validators import (
    validate_automation_id,
    validate_email,
    validate_config_freddy_json,
    validate_github_url,
    sanitize_automation_name
)


class TestValidateAutomationId:
    """Test automation ID validation."""
    
    def test_valid_automation_id(self):
        assert validate_automation_id("com.company.automation")
        assert validate_automation_id("com.example.my-automation")
        assert validate_automation_id("io.github.user.project")
    
    def test_invalid_automation_id(self):
        assert not validate_automation_id("invalid")
        assert not validate_automation_id("com")
        assert not validate_automation_id("Com.Company.Automation")  # uppercase
        assert not validate_automation_id("com.company")  # too short
        assert not validate_automation_id("com..automation")  # double dot


class TestValidateEmail:
    """Test email validation."""
    
    def test_valid_email(self):
        assert validate_email("user@example.com")
        assert validate_email("test.user@company.co.uk")
        assert validate_email("user+tag@domain.com")
    
    def test_invalid_email(self):
        assert not validate_email("invalid")
        assert not validate_email("@example.com")
        assert not validate_email("user@")
        assert not validate_email("user@domain")


class TestValidateConfigFreddyJson:
    """Test config.freddy.json validation."""
    
    def test_valid_config(self):
        config_data = [
            {
                "id": "com.example.automation",
                "configuration": {
                    "executionDescription": "Test automation",
                    "executionFilePath": "src/main.py",
                    "returnMode": "stream"
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = Path(f.name)
        
        try:
            is_valid, error = validate_config_freddy_json(temp_path)
            assert is_valid
            assert error is None
        finally:
            temp_path.unlink()
    
    def test_missing_file(self):
        is_valid, error = validate_config_freddy_json(Path("nonexistent.json"))
        assert not is_valid
        assert "not found" in error
    
    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_path = Path(f.name)
        
        try:
            is_valid, error = validate_config_freddy_json(temp_path)
            assert not is_valid
            assert "Invalid JSON" in error
        finally:
            temp_path.unlink()
    
    def test_missing_required_field(self):
        config_data = [
            {
                "id": "com.example.automation",
                "configuration": {
                    "executionDescription": "Test"
                    # Missing executionFilePath and returnMode
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = Path(f.name)
        
        try:
            is_valid, error = validate_config_freddy_json(temp_path)
            assert not is_valid
            assert "Missing required field" in error
        finally:
            temp_path.unlink()


class TestValidateGithubUrl:
    """Test GitHub URL validation."""
    
    def test_valid_github_url(self):
        assert validate_github_url("https://github.com/user/repo")
        assert validate_github_url("https://github.com/user/repo.git")
        assert validate_github_url("https://github.com/user-name/repo-name")
    
    def test_invalid_github_url(self):
        assert not validate_github_url("http://github.com/user/repo")  # http
        assert not validate_github_url("https://gitlab.com/user/repo")  # not github
        assert not validate_github_url("github.com/user/repo")  # no protocol
        assert not validate_github_url("https://github.com/user")  # no repo


class TestSanitizeAutomationName:
    """Test automation name sanitization."""
    
    def test_sanitize_name(self):
        assert sanitize_automation_name("My Automation!") == "My Automation"
        assert sanitize_automation_name("Test@#$%") == "Test"
        assert sanitize_automation_name("  Spaced  ") == "Spaced"
        assert sanitize_automation_name("Valid-Name_123") == "Valid-Name_123"

