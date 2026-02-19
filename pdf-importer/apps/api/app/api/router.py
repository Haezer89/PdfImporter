from fastapi import APIRouter

from app.api.imports import router as imports_router
from app.api.models import router as models_router

api_router = APIRouter()
api_router.include_router(models_router)
api_router.include_router(imports_router)
