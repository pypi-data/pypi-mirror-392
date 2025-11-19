"""Input validation utilities."""

import re
import json
import yaml
from pathlib import Path
from typing import Optional, Tuple


def validate_automation_id(automation_id: str) -> bool:
    """
    Validate automation ID format.
    
    Expected format: com.company.automation-name
    """
    pattern = r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$'
    return bool(re.match(pattern, automation_id))


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_config_freddy_json(file_path: Path) -> tuple[bool, Optional[str]]:
    """
    Validate config.freddy.json file.
    
    Returns:
        (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "config.freddy.json not found"
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False, "config.freddy.json must be an array"
        
        if len(data) == 0:
            return False, "config.freddy.json must contain at least one automation"
        
        for item in data:
            if 'id' not in item:
                return False, "Each automation must have an 'id' field"
            
            if 'configuration' not in item:
                return False, "Each automation must have a 'configuration' field"
            
            config = item['configuration']
            required_fields = ['executionDescription', 'executionFilePath', 'returnMode']
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"
        
        return True, None
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_github_url(url: str) -> bool:
    """Validate GitHub repository URL."""
    pattern = r'^https://github\.com/[\w-]+/[\w.-]+(?:\.git)?$'
    return bool(re.match(pattern, url))


def sanitize_automation_name(name: str) -> str:
    """Sanitize automation name for use in file names."""
    # Remove special characters, keep alphanumeric and basic punctuation
    return re.sub(r'[^\w\s-]', '', name).strip()


def validate_streamline_yaml(yaml_file: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate streamline.yaml configuration file.
    
    Args:
        yaml_file: Path to streamline.yaml file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not yaml_file.exists():
        return False, f"File not found: {yaml_file}"
    
    try:
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            return False, "Invalid YAML: must be a dictionary"
        
        # Required fields
        required_fields = ['automation_id', 'name', 'entry_point', 'return_mode']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
            if not config[field]:
                return False, f"Field cannot be empty: {field}"
        
        # Validate return_mode
        if config['return_mode'] not in ['stream', 'sync']:
            return False, f"Invalid return_mode: {config['return_mode']} (must be 'stream' or 'sync')"
        
        # Validate automation_id format
        automation_id = config['automation_id']
        if '.' not in automation_id:
            return False, f"Invalid automation_id format: {automation_id} (should be like 'com.company.automation-name')"
        
        return True, None
        
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

