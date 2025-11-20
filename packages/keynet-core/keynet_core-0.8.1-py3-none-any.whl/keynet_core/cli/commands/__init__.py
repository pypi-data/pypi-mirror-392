"""Common commands for keynet CLI."""

from .login import handle_login, setup_login_parser
from .logout import handle_logout, setup_logout_parser

__all__ = [
    "setup_login_parser",
    "handle_login",
    "setup_logout_parser",
    "handle_logout",
]
