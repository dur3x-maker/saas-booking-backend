from fastapi import APIRouter

from app.api.v1.endpoints import businesses, auth, bookings
from app.api.v1.services import router as services_router
from app.api.v1.staff import router as staff_router
from app.api.v1 import schedule
from app.api.v1.endpoints import working_hours


api_router = APIRouter(prefix="/api/v1")

# --- Глобальные (не привязаны к business) ---

api_router.include_router(
    businesses.router,
    prefix="/businesses",
    tags=["businesses"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

# --- Tenant-scoped: /api/v1/businesses/{business_id}/... ---

_tenant_router = APIRouter(prefix="/businesses/{business_id}")

_tenant_router.include_router(services_router)
_tenant_router.include_router(staff_router)
_tenant_router.include_router(schedule.router)
_tenant_router.include_router(working_hours.router)
_tenant_router.include_router(bookings.router)

api_router.include_router(_tenant_router)
