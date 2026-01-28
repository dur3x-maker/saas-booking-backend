from fastapi import APIRouter

from app.api.v1.endpoints import businesses, auth
from app.api.v1.services import router as services_router

api_router = APIRouter(prefix="/api/v1")

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

api_router.include_router(
    services_router,
    prefix="/services",
    tags=["services"],
)
