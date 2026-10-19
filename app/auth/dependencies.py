from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.auth_service import decode_token
from app.database.database import get_db
from app.database.models import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )

    user = (
        db.query(User)
        .filter(User.id == payload.get("user_id"))
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User account is invalid or inactive"
        )

    return user


def require_employee(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "EMPLOYEE":
        raise HTTPException(
            status_code=403,
            detail="Employee access required"
        )

    return current_user


def require_hr(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "HR":
        raise HTTPException(
            status_code=403,
            detail="HR access required"
        )

    return current_user
