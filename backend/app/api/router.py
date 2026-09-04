from fastapi import APIRouter

from app.modules.access_requests.admin_router import router as access_admin_router
from app.modules.access_requests.router import router as access_router
from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.employees.router import router as employees_router
from app.modules.files.router import router as files_router
from app.modules.health.router import router as health_router
from app.modules.operations.router import router as operations_router
from app.modules.privacy.router import router as privacy_router

api_router = APIRouter()
api_router.include_router(access_admin_router)
api_router.include_router(access_router)
api_router.include_router(ai_router)
api_router.include_router(auth_router)
api_router.include_router(billing_router)
api_router.include_router(employees_router)
api_router.include_router(files_router)
api_router.include_router(health_router)
api_router.include_router(operations_router)
api_router.include_router(privacy_router)
