from __future__ import annotations

from pydantic import BaseModel


class SessionQuestionItem(BaseModel):
    id: str
    code: str
    order_no: int
    title: str
    description: str | None
    question_type: str
    is_required: bool
    is_active: bool
    has_answer: bool
    answer_id: str | None
    revision_no: int | None
    ai_status: str | None
    is_current_question: bool


class SessionQuestionsResponse(BaseModel):
    session_id: str
    taxonomy_version_id: str
    current_question_order: int
    questions: list[SessionQuestionItem]
