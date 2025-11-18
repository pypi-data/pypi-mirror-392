"""
Security utilities for Flask applications.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import current_app, redirect, request, url_for


def is_safe_url(target):
    """
    Validate URL to prevent open redirect vulnerabilities.

    Args:
        target: URL to validate

    Returns:
        bool: True if safe
    """
    if target is None:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_client_ip():
    """
    Get client IP. Only trusts X-Forwarded-For if BEHIND_PROXY is configured.

    Returns:
        str: Client IP address
    """
    if current_app.config.get("BEHIND_PROXY"):
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()

    return request.remote_addr or "127.0.0.1"


def require_fresh_login(timeout_minutes=30):
    """
    Decorator requiring recent login for sensitive operations.

    Args:
        timeout_minutes: Minutes before requiring fresh login
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from flask_login import current_user, logout_user

                if not current_user.is_authenticated:
                    return redirect(url_for("auth.login", next=request.url))

                last_login = getattr(current_user, "last_login", None)
                if not last_login or datetime.now(timezone.utc) - last_login > timedelta(
                    minutes=timeout_minutes
                ):
                    logout_user()
                    return redirect(url_for("auth.login", next=request.url))

                return f(*args, **kwargs)
            except ImportError:
                # If flask_login not available, just run the function
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_content_security(content):
    """
    Check content for XSS patterns.

    Args:
        content: Content to check

    Returns:
        tuple: (is_safe, message)
    """
    suspicious_patterns = [
        "<script",
        "javascript:",
        "data:text/html",
        "vbscript:",
        "onclick=",
        "onerror=",
        "onload=",
    ]

    content_lower = content.lower()
    for pattern in suspicious_patterns:
        if pattern in content_lower:
            return False, f"Suspicious content: {pattern}"
    return True, None


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    import os
    from werkzeug.utils import secure_filename

    safe_name = secure_filename(filename)
    safe_name = os.path.basename(safe_name)
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")

    return safe_name


def validate_password_strength(password):
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        tuple: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, None
