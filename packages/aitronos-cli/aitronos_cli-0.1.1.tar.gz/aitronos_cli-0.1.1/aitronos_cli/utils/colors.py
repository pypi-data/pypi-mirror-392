"""ANSI color utilities for terminal output."""

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_CYAN = "\033[36m"
FG_GRAY = "\033[90m"

# Status indicators
OK = "✓"
ERROR = "✗"
INFO = "ℹ"
WARN = "⚠"
STEP = "→"


def log_ok(msg: str):
    """Print success message."""
    print(f"{FG_GREEN}{OK} [OK]{RESET}    {msg}")


def log_error(msg: str):
    """Print error message."""
    print(f"{FG_RED}{ERROR} [ERROR]{RESET} {msg}")


def log_info(msg: str):
    """Print info message."""
    print(f"{FG_BLUE}{INFO} [INFO]{RESET}  {msg}")


def log_warn(msg: str):
    """Print warning message."""
    print(f"{FG_YELLOW}{WARN} [WARN]{RESET}  {msg}")


def log_step(msg: str):
    """Print step message."""
    print(f"{FG_CYAN}{STEP}{RESET} {msg}")

