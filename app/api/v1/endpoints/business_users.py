# app/api/v1/endpoints/business_users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    get_current_business,
    require_role,
    BusinessContext,
)
from app.models.business_user import BusinessUser, BusinessRole
from app.models.user import User
from app.schemas.business_user import (
    BusinessUserRead,
    BusinessUserInvite,
    BusinessUserUpdate,
)

router = APIRouter(tags=["Business Users"])

_owner_dep = require_role(BusinessRole.OWNER)


@router.get("/business-users", response_model=list[BusinessUserRead])
def list_business_users(
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    bus = (
        db.query(BusinessUser)
        .filter(BusinessUser.business_id == ctx.business_id)
        .all()
    )
    result = []
    for bu in bus:
        user = db.query(User).filter(User.id == bu.user_id).first()
        result.append(BusinessUserRead(
            user_id=bu.user_id,
            business_id=bu.business_id,
            role=bu.role,
            email=user.email if user else None,
        ))
    return result


@router.post(
    "/business-users/invite",
    response_model=BusinessUserRead,
    status_code=status.HTTP_201_CREATED,
)
def invite_user(
    body: BusinessUserInvite,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(_owner_dep),
):
    target_user = db.query(User).filter(User.email == body.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )

    existing = (
        db.query(BusinessUser)
        .filter(
            BusinessUser.user_id == target_user.id,
            BusinessUser.business_id == ctx.business_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has access to this business",
        )

    bu = BusinessUser(
        user_id=target_user.id,
        business_id=ctx.business_id,
        role=body.role,
    )
    db.add(bu)
    db.commit()

    return BusinessUserRead(
        user_id=bu.user_id,
        business_id=bu.business_id,
        role=bu.role,
        email=target_user.email,
    )


@router.patch("/business-users/{user_id}", response_model=BusinessUserRead)
def update_user_role(
    user_id: int,
    body: BusinessUserUpdate,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(_owner_dep),
):
    bu = (
        db.query(BusinessUser)
        .filter(
            BusinessUser.user_id == user_id,
            BusinessUser.business_id == ctx.business_id,
        )
        .first()
    )
    if not bu:
        raise HTTPException(status_code=404, detail="Business user not found")

    bu.role = body.role
    db.commit()

    user = db.query(User).filter(User.id == user_id).first()
    return BusinessUserRead(
        user_id=bu.user_id,
        business_id=bu.business_id,
        role=bu.role,
        email=user.email if user else None,
    )


@router.delete(
    "/business-users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_user_access(
    user_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(_owner_dep),
):
    bu = (
        db.query(BusinessUser)
        .filter(
            BusinessUser.user_id == user_id,
            BusinessUser.business_id == ctx.business_id,
        )
        .first()
    )
    if not bu:
        raise HTTPException(status_code=404, detail="Business user not found")

    if bu.role == BusinessRole.OWNER and bu.user_id == user_id:
        owner_count = (
            db.query(BusinessUser)
            .filter(
                BusinessUser.business_id == ctx.business_id,
                BusinessUser.role == BusinessRole.OWNER,
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot remove the last owner",
            )

    db.delete(bu)
    db.commit()
