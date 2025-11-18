# Flask-Security-Headers

Security utilities for Flask applications.

## What it does

- **Open redirect prevention**: Validates URLs before redirecting
- **XSS detection**: Checks content for suspicious patterns
- **Password validation**: Enforces strength requirements
- **Fresh login requirement**: Re-auth for sensitive operations
- **Filename sanitization**: Prevents path traversal
- **Proxy-aware IP detection**: Gets real client IP

Built while working on [wallmarkets](https://wallmarkets.store).

## Installation

```bash
pip install flask-security-headers
```

## Usage

### Safe URL validation

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

### Require fresh login

```python
from flask_security_headers import require_fresh_login

@app.route('/settings/password', methods=['POST'])
@require_fresh_login(timeout_minutes=30)
def change_password():
    # User must have logged in within last 30 minutes
    pass
```

### Password validation

```python
from flask_security_headers import validate_password_strength

valid, msg = validate_password_strength(password)
if not valid:
    return {'error': msg}, 400
```

### Filename sanitization

```python
from flask_security_headers import sanitize_filename

filename = sanitize_filename(request.files['file'].filename)
# Safe to use in file paths
```

## License

MIT

## Contributing

Pull requests welcome. Please add tests.
