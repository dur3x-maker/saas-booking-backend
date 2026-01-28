from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# сюда позже подключим эндпоинты:
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
