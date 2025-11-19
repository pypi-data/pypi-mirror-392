"""Streamline project initialization."""

import os
import io
import zipfile
import tempfile
import yaml
from pathlib import Path
from typing import Optional

from aitronos_cli.config import config
from aitronos_cli.auth import auth_manager
from aitronos_cli.api_client import AitronosAPIClient, AuthenticationError, AuthorizationError
from aitronos_cli.utils.colors import log_ok, log_error, log_info, log_step


def init_project(directory: Optional[str] = None, is_repo: bool = False):
    """
    Initialize Streamline project or repository in current or specified directory.
    
    Fetches templates from Freddy Backend (which proxies to Streamline).
    
    Args:
        directory: Target directory (defaults to current directory)
        is_repo: If True, initialize multi-automation repository; if False, single project
    """
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Determine target directory
    target_dir = Path(directory) if directory else Path.cwd()
    if not target_dir.exists():
        log_error(f"Directory does not exist: {target_dir}")
        return False
    
    # Check if directory is empty or confirm overwrite
    if list(target_dir.iterdir()):
        response = input(f"Directory {target_dir} is not empty. Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            log_info("Cancelled")
            return False
    
    template_type = "repository" if is_repo else "project"
    log_step(f"Initializing Streamline {template_type}...")
    
    # Get API client
    api_url = config.get_api_url()
    access_token = auth_manager.get_access_token()
    client = AitronosAPIClient(api_url, access_token)
    
    try:
        # Fetch template ZIP from Freddy Backend
        log_info(f"Fetching {template_type} template...")
        
        if is_repo:
            zip_bytes = client.get_repository_template()
        else:
            zip_bytes = client.get_project_templates()
        
        if not zip_bytes:
            log_error("No template received from server")
            return False
        
        log_ok("Template downloaded successfully")
        
        # Extract ZIP to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                zf.extractall(temp_path)
            
            # Find the template directory (might be nested)
            template_files = list(temp_path.rglob('streamline.yaml'))
            if not template_files:
                log_error("Invalid template: streamline.yaml not found")
                return False
            
            template_root = template_files[0].parent
            log_ok(f"Extracted {len(list(template_root.rglob('*')))} template files")
            
            if is_repo:
                # Repository template: extract as-is without modification
                print()
                log_step("Generating repository files...")
                
                files_created = 0
                for file_path in template_root.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(template_root)
                        target_file = target_dir / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file as-is
                        target_file.write_bytes(file_path.read_bytes())
                        files_created += 1
                        log_ok(f"Created: {relative_path}")
                
                print()
                log_ok(f"Repository initialized successfully!")
                log_info(f"Created {files_created} files in {target_dir}")
                print()
                print("Repository structure:")
                print("  - Multiple automation directories (automation-1/, automation-2/, etc.)")
                print("  - Each automation has its own streamline.yaml")
                print("  - Shared resources in common/ directory")
                print()
                print("Next steps:")
                print("  1. Edit each automation's main.py with your logic")
                print("  2. Update each streamline.yaml with configuration")
                print("  3. Add shared dependencies to common/requirements.txt")
                print("  4. Upload each automation individually or link to GitHub")
                print()
            else:
                # Single project template: interactive wizard
                print()
                log_step("Project Configuration")
                print()
                
                # Get automation ID
                automation_id = input("Automation ID (e.g., com.company.my-automation): ").strip()
                if not automation_id:
                    log_error("Automation ID is required")
                    return False
                
                # Get automation name
                automation_name = input("Automation name: ").strip()
                if not automation_name:
                    automation_name = automation_id.split('.')[-1].replace('-', ' ').title()
                    log_info(f"Using default name: {automation_name}")
                
                # Get description
                description = input("Description (optional): ").strip()
                if not description:
                    description = f"Streamline automation: {automation_name}"
                
                # Get entry point
                entry_point = input("Entry point [default: main.py]: ").strip()
                if not entry_point:
                    entry_point = "main.py"
                
                # Get return mode
                print("\nReturn mode:")
                print("  1. stream (real-time output)")
                print("  2. sync (wait for completion)")
                return_mode_choice = input("Select (1/2) [default: 1]: ").strip()
                return_mode = "sync" if return_mode_choice == "2" else "stream"
                
                print()
                log_step("Generating project files...")
                
                # Process and copy files
                files_created = 0
                for file_path in template_root.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(template_root)
                        target_file = target_dir / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Read file content
                        content = file_path.read_text()
                        
                        # Replace placeholders in streamline.yaml
                        if file_path.name == 'streamline.yaml':
                            # Parse YAML
                            yaml_data = yaml.safe_load(content)
                            
                            # Update fields
                            yaml_data['automation_id'] = automation_id
                            yaml_data['name'] = automation_name
                            yaml_data['description'] = description
                            yaml_data['entry_point'] = entry_point
                            yaml_data['return_mode'] = return_mode
                            
                            # Write updated YAML
                            content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
                        
                        # Write file
                        target_file.write_text(content)
                        files_created += 1
                        log_ok(f"Created: {relative_path}")
                
                print()
                log_ok(f"Project initialized successfully!")
                log_info(f"Created {files_created} files in {target_dir}")
                print()
                print("Next steps:")
                print("  1. Edit main.py with your automation logic")
                print("  2. Add dependencies to requirements.txt")
                print("  3. Update streamline.yaml with parameters")
                print("  4. Run 'aitronos streamline upload' to deploy")
                print()
            
            return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again:")
        print("  aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        print()
        print("You don't have permission to access this resource.")
        print("Please contact your administrator.")
        print()
        return False
        
    except Exception as e:
        log_error(f"Failed to initialize project: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_project_structure():
    """Display expected project structure."""
    structure = """
Streamline Project Structure:
├── config.freddy.json      # Automation configuration
├── requirements.txt        # Python dependencies
├── documentation.txt       # Usage documentation
├── resources/
│   └── parameters.json     # Parameter schema
└── src/
    └── main.py             # Entry point
"""
    print(structure)

