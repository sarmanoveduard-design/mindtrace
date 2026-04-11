from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel


class AnswerCreateRequest(BaseModel):
    question_id: str
    source: Literal["web", "telegram", "mini_app"]
    answer_text: str | None = None
    answer_payload: dict[str, Any] | None = None
    client_event_id: str | None = None


class AnswerCreateResponse(BaseModel):
    answer_id: str
    session_id: str
    question_id: str
    revision_no: int
    ai_status: str
    celery_task_id: str
