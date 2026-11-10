from fastapi import APIRouter

from backend.api.endpoints.upload import router as upload_router
from backend.api.endpoints.evaluate import router as evaluate_router
from backend.api.endpoints.slides import router as slides_router
from backend.api.endpoints.jury import router as jury_router
from backend.api.endpoints.assistant import router as assistant_router
from backend.api.endpoints.rubrics import router as rubrics_router
from backend.api.endpoints.reports import router as reports_router
from backend.api.endpoints.analytics import router as analytics_router
from backend.api.endpoints.settings import router as settings_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="", tags=["Upload & Pipeline"])
api_router.include_router(evaluate_router, prefix="/evaluations", tags=["Evaluations"])
api_router.include_router(slides_router, prefix="/slides", tags=["Slides"])
api_router.include_router(jury_router, prefix="/jury", tags=["Jury Simulator"])
api_router.include_router(assistant_router, prefix="/assistant", tags=["AI Assistant"])
api_router.include_router(rubrics_router, prefix="/rubrics", tags=["Rubrics"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics & Dashboard"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])

