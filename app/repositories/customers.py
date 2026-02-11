# app/repositories/customers.py

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


def create(session: Session, customer: Customer) -> Customer:
    session.add(customer)
    session.flush()
    return customer


def get_by_id(
    session: Session,
    customer_id: int,
    *,
    business_id: int,
) -> Optional[Customer]:
    stmt = (
        select(Customer)
        .where(
            Customer.id == customer_id,
            Customer.business_id == business_id,
            Customer.is_active == True,
        )
    )
    return session.scalar(stmt)


def get_by_phone(
    session: Session,
    *,
    business_id: int,
    phone: str,
) -> Optional[Customer]:
    stmt = (
        select(Customer)
        .where(
            Customer.business_id == business_id,
            Customer.phone == phone,
            Customer.is_active == True,
        )
    )
    return session.scalar(stmt)


def list_for_business(
    session: Session,
    *,
    business_id: int,
    only_active: bool = True,
) -> List[Customer]:
    conditions = [Customer.business_id == business_id]
    if only_active:
        conditions.append(Customer.is_active == True)
    stmt = (
        select(Customer)
        .where(*conditions)
        .order_by(Customer.created_at.desc())
    )
    return list(session.scalars(stmt))
