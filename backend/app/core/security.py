import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import settings

PASSWORD_ITERATIONS = 120000


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _base64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), PASSWORD_ITERATIONS)
    return f"{salt}${base64.b64encode(hashed).decode()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, encoded_hash = stored_password.split('$', 1)
    except ValueError:
        return False

    derived_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), PASSWORD_ITERATIONS)
    return hmac.compare_digest(base64.b64encode(derived_hash).decode(), encoded_hash)


def create_access_token(data: dict, expires_seconds: int) -> str:
    payload = data.copy()
    payload['exp'] = int(time.time()) + expires_seconds
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode()
    payload_b64 = _base64url(payload_bytes)
    signature = hmac.new(settings.SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    return f"{payload_b64}.{_base64url(signature)}"


def decode_access_token(token: str) -> dict:
    try:
        payload_b64, signature_b64 = token.split('.')
    except ValueError:
        raise ValueError('Invalid token format')

    expected_sig = hmac.new(settings.SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(_base64url(expected_sig), signature_b64):
        raise ValueError('Invalid token signature')

    payload_bytes = _base64url_decode(payload_b64)
    payload = json.loads(payload_bytes.decode())
    if payload.get('exp', 0) < int(time.time()):
        raise ValueError('Token expired')

    return payload
