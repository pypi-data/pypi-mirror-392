"""Interactive menu system with custom arrow key navigation.

Navigation:
- Up/Down arrows: Navigate menu items
- Right arrow or Enter: Select highlighted item
- Left arrow or Esc: Go back to previous menu
"""

import sys
from typing import Optional, Callable

from aitronos_cli.utils.colors import BOLD, RESET, FG_CYAN, FG_GRAY
from aitronos_cli.utils.terminal import get_key, clear_screen, hide_cursor, show_cursor


class MenuSystem:
    """Interactive menu system with custom arrow key handling."""
    
    def __init__(self):
        self.breadcrumbs = []
    
    def show_header(self):
        """Display CLI header."""
        print(f"\n{BOLD}Aitronos CLI{RESET}")
        print(f"{FG_GRAY}{'━' * 60}{RESET}")
        
        if self.breadcrumbs:
            breadcrumb_str = " > ".join(self.breadcrumbs)
            print(f"{FG_CYAN}{breadcrumb_str}{RESET}")
        
        print(f"{FG_GRAY}Navigation: ↑↓ move | → or Enter select | ← back{RESET}")
        print()
    
    def show_menu(
        self,
        title: str,
        options: list[str],
        handlers: dict[str, Callable]
    ) -> Optional[str]:
        """
        Show menu and handle selection with custom arrow key navigation.
        
        Navigation:
        - Up/Down arrows: Navigate menu
        - Right arrow or Enter: Select item
        - Left arrow or Esc: Go back
        
        Args:
            title: Menu title
            options: List of menu options
            handlers: Dict mapping option to handler function
            
        Returns:
            Selected option or None if back/exit
        """
        selected_index = 0
        
        while True:
            # Clear and redraw
            clear_screen()
            self.show_header()
            
            print(f"{BOLD}{title}{RESET}")
            for i, option in enumerate(options):
                if i == selected_index:
                    print(f"{FG_CYAN}❯ {option}{RESET}")
                else:
                    print(f"  {option}")
            
            # Get key press
            try:
                key = get_key()
            except KeyboardInterrupt:
                show_cursor()
                print("\n\nExiting...")
                sys.exit(0)
            
            # Handle navigation
            if key == 'up':
                selected_index = (selected_index - 1) % len(options)
            elif key == 'down':
                selected_index = (selected_index + 1) % len(options)
            elif key in ['right', 'enter']:
                # Select item
                selected_option = options[selected_index]
                
                # Handle special options
                if selected_option in ["← Back", "Exit"]:
                    show_cursor()
                    return selected_option
                
                # Call handler if exists
                if selected_option in handlers:
                    show_cursor()
                    clear_screen()
                    handlers[selected_option]()
                    input("\nPress Enter to continue...")
                
                return selected_option
            elif key in ['left', 'esc']:
                # Go back
                show_cursor()
                return "← Back"
    
    def main_menu(self, handlers: dict):
        """Display main menu."""
        self.breadcrumbs = ["Main Menu"]
        
        options = [
            "Streamline",
            "Assistants (Coming Soon)",
            "Configuration",
            "Authentication",
            "Exit"
        ]
        
        while True:
            selection = self.show_menu("Main Menu", options, handlers)
            
            if selection == "Exit" or selection is None:
                show_cursor()
                break
    
    def streamline_menu(self, handlers: dict):
        """Display Streamline submenu."""
        self.breadcrumbs = ["Main Menu", "Streamline"]
        
        options = [
            "Initialize Project (Single Automation)",
            "Initialize Repository (Multi-Automation)",
            "Upload (Manual)",
            "Upload (GitHub Sync)",
            "List Automations",
            "List Automations (Verbose)",
            "Execute Automation",
            "View Logs",
            "Sync Git Automation",
            "Delete Automation",
            "Set Schedule",
            "Remove Schedule",
            "← Back"
        ]
        
        while True:
            selection = self.show_menu("Streamline", options, handlers)
            
            if selection == "← Back" or selection is None:
                break
    
    def config_menu(self, handlers: dict):
        """Display Configuration submenu."""
        self.breadcrumbs = ["Main Menu", "Configuration"]
        
        options = [
            "Set Config Value",
            "Get Config Value",
            "List All Config",
            "← Back"
        ]
        
        while True:
            selection = self.show_menu("Configuration", options, handlers)
            
            if selection == "← Back" or selection is None:
                break
    
    def auth_menu(self, handlers: dict):
        """Display Authentication submenu."""
        self.breadcrumbs = ["Main Menu", "Authentication"]
        
        options = [
            "Login",
            "Logout",
            "Show Status",
            "Refresh Token",
            "← Back"
        ]
        
        while True:
            selection = self.show_menu("Authentication", options, handlers)
            
            if selection == "← Back" or selection is None:
                break


# Global menu instance
menu_system = MenuSystem()
