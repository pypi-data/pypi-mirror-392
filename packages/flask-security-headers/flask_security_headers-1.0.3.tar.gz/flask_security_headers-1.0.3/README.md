# Flask-Security-Headers

**Essential security utilities for Flask applications** - Prevent common vulnerabilities like open redirects, XSS attacks, and weak passwords with battle-tested helper functions.

[![PyPI version](https://badge.fury.io/py/flask-security-headers.svg)](https://pypi.org/project/flask-security-headers/)
[![Python Support](https://img.shields.io/pypi/pyversions/flask-security-headers.svg)](https://pypi.org/project/flask-security-headers/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Flask-Security-Headers?

Security shouldn't be an afterthought. This package provides production-ready security utilities that are:
- ✅ **Battle-tested** in production at [wallmarkets](https://wallmarkets.store)
- ✅ **Zero dependencies** beyond Flask
- ✅ **Easy to integrate** - just import and use
- ✅ **Well-documented** with real-world examples

## Features

### 🛡️ Open Redirect Prevention
Validate URLs before redirecting to prevent phishing attacks. Ensures redirects only go to your domain.

### 🔐 Password Strength Validation
Enforce strong passwords with customizable requirements:
- Minimum 8 characters
- Uppercase and lowercase letters
- Numbers and special characters
- Clear error messages for users

### ⏰ Fresh Login Requirement
Require recent authentication for sensitive operations (password changes, payment methods, etc.)

### 📁 Filename Sanitization
Prevent path traversal attacks by sanitizing uploaded filenames

### 🌐 Proxy-Aware IP Detection
Get the real client IP address, even behind proxies and load balancers

### 🔍 XSS Content Detection
Check user-submitted content for suspicious patterns before storing

## Installation

```bash
pip install flask-security-headers
```

## Quick Start

```bash
pip install flask-security-headers
```

## Usage Examples

### 1. Safe URL Validation (Prevent Open Redirects)

```python
from flask import redirect, request
from flask_security_headers import is_safe_url

@app.route('/redirect')
def safe_redirect():
    target = request.args.get('next', '/')
    if is_safe_url(target):
        return redirect(target)
    return redirect('/')
```

### 2. Require Fresh Login for Sensitive Operations

```python
from flask_security_headers import require_fresh_login

@app.route('/settings/password', methods=['POST'])
@require_fresh_login(timeout_minutes=30)
def change_password():
    # User must have logged in within last 30 minutes
    pass
```

### 3. Password Strength Validation

```python
from flask_security_headers import validate_password_strength

valid, msg = validate_password_strength(password)
if not valid:
    return {'error': msg}, 400
```

### 4. Filename Sanitization (Prevent Path Traversal)

```python
from flask_security_headers import sanitize_filename

filename = sanitize_filename(request.files['file'].filename)
# Safe to use in file paths
```

### 5. Get Client IP (Proxy-Aware)

```python
from flask_security_headers import get_client_ip

@app.route('/api/endpoint')
def endpoint():
    client_ip = get_client_ip()
    # Works correctly behind proxies, load balancers, CDNs
    app.logger.info(f"Request from {client_ip}")
```

### 6. Content Security Check

```python
from flask_security_headers import check_content_security

@app.route('/comment', methods=['POST'])
def post_comment():
    content = request.form['comment']
    is_safe, message = check_content_security(content)
    
    if not is_safe:
        return {'error': f'Suspicious content detected: {message}'}, 400
    
    # Safe to store
```

## Real-World Use Cases

### E-commerce Platform
```python
# Secure password reset flow
@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    new_password = request.form['password']
    
    # Validate password strength
    valid, msg = validate_password_strength(new_password)
    if not valid:
        flash(msg, 'error')
        return redirect(url_for('reset_password', token=token))
    
    # Update password...
    
    # Safe redirect
    next_url = request.args.get('next', '/')
    if is_safe_url(next_url):
        return redirect(next_url)
    return redirect('/')
```

### Admin Panel
```python
# Require fresh login for critical operations
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
@require_fresh_login(timeout_minutes=15)
def delete_user(user_id):
    # User must have logged in within last 15 minutes
    # Prevents session hijacking from causing damage
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users'))
```

### File Upload Service
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['document']
    
    # Sanitize filename to prevent path traversal
    safe_filename = sanitize_filename(file.filename)
    # "../../../etc/passwd" becomes "etc_passwd"
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], safe_filename))
```

## API Reference

### `is_safe_url(target: str) -> bool`
Validates if a URL is safe for redirect (same domain).

### `validate_password_strength(password: str) -> Tuple[bool, Optional[str]]`
Returns `(True, None)` if valid, or `(False, error_message)` if invalid.

### `require_fresh_login(timeout_minutes: int = 30)`
Decorator that requires recent authentication.

### `sanitize_filename(filename: str) -> str`
Removes dangerous characters and path components from filenames.

### `get_client_ip() -> str`
Returns the real client IP, respecting proxy headers if configured.

### `check_content_security(content: str) -> Tuple[bool, str]`
Checks content for suspicious patterns like script tags.

## Configuration

```python
# Enable proxy header trust (only if behind a trusted proxy!)
app.config['BEHIND_PROXY'] = True

# Customize password requirements (optional)
app.config['MIN_PASSWORD_LENGTH'] = 10
app.config['REQUIRE_SPECIAL_CHARS'] = True
```

## Security Best Practices

1. **Always validate redirects** - Use `is_safe_url()` before any `redirect()`
2. **Enforce strong passwords** - Use `validate_password_strength()` on registration/password change
3. **Require fresh login** - Use `@require_fresh_login()` for sensitive operations
4. **Sanitize filenames** - Always use `sanitize_filename()` for user uploads
5. **Log security events** - Track failed validation attempts

## Testing

```bash
pytest tests/
```

## Production Usage

This package is used in production at:
- [wallmarkets](https://wallmarkets.store) - Multi-vendor marketplace platform
- Handling thousands of daily requests
- Protecting sensitive user operations

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 📚 [Documentation](https://github.com/wallmarkets/flask-security-headers)
- 🐛 [Issue Tracker](https://github.com/wallmarkets/flask-security-headers/issues)
- 💬 [Discussions](https://github.com/wallmarkets/flask-security-headers/discussions)

## Related Packages

- [flask-ratelimit-simple](https://pypi.org/project/flask-ratelimit-simple/) - Rate limiting
- [flask-supercache](https://pypi.org/project/flask-supercache/) - Caching
- [flask-querymonitor](https://pypi.org/project/flask-querymonitor/) - Query optimization

---

**Made with ❤️ by the wallmarkets Team**
