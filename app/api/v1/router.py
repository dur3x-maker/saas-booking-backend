from fastapi import APIRouter

from app.api.v1.endpoints import businesses, auth, bookings, customers, business_users, me, context
from app.api.v1.services import router as services_router
from app.api.v1.staff import router as staff_router
from app.api.v1 import schedule
from app.api.v1.endpoints import working_hours


api_router = APIRouter(prefix="/api/v1")

# --- Global (no tenant context needed) ---

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    businesses.router,
    prefix="/businesses",
    tags=["Businesses"],
)

api_router.include_router(me.router)
api_router.include_router(context.router)

# --- Tenant-scoped (X-Business-ID header required) ---

api_router.include_router(services_router)
api_router.include_router(staff_router)
api_router.include_router(schedule.router)
api_router.include_router(working_hours.router)
api_router.include_router(bookings.router)
api_router.include_router(customers.router)
api_router.include_router(business_users.router)
