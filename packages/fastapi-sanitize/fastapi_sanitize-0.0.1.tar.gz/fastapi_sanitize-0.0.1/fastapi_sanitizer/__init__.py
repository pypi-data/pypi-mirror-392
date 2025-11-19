"""fastapi_sanitizer package - simple configurable middleware."""

from .middleware import SanitizerMiddleware  # public import
__all__ = ["SanitizerMiddleware"]
