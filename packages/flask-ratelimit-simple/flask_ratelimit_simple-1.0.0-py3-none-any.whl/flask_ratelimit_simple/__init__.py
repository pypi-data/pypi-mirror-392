"""
Flask-RateLimit-Simple
======================

In-memory rate limiting. No Redis required.

Usage:
    from flask import Flask
    from flask_ratelimit_simple import rate_limit

    app = Flask(__name__)

    @app.route('/login', methods=['POST'])
    @rate_limit('login', limit=5, period=300)
    def login():
        pass
"""

__version__ = "1.0.0"

from .limiter import rate_limit, RateLimiter, RateLimitExceeded

__all__ = ["rate_limit", "RateLimiter", "RateLimitExceeded"]
