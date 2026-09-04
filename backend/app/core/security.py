import base64
import hashlib
import hmac
import secrets

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return _password_hash.verify(password, encoded)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def signed_token(*, purpose: str, subject: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode('utf-8'),
        f'{purpose}:{subject}'.encode(),
        hashlib.sha256,
    ).digest()
    encoded = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('ascii')
    return f'{subject}.{encoded}'
