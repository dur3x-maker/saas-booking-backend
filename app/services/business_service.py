from sqlalchemy.orm import Session

from app.models.business import Business
from app.schemas.business import BusinessCreate


def create_business(db: Session, data: BusinessCreate) -> Business:
    business = Business(
        name=data.name,
        timezone=data.timezone,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def get_businesses(db: Session) -> list[Business]:
    return db.query(Business).all()
