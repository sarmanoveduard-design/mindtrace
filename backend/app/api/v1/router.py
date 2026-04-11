from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.answers import router as answers_router
from app.api.v1.expert_session_detail import router as expert_session_detail_router
from app.api.v1.expert_sessions_list import router as expert_sessions_list_router
from app.api.v1.final_profiles import router as final_profiles_router
from app.api.v1.session_status import router as session_status_router
from app.api.v1.session_questions import router as session_questions_router
from app.api.v1.session_overview import router as session_overview_router
from app.api.v1.user_sessions_list import router as user_sessions_list_router
from app.api.v1.expert_reviews import router as expert_reviews_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.session_get_or_create import router as session_get_or_create_router
from app.api.v1.taxonomy import router as taxonomy_router

router = APIRouter()
router.include_router(taxonomy_router)
router.include_router(sessions_router)
router.include_router(final_profiles_router)
router.include_router(session_get_or_create_router)
router.include_router(answers_router)
router.include_router(session_status_router)
router.include_router(session_questions_router)
router.include_router(session_overview_router)
router.include_router(user_sessions_list_router)
router.include_router(expert_reviews_router)
router.include_router(expert_session_detail_router)
router.include_router(expert_sessions_list_router)
