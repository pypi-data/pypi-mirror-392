"""Main CLI entry point for Aitronos CLI."""

import sys

from aitronos_cli.config import config
from aitronos_cli.auth import auth_manager
from aitronos_cli.menu import menu_system
from aitronos_cli.streamline import project, upload
from aitronos_cli.utils.colors import (
    log_ok, log_error, log_info, log_warn,
    BOLD, RESET, FG_CYAN, FG_GRAY
)


def show_header():
    """Display CLI header."""
    print(f"\n{BOLD}Aitronos CLI{RESET}")
    print(f"{FG_GRAY}{'━' * 60}{RESET}")
    print(f"Type {FG_CYAN}help{RESET} for available commands, {FG_CYAN}quit{RESET} to exit")
    print(f"{FG_GRAY}{'━' * 60}{RESET}\n")


def show_help():
    """Display help information."""
    help_text = f"""
{BOLD}Aitronos CLI{RESET}

{BOLD}Interactive Mode:{RESET}
  {FG_CYAN}aitronos{RESET}                          Start interactive mode
  {FG_CYAN}aitronos start{RESET}                    Start interactive mode (explicit)
  {FG_CYAN}aitronos i{RESET}                        Start interactive mode (shorthand)

{BOLD}Authentication Commands:{RESET}
  {FG_CYAN}aitronos login{RESET}                    Quick login (shortcut)
  {FG_CYAN}aitronos auth login{RESET}              Login with email/password + 2FA
  {FG_CYAN}aitronos auth logout{RESET}             Logout and clear tokens
  {FG_CYAN}aitronos auth status{RESET}             Show authentication status
  {FG_CYAN}aitronos auth refresh{RESET}            Refresh access token

{BOLD}Streamline Commands:{RESET}
  {FG_CYAN}aitronos streamline project init [--repo] [dir]{RESET}
                                           Initialize new project or repository
                                           --repo: Create multi-automation repository
  {FG_CYAN}aitronos streamline upload{RESET}              Upload automation (manual)
  {FG_CYAN}aitronos streamline upload-github{RESET}       Link GitHub repository
  {FG_CYAN}aitronos streamline list{RESET}                List all automations
  {FG_CYAN}aitronos streamline list -v{RESET}             List with details (verbose)
  {FG_CYAN}aitronos streamline execute <id>{RESET}        Execute automation
  {FG_CYAN}aitronos streamline logs <id>{RESET}           View execution logs
  {FG_CYAN}aitronos streamline sync <id>{RESET}           Manually sync Git automation
  {FG_CYAN}aitronos streamline delete <id>{RESET}         Delete automation
  {FG_CYAN}aitronos streamline schedule <id> <cron>{RESET} Set schedule
  {FG_CYAN}aitronos streamline schedule-remove <id>{RESET} Remove schedule

{BOLD}Configuration Commands:{RESET}
  {FG_CYAN}aitronos config set <key> <value>{RESET} Set configuration value
  {FG_CYAN}aitronos config get <key>{RESET}         Get configuration value
  {FG_CYAN}aitronos config list{RESET}              List all configuration

{BOLD}General Commands:{RESET}
  {FG_CYAN}aitronos{RESET}                          Start interactive mode
  {FG_CYAN}aitronos help{RESET}                     Show this help
  {FG_CYAN}aitronos version{RESET}                  Show version

{BOLD}Interactive Mode:{RESET}
  Run {FG_CYAN}aitronos{RESET} without arguments to enter interactive mode.
  
  Navigation:
    ↑↓ arrows    - Move between menu items
    → or Enter   - Select highlighted item
    ←            - Go back to previous menu
  
  Note: Authentication required for all commands except login/help
"""
    print(help_text)


def cmd_auth(args):
    """Handle auth commands."""
    if not args:
        log_error("Usage: aitronos auth <login|logout|status|refresh>")
        return
    
    subcommand = args[0]
    
    if subcommand == 'login':
        # Check for dev credentials in environment
        import os
        dev_email = os.getenv('AITRONOS_DEV_EMAIL')
        dev_password = os.getenv('AITRONOS_DEV_PASSWORD')
        
        if dev_email and dev_password:
            log_info(f"Using dev credentials from .env: {dev_email}")
            email_or_username = dev_email
            password = dev_password
        else:
            email_or_username = input("Email or username: ").strip()
            if not email_or_username:
                log_error("Email/username required")
                return
            
            from getpass import getpass
            password = getpass("Password: ")
            if not password:
                log_error("Password required")
                return
        
        auth_manager.login(email_or_username, password)
    
    elif subcommand == 'logout':
        auth_manager.logout()
    
    elif subcommand == 'status':
        auth_manager.show_status()
    
    elif subcommand == 'refresh':
        if auth_manager.refresh_access_token():
            log_ok("Access token refreshed")
        else:
            log_error("Failed to refresh token")
    
    else:
        log_error(f"Unknown auth command: {subcommand}")


def cmd_streamline(args):
    """Handle streamline commands."""
    if not args:
        log_error("Usage: aitronos streamline <command>")
        return
    
    subcommand = args[0]
    subargs = args[1:]
    
    if subcommand == 'project' and subargs and subargs[0] == 'init':
        # Check for --repo flag
        is_repo = '--repo' in subargs
        directory = None
        
        # Extract directory if provided (not a flag)
        for arg in subargs[1:]:
            if not arg.startswith('--'):
                directory = arg
                break
        
        project.init_project(directory=directory, is_repo=is_repo)
    
    elif subcommand == 'upload':
        directory = subargs[0] if subargs else None
        upload.upload_manual(directory)
    
    elif subcommand == 'upload-github':
        repo_url = subargs[0] if subargs else None
        upload.upload_github(repo_url)
    
    elif subcommand == 'list':
        # Check for verbose flag
        verbose = '-v' in subargs or '--verbose' in subargs
        upload.list_automations(verbose=verbose)
    
    elif subcommand == 'execute':
        automation_id = subargs[0] if subargs else None
        upload.execute_automation(automation_id)
    
    elif subcommand == 'logs':
        execution_id = subargs[0] if subargs else None
        upload.view_logs(execution_id)
    
    elif subcommand == 'delete':
        automation_id = subargs[0] if subargs else None
        upload.delete_automation(automation_id)
    
    elif subcommand == 'schedule':
        if len(subargs) >= 2:
            automation_id = subargs[0]
            cron_expression = subargs[1]
            upload.schedule_automation(automation_id, cron_expression)
        elif len(subargs) == 1:
            automation_id = subargs[0]
            upload.schedule_automation(automation_id)
        else:
            upload.schedule_automation()
    
    elif subcommand == 'schedule-remove':
        automation_id = subargs[0] if subargs else None
        upload.remove_schedule(automation_id)
    
    else:
        log_error(f"Unknown streamline command: {subcommand}")


def cmd_config(args):
    """Handle config commands."""
    if not args:
        log_error("Usage: aitronos config <set|get|list>")
        return
    
    subcommand = args[0]
    
    if subcommand == 'set':
        if len(args) < 3:
            log_error("Usage: aitronos config set <key> <value>")
            return
        key, value = args[1], args[2]
        config.set(key, value)
        
        # Mask sensitive values
        display_value = value
        if 'token' in key.lower() or 'secret' in key.lower():
            display_value = '*' * 8 + value[-4:] if len(value) > 4 else '****'
        
        log_ok(f"Set {key} = {display_value}")
    
    elif subcommand == 'get':
        if len(args) < 2:
            log_error("Usage: aitronos config get <key>")
            return
        key = args[1]
        value = config.get(key)
        if value:
            print(value)
        else:
            log_warn(f"Key '{key}' not found")
    
    elif subcommand == 'list':
        config_data = config.list_all()
        if not config_data:
            log_info("No configuration set")
            return
        
        print(f"{BOLD}Configuration:{RESET}")
        for key, value in config_data.items():
            # Mask sensitive values
            if 'token' in key.lower() or 'secret' in key.lower():
                value = '*' * 8 + value[-4:] if len(value) > 4 else '****'
            print(f"  {key}: {value}")
    
    else:
        log_error(f"Unknown config command: {subcommand}")


def select_organization():
    """Fetch and select organization."""
    from aitronos_cli.api_client import AitronosAPIClient
    
    api_url = config.get_api_url()
    token = auth_manager.get_access_token()
    
    if not token:
        log_error("Not authenticated")
        return False
    
    client = AitronosAPIClient(api_url, token)
    
    try:
        log_info("Fetching organizations...")
        response = client.list_organizations()
        organizations = response.get('organizations', [])
        
        if not organizations:
            log_error("No organizations found")
            return False
        
        if len(organizations) == 1:
            # Only one org, auto-select it
            org = organizations[0]
            org_id = org.get('id')
            org_name = org.get('name', 'Unknown')
            auth_manager.set_organization_id(org_id)
            log_ok(f"Auto-selected organization: {org_name}")
            return True
        
        # Multiple organizations, show selection menu
        print("\n" + "="*60)
        print("Select Organization:")
        print("="*60)
        
        for idx, org in enumerate(organizations, 1):
            org_name = org.get('name', 'Unknown')
            org_id = org.get('id')
            print(f"  {idx}. {org_name} ({org_id})")
        
        print()
        choice = input("Enter number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            return False
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(organizations):
                org = organizations[idx]
                org_id = org.get('id')
                org_name = org.get('name', 'Unknown')
                auth_manager.set_organization_id(org_id)
                log_ok(f"Selected organization: {org_name}")
                return True
            else:
                log_error("Invalid selection")
                return False
        except ValueError:
            log_error("Invalid input")
            return False
            
    except Exception as e:
        log_error(f"Failed to fetch organizations: {str(e)}")
        return False


def interactive_mode():
    """Start interactive mode with menu navigation."""
    # Check authentication
    if not auth_manager.is_authenticated():
        print("\n" + "="*60)
        log_warn("Authentication required to use Aitronos CLI")
        print("="*60 + "\n")

        # Check for dev credentials in environment
        import os
        dev_email = os.getenv('AITRONOS_DEV_EMAIL')
        dev_password = os.getenv('AITRONOS_DEV_PASSWORD')

        if dev_email and dev_password:
            log_info(f"Using dev credentials from .env: {dev_email}")
            email = dev_email
            password = dev_password
        else:
            email = input("Email or username: ").strip()
            if not email:
                log_error("Email/username required. Exiting.")
                sys.exit(1)

            import getpass
            password = getpass.getpass("Password: ").strip()
            if not password:
                log_error("Password required. Exiting.")
                sys.exit(1)

        if not auth_manager.login(email, password):
            log_error("Login failed. Exiting.")
            sys.exit(1)

        print()  # Spacing
    
    # Check if organization is selected
    if not auth_manager.get_organization_id():
        if not select_organization():
            log_error("Organization selection required. Exiting.")
            sys.exit(1)
        print()  # Spacing
    
    # Main menu handlers
    def handle_streamline():
        def handle_project_init():
            project.init_project(is_repo=False)
            input("\nPress Enter to continue...")
        
        def handle_repo_init():
            project.init_project(is_repo=True)
            input("\nPress Enter to continue...")
        
        streamline_handlers = {
            "Initialize Project (Single Automation)": handle_project_init,
            "Initialize Repository (Multi-Automation)": handle_repo_init,
            "Upload (Manual)": lambda: upload.upload_manual(),
            "Upload (GitHub Sync)": lambda: upload.upload_github(),
            "List Automations": lambda: upload.list_automations(),
            "List Automations (Verbose)": lambda: upload.list_automations(verbose=True),
            "Execute Automation": lambda: upload.execute_automation(),
            "View Logs": lambda: upload.view_logs(),
            "Sync Git Automation": lambda: upload.sync_automation(),
            "Delete Automation": lambda: upload.delete_automation(),
            "Set Schedule": lambda: upload.schedule_automation(),
            "Remove Schedule": lambda: upload.remove_schedule(),
        }
        menu_system.streamline_menu(streamline_handlers)
    
    def handle_assistants():
        log_warn("Assistant commands coming soon")
        input("\nPress Enter to continue...")
    
    def handle_config():
        config_handlers = {
            "Set Config Value": lambda: cmd_config(['set'] + input("Key: ").split() + input("Value: ").split()),
            "Get Config Value": lambda: cmd_config(['get', input("Key: ").strip()]),
            "List All Config": lambda: cmd_config(['list']),
        }
        menu_system.config_menu(config_handlers)
    
    def handle_auth():
        auth_handlers = {
            "Login": lambda: cmd_auth(['login']),
            "Logout": lambda: cmd_auth(['logout']),
            "Show Status": lambda: cmd_auth(['status']),
            "Refresh Token": lambda: cmd_auth(['refresh']),
        }
        menu_system.auth_menu(auth_handlers)
    
    def handle_change_org():
        select_organization()
        input("\nPress Enter to continue...")
    
    main_handlers = {
        "Streamline": handle_streamline,
        "Change Organization": handle_change_org,
        "Assistants (Coming Soon)": handle_assistants,
        "Configuration": handle_config,
        "Authentication": handle_auth,
    }
    
    menu_system.main_menu(main_handlers)


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    # Interactive mode triggers
    if not args or (args and args[0] in ['start', 'i', 'interactive']):
        interactive_mode()
        return
    
    command = args[0]
    command_args = args[1:]
    
    # Handle commands
    if command == 'help' or command == '--help' or command == '-h':
        show_help()
    elif command == 'login':
        # Shortcut for login
        cmd_auth(['login'])
    
    elif command == 'version' or command == '--version' or command == '-v':
        from aitronos_cli import __version__
        print(f"Aitronos CLI v{__version__}")
    
    elif command == 'auth':
        cmd_auth(command_args)
    
    elif command == 'streamline':
        cmd_streamline(command_args)
    
    elif command == 'config':
        cmd_config(command_args)
    
    else:
        log_error(f"Unknown command: {command}")
        log_info("Run 'aitronos help' for available commands")
        sys.exit(1)


if __name__ == '__main__':
    main()

