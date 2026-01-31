"""JWT validation middleware."""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.dependencies import jwt_service


class JwtAuthMiddleware:
    """Middleware that validates JWT when present."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path
        if path.startswith("/api/auth"):
            await self.app(scope, receive, send)
            return

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.replace("Bearer ", "", 1)
            try:
                claims = jwt_service.verify_token(token)
                request.state.user_id = claims.get("sub")
            except Exception:
                response = JSONResponse(status_code=401, content={"detail": "Invalid token"})
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
