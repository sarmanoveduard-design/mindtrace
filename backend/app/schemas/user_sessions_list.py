from __future__ import annotations

from pydantic import BaseModel


class UserSessionListItem(BaseModel):
    session_id: str
    status: str
    channel: str
    current_question_order: int
    answered_questions: int
    total_questions: int
    has_final_profile: bool
    final_profile_status: str | None


class UserSessionsListResponse(BaseModel):
    user_id: str
    sessions: list[UserSessionListItem]
