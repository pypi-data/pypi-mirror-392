"""Terminal utilities for raw input handling."""

import sys
import tty
import termios
from typing import Optional


def get_key() -> Optional[str]:
    """
    Get a single keypress from terminal.
    
    Returns:
        Key name: 'up', 'down', 'left', 'right', 'enter', 'esc', or the character
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        
        # Handle escape sequences (arrow keys, etc.)
        if ch == '\x1b':
            # Read next two characters for arrow keys
            next_chars = sys.stdin.read(2)
            if next_chars == '[A':
                return 'up'
            elif next_chars == '[B':
                return 'down'
            elif next_chars == '[C':
                return 'right'
            elif next_chars == '[D':
                return 'left'
            else:
                return 'esc'
        elif ch == '\r' or ch == '\n':
            return 'enter'
        elif ch == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif ch == '\x04':  # Ctrl+D (EOF)
            return 'eof'
        else:
            return ch
            
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def clear_screen():
    """Clear the terminal screen."""
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()


def move_cursor(row: int, col: int):
    """Move cursor to specific position."""
    sys.stdout.write(f'\033[{row};{col}H')
    sys.stdout.flush()


def hide_cursor():
    """Hide the terminal cursor."""
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()


def show_cursor():
    """Show the terminal cursor."""
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

