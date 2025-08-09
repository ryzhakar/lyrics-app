from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Set common security headers."""

    async def dispatch(self, request, call_next):  # type: ignore[override]
        response = await call_next(request)
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')
        response.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=()',
        )
        if request.url.scheme == 'https':
            response.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=63072000; includeSubDomains; preload',
            )
        return response
