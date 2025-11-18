"""
Rate limiting using in-memory storage.
"""

import logging
from functools import wraps
from time import time
from flask import current_app, request


logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter with TTL-based storage."""

    def __init__(self, key_prefix, limit, period):
        self.key_prefix = key_prefix
        self.limit = limit
        self.period = period

    def _get_storage(self):
        if not hasattr(current_app, "rate_limit_storage"):
            current_app.rate_limit_storage = {}
        return current_app.rate_limit_storage

    def _clean_old_entries(self, storage, key, now):
        if key in storage:
            storage[key] = [t for t in storage[key] if t > now - self.period]
        else:
            storage[key] = []

    def is_rate_limited(self, key):
        try:
            storage = self._get_storage()
            now = time()
            key = f"{self.key_prefix}:{key}"

            self._clean_old_entries(storage, key, now)

            if len(storage[key]) >= self.limit:
                logger.warning(
                    f"Rate limit exceeded: {key}, "
                    f"attempts: {len(storage[key])}, limit: {self.limit}"
                )
                return True

            storage[key].append(now)
            return False

        except Exception as e:
            logger.error(f"Rate limit error for {key}: {str(e)}")
            return False

    def get_remaining_requests(self, key):
        try:
            storage = self._get_storage()
            now = time()
            key = f"{self.key_prefix}:{key}"

            self._clean_old_entries(storage, key, now)

            remaining = max(0, self.limit - len(storage[key]))
            if storage[key]:
                reset_time = min(storage[key]) + self.period - now
            else:
                reset_time = 0

            return remaining, int(reset_time)

        except Exception as e:
            logger.error(f"Error getting remaining requests for {key}: {str(e)}")
            return 0, 0


def get_client_ip():
    """Get client IP from request."""
    if current_app.config.get("BEHIND_PROXY"):
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def rate_limit(key_prefix, limit=5, period=300):
    """
    Rate limiting decorator.

    Args:
        key_prefix: Identifier (e.g., 'login', 'api')
        limit: Max requests allowed
        period: Time window in seconds
    """
    limiter = RateLimiter(key_prefix, limit, period)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Try to get user ID if authenticated
                from flask_login import current_user
                if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                    identifier = str(current_user.id)
                else:
                    identifier = get_client_ip()
            except ImportError:
                identifier = get_client_ip()

            if limiter.is_rate_limited(identifier):
                remaining, reset_time = limiter.get_remaining_requests(identifier)

                response = current_app.make_response(
                    "Rate limit exceeded. Please try again later."
                )
                response.status_code = 429
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                response.headers["Retry-After"] = str(reset_time)

                return response

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class RateLimitExceeded(Exception):
    """Exception for rate limit exceeded."""

    def __init__(self, message="Rate limit exceeded", remaining=0, reset_time=0):
        self.message = message
        self.remaining = remaining
        self.reset_time = reset_time
        super().__init__(self.message)
