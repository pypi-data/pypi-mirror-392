"""ANSI color codes for terminal output."""
# Copyright (c) 2024 FastStreamingAgent Contributors
from typing import Final


class Colors:
    """ANSI color codes for terminal styling."""

    RESET: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"

    # Text colors
    BLACK: Final[str] = "\033[30m"
    RED: Final[str] = "\033[31m"
    GREEN: Final[str] = "\033[32m"
    YELLOW: Final[str] = "\033[33m"
    BLUE: Final[str] = "\033[34m"
    MAGENTA: Final[str] = "\033[35m"
    CYAN: Final[str] = "\033[36m"
    WHITE: Final[str] = "\033[37m"

    # Bright colors
    BRIGHT_BLACK: Final[str] = "\033[90m"
    BRIGHT_RED: Final[str] = "\033[91m"
    BRIGHT_GREEN: Final[str] = "\033[92m"
    BRIGHT_YELLOW: Final[str] = "\033[93m"
    BRIGHT_BLUE: Final[str] = "\033[94m"
    BRIGHT_MAGENTA: Final[str] = "\033[95m"
    BRIGHT_CYAN: Final[str] = "\033[96m"
    BRIGHT_WHITE: Final[str] = "\033[97m"

    # Background colors
    BG_BLACK: Final[str] = "\033[40m"
    BG_RED: Final[str] = "\033[41m"
    BG_GREEN: Final[str] = "\033[42m"
    BG_YELLOW: Final[str] = "\033[43m"
    BG_BLUE: Final[str] = "\033[44m"
    BG_MAGENTA: Final[str] = "\033[45m"
    BG_CYAN: Final[str] = "\033[46m"
    BG_WHITE: Final[str] = "\033[47m"
