from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.models.business_user import BusinessUser, BusinessRole

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------ #
#  get_current_user: Bearer token → User
# ------------------------------------------------------------------ #

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


# ------------------------------------------------------------------ #
#  get_current_business: X-Business-ID header → (business_id, role)
# ------------------------------------------------------------------ #

@dataclass
class BusinessContext:
    business_id: int
    role: BusinessRole


def get_current_business(
    x_business_id: int | None = Header(None, alias="X-Business-ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessContext:
    if x_business_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Business-ID header required",
        )
    bu = (
        db.query(BusinessUser)
        .filter(
            BusinessUser.user_id == current_user.id,
            BusinessUser.business_id == x_business_id,
        )
        .first()
    )
    if bu is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this business",
        )
    return BusinessContext(business_id=bu.business_id, role=bu.role)


# ------------------------------------------------------------------ #
#  require_role: owner > admin
# ------------------------------------------------------------------ #

_ROLE_LEVEL = {
    BusinessRole.ADMIN: 1,
    BusinessRole.OWNER: 2,
}


def require_role(minimum: BusinessRole) -> Callable:
    def _dependency(
        ctx: BusinessContext = Depends(get_current_business),
    ) -> BusinessContext:
        if _ROLE_LEVEL[ctx.role] < _ROLE_LEVEL[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role {minimum.value} or higher",
            )
        return ctx
    return _dependency
