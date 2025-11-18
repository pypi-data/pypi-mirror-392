# Flask-RateLimit-Simple

In-memory rate limiting for Flask. No Redis required.

## What it does

- TTL-based in-memory storage
- Standard `X-RateLimit-*` headers
- IP-based (anonymous) or user-based (authenticated)
- No external dependencies

Built while working on [wallmarkets](https://wallmarkets.store).

## Installation

```bash
pip install flask-ratelimit-simple
```

## Usage

```python
from flask import Flask
from flask_ratelimit_simple import rate_limit

app = Flask(__name__)

@app.route('/login', methods=['POST'])
@rate_limit('login', limit=5, period=300)  # 5 attempts per 5min
def login():
    # Your code here
    pass
```

## Response (429 Too Many Requests)

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 247
Retry-After: 247
```

## How it works

- Uses Flask app context to store attempt timestamps
- Cleans up expired entries automatically
- Uses client IP for anonymous users
- Uses user ID for authenticated users (via flask_login if available)

## License

MIT

## Contributing

Pull requests welcome. Please add tests.
