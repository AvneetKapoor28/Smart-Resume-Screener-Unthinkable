from fastapi import APIRouter
from app.api.v1.endpoints import screening

# This is the main router for the v1 API.
# It includes all the specific endpoint routers.
api_router = APIRouter()
api_router.include_router(screening.router, prefix="/screening", tags=["Screening"])
