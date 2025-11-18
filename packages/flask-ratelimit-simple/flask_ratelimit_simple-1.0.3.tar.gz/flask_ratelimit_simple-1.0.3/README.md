# Flask-RateLimit-Simple

**Lightweight, in-memory rate limiting for Flask** - Protect your API endpoints from abuse without the complexity of Redis or external dependencies.

[![PyPI version](https://badge.fury.io/py/flask-ratelimit-simple.svg)](https://pypi.org/project/flask-ratelimit-simple/)
[![Python Support](https://img.shields.io/pypi/pyversions/flask-ratelimit-simple.svg)](https://pypi.org/project/flask-ratelimit-simple/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Flask-RateLimit-Simple?

Most rate limiting solutions require Redis or Memcached. This package uses **in-memory storage** with automatic cleanup, making it:
- ✅ **Zero external dependencies** - No Redis, no Memcached
- ✅ **Production-ready** - Battle-tested at [wallmarkets](https://wallmarkets.store)
- ✅ **Standards-compliant** - Returns proper `X-RateLimit-*` headers
- ✅ **Smart tracking** - IP-based for anonymous, user-based for authenticated

## Features

### 🚀 Simple Decorator API
Just add `@rate_limit()` to any route - no complex setup required

### 📊 Standard Rate Limit Headers
Returns RFC-compliant headers:
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Seconds until limit resets
- `Retry-After` - When to retry (on 429 responses)

### 🎯 Smart User Tracking
- **Anonymous users**: Tracked by IP address
- **Authenticated users**: Tracked by user ID (via Flask-Login)
- **Automatic detection**: No configuration needed

### 🧹 Automatic Cleanup
Expired entries are automatically removed - no memory leaks

### 🔧 Flexible Configuration
Set different limits for different endpoints

## Installation

```bash
pip install flask-ratelimit-simple
```

## Quick Start

```bash
pip install flask-ratelimit-simple
```

## Usage Examples

### Basic Rate Limiting

```python
from flask import Flask
from flask_ratelimit_simple import rate_limit

app = Flask(__name__)

# Limit login attempts: 5 per 5 minutes
@app.route('/login', methods=['POST'])
@rate_limit('login', limit=5, period=300)
def login():
    # Your login logic here
    return {'message': 'Login successful'}

# Limit API calls: 100 per minute
@app.route('/api/data')
@rate_limit('api_data', limit=100, period=60)
def get_data():
    return {'data': [...]}  

# Limit password resets: 3 per hour
@app.route('/reset-password', methods=['POST'])
@rate_limit('password_reset', limit=3, period=3600)
def reset_password():
    # Send reset email
    return {'message': 'Reset email sent'}
```

### Different Limits for Different Endpoints

```python
# Strict limit for authentication
@app.route('/api/auth/login', methods=['POST'])
@rate_limit('auth_login', limit=5, period=300)  # 5 per 5min
def api_login():
    pass

# Generous limit for public data
@app.route('/api/products')
@rate_limit('products_list', limit=1000, period=3600)  # 1000 per hour
def list_products():
    pass

# Very strict for expensive operations
@app.route('/api/export', methods=['POST'])
@rate_limit('data_export', limit=2, period=86400)  # 2 per day
def export_data():
    pass
```

## Response Headers

### Successful Request (200 OK)
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 42
```

### Rate Limit Exceeded (429 Too Many Requests)
```http
HTTP/1.1 429 TOO MANY REQUESTS
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 247
Retry-After: 247
Content-Type: application/json

{"error": "Rate limit exceeded. Try again in 247 seconds."}
```

## Real-World Use Cases

### API Protection
```python
# Protect your API from abuse
@app.route('/api/v1/search', methods=['POST'])
@rate_limit('api_search', limit=30, period=60)  # 30 searches per minute
def search_api():
    query = request.json.get('query')
    results = perform_expensive_search(query)
    return {'results': results}
```

### Authentication Security
```python
# Prevent brute force attacks
@app.route('/login', methods=['POST'])
@rate_limit('login_attempts', limit=5, period=900)  # 5 attempts per 15min
def login():
    username = request.form['username']
    password = request.form['password']
    
    if verify_credentials(username, password):
        return redirect('/dashboard')
    
    return {'error': 'Invalid credentials'}, 401
```

### Resource-Intensive Operations
```python
# Limit expensive operations
@app.route('/generate-report', methods=['POST'])
@rate_limit('report_generation', limit=3, period=3600)  # 3 reports per hour
def generate_report():
    # This takes 30 seconds and uses lots of CPU
    report = create_detailed_report()
    return send_file(report)
```

### Email/SMS Sending
```python
# Prevent spam
@app.route('/send-verification', methods=['POST'])
@rate_limit('verification_email', limit=3, period=3600)  # 3 emails per hour
def send_verification():
    send_email(current_user.email, verification_code)
    return {'message': 'Verification email sent'}
```

## How It Works

### Storage
- Uses Flask's `g` object to store rate limit data per request
- Stores timestamps of requests in memory
- Automatically cleans up expired entries

### User Identification
1. **Authenticated users** (Flask-Login detected):
   - Tracked by `current_user.id`
   - Limits apply per user account
   
2. **Anonymous users**:
   - Tracked by IP address (`request.remote_addr`)
   - Limits apply per IP

### Algorithm
- **Sliding window** approach
- Counts requests within the time period
- Removes expired timestamps automatically
- O(n) complexity where n = number of requests in window

## Configuration

### Custom Error Messages

```python
from flask_ratelimit_simple import rate_limit

@app.errorhandler(429)
def ratelimit_handler(e):
    return {
        'error': 'Too many requests',
        'message': 'Please slow down and try again later',
        'retry_after': e.description
    }, 429
```

### Integration with Flask-Login

```python
from flask_login import LoginManager, current_user

login_manager = LoginManager(app)

# Rate limits automatically use current_user.id when available
@app.route('/api/user/profile')
@login_required
@rate_limit('profile_view', limit=100, period=60)
def view_profile():
    # This limit is per user, not per IP
    return {'user': current_user.to_dict()}
```

## Performance

- **Memory usage**: ~100 bytes per tracked request
- **Overhead**: <1ms per request
- **Scalability**: Suitable for single-server deployments
- **Cleanup**: Automatic, runs on each request

### When to Use This Package

✅ **Good for**:
- Single-server Flask applications
- Development and testing
- Small to medium traffic (< 10k requests/min)
- When you don't want Redis complexity

❌ **Not recommended for**:
- Multi-server deployments (use Redis-based solution)
- Very high traffic (> 100k requests/min)
- When you need persistent rate limit data across restarts

## Testing

```python
import pytest
from flask import Flask
from flask_ratelimit_simple import rate_limit

def test_rate_limiting():
    app = Flask(__name__)
    
    @app.route('/test')
    @rate_limit('test', limit=3, period=60)
    def test_endpoint():
        return {'success': True}
    
    client = app.test_client()
    
    # First 3 requests should succeed
    for i in range(3):
        response = client.get('/test')
        assert response.status_code == 200
    
    # 4th request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429
```

## Production Usage

This package is used in production at:
- [wallmarkets](https://wallmarkets.store) - Multi-vendor marketplace
- Protecting authentication endpoints
- Rate limiting API calls
- Preventing abuse of resource-intensive operations

## Comparison with Alternatives

| Feature | flask-ratelimit-simple | Flask-Limiter | flask-ratelimit |
|---------|----------------------|---------------|------------------|
| **Redis required** | ❌ No | ✅ Yes | ✅ Yes |
| **Setup complexity** | Low | Medium | Medium |
| **Multi-server** | ❌ No | ✅ Yes | ✅ Yes |
| **Memory usage** | Low | N/A | N/A |
| **Dependencies** | 0 | 2+ | 2+ |

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 📚 [Documentation](https://github.com/wallmarkets/flask-ratelimit-simple)
- 🐛 [Issue Tracker](https://github.com/wallmarkets/flask-ratelimit-simple/issues)
- 💬 [Discussions](https://github.com/wallmarkets/flask-ratelimit-simple/discussions)

## Related Packages

- [flask-security-headers](https://pypi.org/project/flask-security-headers/) - Security utilities
- [flask-supercache](https://pypi.org/project/flask-supercache/) - Caching
- [flask-querymonitor](https://pypi.org/project/flask-querymonitor/) - Query optimization

---

**Made with ❤️ by the wallmarkets Team**
