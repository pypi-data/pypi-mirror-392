# fastapi_sanitizer/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import json
from .sanitizer import sanitize_input, sanitize_output

class SanitizerMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware that sanitizes JSON request bodies and JSON responses.

    Usage:
        app.add_middleware(
            SanitizerMiddleware,
            allowed_tags=["b", "i"],
            script_allowed_fields=["raw_js"],
            whitelist_fields=["system_status"],
        )
    """
    def __init__(self, app, *, allowed_tags=None, script_allowed_fields=None, whitelist_fields=None):
        super().__init__(app)
        self.config = {
            "allowed_tags": allowed_tags or [],
            "script_allowed_fields": script_allowed_fields or [],
            "whitelist_fields": whitelist_fields or [],
        }

    async def dispatch(self, request: Request, call_next):
        # Sanitize incoming JSON body if present
        try:
            body = await request.json()
            # Only sanitize if it's a dict
            if isinstance(body, dict):
                sanitized_body = sanitize_input(body, self.config)
                request._body = json.dumps(sanitized_body).encode()
        except Exception:
            # no JSON body or parse error: ignore
            pass

        response: Response = await call_next(request)

        # Sanitize JSON response bodies
        try:
            # decode bytes -> try to parse JSON
            raw = response.body.decode()
            content = json.loads(raw)
            if isinstance(content, dict):
                sanitized_content = sanitize_output(content, self.config)
                response.body = json.dumps(sanitized_content).encode()
        except Exception:
            pass

        return response
