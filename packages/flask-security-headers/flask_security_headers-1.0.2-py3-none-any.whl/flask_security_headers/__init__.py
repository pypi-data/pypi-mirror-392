"""
Flask-Security-Headers
======================

Security utilities for Flask applications.

Usage:
    from flask_security_headers import (
        is_safe_url,
        require_fresh_login,
        validate_password_strength
    )
"""

__version__ = "1.0.0"

from .security import (
    is_safe_url,
    get_client_ip,
    require_fresh_login,
    check_content_security,
    sanitize_filename,
    validate_password_strength,
)

__all__ = [
    "is_safe_url",
    "get_client_ip",
    "require_fresh_login",
    "check_content_security",
    "sanitize_filename",
    "validate_password_strength",
]
