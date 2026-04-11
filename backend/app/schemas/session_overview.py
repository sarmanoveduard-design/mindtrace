from __future__ import annotations

from app.schemas.ai.final_profile import FinalProfileBuildResult
from app.schemas.session_questions import SessionQuestionsResponse
from app.schemas.session_status import SessionStatusResponse
from pydantic import BaseModel


class SessionOverviewResponse(BaseModel):
    status: SessionStatusResponse
    questions: SessionQuestionsResponse
    final_profile: FinalProfileBuildResult | None
