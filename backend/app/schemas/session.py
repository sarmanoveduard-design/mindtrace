from __future__ import annotations

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    user_id: str
    channel: str


class SessionResponse(BaseModel):
    id: str
    user_id: str
    taxonomy_version_id: str
    channel: str
    status: str
    current_question_order: int
