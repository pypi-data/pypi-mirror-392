"""Streamline automation upload commands."""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Optional

from aitronos_cli.config import config
from aitronos_cli.auth import auth_manager
from aitronos_cli.api_client import AitronosAPIClient, AuthenticationError, AuthorizationError
from aitronos_cli.utils.colors import log_ok, log_error, log_info, log_step, log_warn
from aitronos_cli.utils.validators import validate_streamline_yaml, validate_github_url


def upload_manual(directory: Optional[str] = None):
    """
    Upload automation from directory (manual upload).
    
    Uploads to Freddy Backend which proxies to Streamline.
    
    Args:
        directory: Directory containing automation (defaults to current directory)
    """
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Determine source directory
    source_dir = Path(directory) if directory else Path.cwd()
    if not source_dir.exists() or not source_dir.is_dir():
        log_error(f"Directory not found: {source_dir}")
        return False
    
    log_step(f"Uploading automation from {source_dir}...")
    
    # Validate streamline.yaml
    config_file = source_dir / "streamline.yaml"
    is_valid, error_msg = validate_streamline_yaml(config_file)
    
    if not is_valid:
        log_error(f"Validation failed: {error_msg}")
        return False
    
    log_ok("streamline.yaml is valid")
    
    # Get automation name
    automation_name = input("Automation name: ").strip()
    if not automation_name:
        log_error("Automation name is required")
        return False
    
    # Create ZIP file
    log_info("Creating ZIP archive...")
    
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
        zip_path = Path(tmp_file.name)
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            for root, dirs, files in os.walk(source_dir):
                # Skip hidden directories and common excludes
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
                
                for file in files:
                    # Skip hidden files and common excludes
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
        
        zip_size = zip_path.stat().st_size
        log_ok(f"Created ZIP archive ({file_count} files, {zip_size / 1024:.1f} KB)")
        
        # Check file size
        if zip_size > 10 * 1024 * 1024:  # 10MB
            log_error("ZIP file exceeds 10MB limit")
            return False
        
        # Upload to Freddy Backend
        log_info("Uploading to Freddy Backend...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.upload_automation(
            zip_file_path=zip_path,
            automation_name=automation_name
        )
        
        automation_id = response.get('automation_id')
        
        log_ok("Automation uploaded successfully!")
        print(f"  Automation ID: {automation_id}")
        print(f"  Name: {automation_name}")
        print()
        print("Next steps:")
        print(f"  - Execute: aitronos streamline execute {automation_id}")
        print(f"  - View logs: aitronos streamline logs <execution_id>")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        print()
        print("You don't have permission to upload automations.")
        print()
        return False
        
    except Exception as e:
        log_error(f"Upload failed: {str(e)}")
        return False
        
    finally:
        # Clean up temporary ZIP file
        if zip_path.exists():
            zip_path.unlink()


def upload_github(repository_url: Optional[str] = None):
    """
    Link GitHub repository for automatic sync.
    
    Sends to Freddy Backend which coordinates with Streamline and GitHub.
    
    Args:
        repository_url: GitHub repository URL
    """
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    log_step("Setting up GitHub repository sync...")
    
    # Get repository URL
    if not repository_url:
        repository_url = input("GitHub repository URL: ").strip()
    
    if not repository_url:
        log_error("Repository URL is required")
        return False
    
    if not validate_github_url(repository_url):
        log_error("Invalid GitHub URL format")
        log_info("Expected: https://github.com/user/repo")
        return False
    
    # Get branch
    branch = input("Branch (default: main): ").strip()
    if not branch:
        branch = "main"
    
    # Get automation name
    automation_name = input("Automation name: ").strip()
    if not automation_name:
        # Extract from repo URL
        automation_name = repository_url.rstrip('/').split('/')[-1].replace('.git', '')
        log_info(f"Using repository name: {automation_name}")
    
    # Get GitHub token
    github_token = config.get('github_token')
    if not github_token:
        github_token = input("GitHub personal access token: ").strip()
        if not github_token:
            log_error("GitHub token is required")
            return False
        
        # Ask to save token
        save_token = input("Save token for future use? (yes/no): ").strip().lower()
        if save_token == 'yes':
            config.set('github_token', github_token)
            log_ok("Token saved")
    
    try:
        # Send to Freddy Backend
        log_info("Linking repository via Freddy Backend...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.link_github_repo(
            repository_url=repository_url,
            branch=branch,
            github_token=github_token,
            automation_name=automation_name
        )
        
        automation_id = response.get('automation_id')
        webhook_url = response.get('webhook_url')
        
        log_ok("Repository linked successfully!")
        print(f"  Automation ID: {automation_id}")
        print(f"  Repository: {repository_url}")
        print(f"  Branch: {branch}")
        print(f"  Webhook URL: {webhook_url}")
        print()
        log_info("Webhook configured - pushes will auto-sync")
        print()
        print("Next steps:")
        print(f"  - Execute: aitronos streamline execute {automation_id}")
        print("  - Push to repository to trigger auto-sync")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        print()
        print("You don't have permission to link GitHub repositories.")
        print()
        return False
        
    except Exception as e:
        log_error(f"GitHub link failed: {str(e)}")
        return False


def list_automations(verbose: bool = False):
    """
    List all automations for user's organization.
    
    Args:
        verbose: If True, show detailed information
    """
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get user info
    user_info = auth_manager.get_user_info()
    organization_id = user_info.get('organization_id')
    
    if not organization_id:
        log_error("Organization ID not found. Please login again.")
        return False
    
    try:
        # Query Freddy Backend
        log_info("Fetching automations...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.list_automations(organization_id)
        automations = response.get('automations', [])
        
        if not automations:
            log_info("No automations found")
            print()
            print("Create your first automation:")
            print("  1. Run: aitronos streamline project init")
            print("  2. Edit the generated files")
            print("  3. Run: aitronos streamline upload")
            print()
            return True
        
        log_ok(f"Found {len(automations)} automation(s)")
        print()
        
        for auto in automations:
            print(f"  {auto.get('name')}")
            print(f"    ID: {auto.get('id')}")
            
            if verbose:
                # Show detailed information
                print(f"    Automation ID: {auto.get('automation_id', 'N/A')}")
                print(f"    Description: {auto.get('description', 'N/A')}")
                print(f"    Upload Method: {auto.get('upload_method', 'N/A')}")
                print(f"    Active: {auto.get('is_active', False)}")
                print(f"    Executions: {auto.get('execution_count', 0)}")
                
                # Show GitHub info if applicable
                if auto.get('upload_method') == 'github':
                    print(f"    Repository: {auto.get('repository_url', 'N/A')}")
                    print(f"    Branch: {auto.get('branch', 'N/A')}")
                
                # Show schedule info if present
                if auto.get('schedule_enabled'):
                    print(f"    Schedule: {auto.get('schedule_cron', 'N/A')}")
                    print(f"    Next Run: {auto.get('next_run', 'N/A')}")
                
                # Show timestamps
                print(f"    Created: {auto.get('created_at', 'N/A')}")
                print(f"    Updated: {auto.get('updated_at', 'N/A')}")
            else:
                # Show basic information
                print(f"    Status: {'Active' if auto.get('is_active') else 'Inactive'}")
                print(f"    Executions: {auto.get('execution_count', 0)}")
                
                # Show schedule if present
                if auto.get('schedule_enabled'):
                    print(f"    Schedule: {auto.get('schedule_cron', 'N/A')}")
            
            print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to list automations: {str(e)}")
        return False


def execute_automation(automation_id: Optional[str] = None):
    """Execute automation with parameters."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get automation ID
    if not automation_id:
        automation_id = input("Automation ID: ").strip()
    
    if not automation_id:
        log_error("Automation ID is required")
        return False
    
    # Get parameters (optional)
    print()
    log_info("Parameters (optional, press Enter to skip)")
    parameters = {}
    
    while True:
        key = input("  Parameter name (or Enter to finish): ").strip()
        if not key:
            break
        value = input(f"  Value for '{key}': ").strip()
        parameters[key] = value
    
    try:
        # Execute via Freddy Backend
        log_step(f"Executing automation {automation_id}...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.execute_automation(automation_id, parameters)
        
        execution_id = response.get('execution_id')
        status = response.get('status')
        
        log_ok("Execution started!")
        print(f"  Execution ID: {execution_id}")
        print(f"  Status: {status}")
        print()
        print("View logs:")
        print(f"  aitronos streamline logs {execution_id}")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Execution failed: {str(e)}")
        return False


def view_logs(execution_id: Optional[str] = None):
    """View execution logs."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get execution ID
    if not execution_id:
        execution_id = input("Execution ID: ").strip()
    
    if not execution_id:
        log_error("Execution ID is required")
        return False
    
    try:
        # Get logs via Freddy Backend
        log_info(f"Fetching logs for {execution_id}...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.get_execution_logs(execution_id)
        
        print()
        print(f"Execution: {response.get('id')}")
        print(f"Automation: {response.get('automation_id')}")
        print(f"Status: {response.get('status')}")
        print(f"Started: {response.get('started_at', 'N/A')}")
        print(f"Completed: {response.get('completed_at', 'N/A')}")
        print()
        
        logs = response.get('logs')
        if logs:
            print("Logs:")
            print("─" * 60)
            print(logs)
            print("─" * 60)
            print()
        
        result = response.get('result')
        if result:
            print("Result:")
            print(result)
            print()
        
        error_message = response.get('error_message')
        if error_message:
            log_error("Error:")
            print(error_message)
            print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to fetch logs: {str(e)}")
        return False


def sync_automation(automation_id: Optional[str] = None):
    """Manually trigger Git sync for an automation."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    if not automation_id:
        automation_id = input("Automation ID: ").strip()
    
    if not automation_id:
        log_error("Automation ID is required")
        return False
    
    log_info(f"Triggering sync for automation {automation_id}...")
    
    try:
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.sync_git_automation(automation_id)
        
        success = response.get('success')
        updated = response.get('updated')
        message = response.get('message', '')
        
        if success:
            if updated:
                log_ok("Automation synced and updated successfully!")
                if message:
                    print(f"  {message}")
            else:
                log_info("Automation is already up to date")
                if message:
                    print(f"  {message}")
        else:
            log_error(f"Sync failed: {message}")
        
        return success
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to sync automation: {str(e)}")
        return False


def delete_automation(automation_id: Optional[str] = None):
    """Delete automation with confirmation."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get automation ID
    if not automation_id:
        automation_id = input("Automation ID: ").strip()
    
    if not automation_id:
        log_error("Automation ID is required")
        return False
    
    # Confirmation
    print()
    log_warn(f"You are about to delete automation: {automation_id}")
    print("This action cannot be undone.")
    confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
    
    if confirm != 'yes':
        log_info("Deletion cancelled")
        return False
    
    try:
        # Delete via Freddy Backend
        log_step(f"Deleting automation {automation_id}...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.delete_automation(automation_id)
        
        log_ok("Automation deleted successfully!")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to delete automation: {str(e)}")
        return False


def schedule_automation(automation_id: Optional[str] = None, cron_expression: Optional[str] = None):
    """Set schedule for automation."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get automation ID
    if not automation_id:
        automation_id = input("Automation ID: ").strip()
    
    if not automation_id:
        log_error("Automation ID is required")
        return False
    
    # Get cron expression
    if not cron_expression:
        print()
        print("Cron expression examples:")
        print("  0 0 * * *     - Daily at midnight")
        print("  0 */6 * * *   - Every 6 hours")
        print("  0 9 * * 1     - Every Monday at 9 AM")
        print("  */15 * * * *  - Every 15 minutes")
        print()
        cron_expression = input("Cron expression: ").strip()
    
    if not cron_expression:
        log_error("Cron expression is required")
        return False
    
    try:
        # Set schedule via Freddy Backend
        log_step(f"Setting schedule for automation {automation_id}...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.set_schedule(automation_id, cron_expression)
        
        log_ok("Schedule set successfully!")
        print(f"  Automation ID: {automation_id}")
        print(f"  Schedule: {cron_expression}")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to set schedule: {str(e)}")
        return False


def remove_schedule(automation_id: Optional[str] = None):
    """Remove schedule from automation."""
    # Check authentication
    if not auth_manager.is_authenticated():
        log_error("Authentication required")
        log_info("Run 'aitronos auth login' to authenticate")
        return False
    
    # Get automation ID
    if not automation_id:
        automation_id = input("Automation ID: ").strip()
    
    if not automation_id:
        log_error("Automation ID is required")
        return False
    
    try:
        # Remove schedule via Freddy Backend
        log_step(f"Removing schedule from automation {automation_id}...")
        
        api_url = config.get_api_url()
        access_token = auth_manager.get_access_token()
        client = AitronosAPIClient(api_url, access_token)
        
        response = client.remove_schedule(automation_id)
        
        log_ok("Schedule removed successfully!")
        print()
        
        return True
    
    except AuthenticationError as e:
        log_error(f"Authentication failed: {str(e)}")
        print()
        print("Your session has expired or is invalid.")
        print("Please log in again: aitronos auth login")
        print()
        return False
    
    except AuthorizationError as e:
        log_error(f"Access denied: {str(e)}")
        return False
        
    except Exception as e:
        log_error(f"Failed to remove schedule: {str(e)}")
        return False

