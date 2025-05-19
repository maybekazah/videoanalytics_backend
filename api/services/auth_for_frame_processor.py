from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import os

ALLOWED_TOKENS_FOR_FRAME_PROCESSOR = [
    os.getenv('TOKEN_FOR_FRAME_PROCESSOR')
]


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Token "):
            raise AuthenticationFailed("Неверный токен или доступ запрещён")
        token = auth_header.split("Token ")[-1]

        if token not in ALLOWED_TOKENS_FOR_FRAME_PROCESSOR:
            raise AuthenticationFailed("Неверный токен или доступ запрещён")

        return (None, None) 