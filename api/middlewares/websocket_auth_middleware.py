from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken

import os
import json


class WebSocketAuthMiddleware:
    """Middleware для проверки JWT или Custom Token при WebSocket подключении."""
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope["query_string"].decode("utf8"))
        token = query_params.get("token", [None])[0] or ""

        if not token:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("utf8")
            if auth_header:
                token = auth_header

        if token and self.authenticate_token(token):
            scope["user"] = "authenticated"
            return await self.inner(scope, receive, send)
        
        await send({
            "type": "websocket.send",
            "text": json.dumps({"error": "403 Forbidden: Invalid token"})
        })
        await send({"type": "websocket.close", "code": 403})

    def authenticate_token(self, token):
        """Проверяет JWT или Custom Token."""
        try:
            if token.startswith("Bearer "):
                jwt_token = token.split("Bearer ")[-1]
                AccessToken(jwt_token)
                return True

            if token.startswith("Token "):
                custom_token = token.split("Token ")[-1]
                allowed_tokens = os.getenv("ALLOWED_WEBSOCKET_TOKENS", "").split(",")
                if custom_token in allowed_tokens:
                    return True

            return False
        except Exception:
            return False