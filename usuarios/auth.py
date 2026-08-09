from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings
from ninja.security import HttpBearer
from usuarios.models import Usuario


def generate_token(user: Usuario) -> str:
    payload = {
        'id': user.id,
        'email': user.email,
        'funcao': user.funcao,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            payload = decode_token(token)
            user_id = payload.get('id')
            if not user_id:
                return None
            user = Usuario.objects.filter(id=user_id, is_active=True).first()
            if user:
                request.user = user
                return user
        except Exception:
            return None
        return None
