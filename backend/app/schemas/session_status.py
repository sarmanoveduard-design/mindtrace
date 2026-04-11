from __future__ import annotations

from pydantic import BaseModel


class SessionStatusQuestion(BaseModel):
    id: str
    code: str
    order_no: int
    title: str
    description: str | None
    question_type: str
    is_required: bool


class SessionStatusResponse(BaseModel):
    session_id: str
    taxonomy_version_id: str
    status: str
    channel: str
    current_question_order: int
    answered_questions: int
    total_questions: int
    has_final_profile: bool
    final_profile_status: str | None
    current_question: SessionStatusQuestion | None
