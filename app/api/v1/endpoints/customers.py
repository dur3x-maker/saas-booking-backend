# app/api/v1/endpoints/customers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_business, BusinessContext
from app.schemas.customer import CustomerCreate, CustomerRead
from app.models.customer import Customer
from app.repositories import customers as customers_repo

router = APIRouter(tags=["Customers"])


@router.post(
    "/customers",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать клиента",
)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    business_id = ctx.business_id
    existing = customers_repo.get_by_phone(
        db, business_id=business_id, phone=body.phone,
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with phone {body.phone} already exists in this business",
        )

    customer = Customer(
        business_id=business_id,
        name=body.name,
        phone=body.phone,
        email=body.email,
    )
    customers_repo.create(db, customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get(
    "/customers",
    response_model=list[CustomerRead],
    summary="Список клиентов бизнеса",
)
def list_customers(
    only_active: bool = True,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return customers_repo.list_for_business(
        db, business_id=ctx.business_id, only_active=only_active,
    )


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerRead,
    summary="Получить клиента по ID",
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    customer = customers_repo.get_by_id(
        db, customer_id, business_id=ctx.business_id,
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    return customer
