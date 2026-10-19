from datetime import datetime, timedelta, timezone

from itsdangerous import BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


SECRET_KEY = "nexacore-ai-hr-development-secret"
TOKEN_MAX_AGE = 60 * 60 * 8  # 8 hours

serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def create_token(user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }

    return serializer.dumps(payload)


def decode_token(token: str):
    try:
        return serializer.loads(
            token,
            max_age=TOKEN_MAX_AGE,
        )
    except BadSignature:
        return None
