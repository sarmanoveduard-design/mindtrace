from __future__ import annotations

from pydantic import BaseModel


class ExpertSessionListItem(BaseModel):
    session_id: str
    user_id: str
    status: str
    channel: str
    current_question_order: int
    answered_questions: int
    total_questions: int
    has_final_profile: bool
    final_profile_status: str | None


class ExpertSessionsListResponse(BaseModel):
    sessions: list[ExpertSessionListItem]
