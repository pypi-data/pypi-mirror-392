"""Exit code constants for reerelease CLI.

Keep this module dependency-free so it can be imported from anywhere safely.
"""

# POSIX-style exit codes
OK = 0
GENERAL_ERROR = 1
USAGE_ERROR = 2

__all__ = ["OK", "GENERAL_ERROR", "USAGE_ERROR"]
