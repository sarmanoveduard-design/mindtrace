from __future__ import annotations

from pydantic import BaseModel


class SessionGetOrCreateRequest(BaseModel):
    user_id: str
    channel: str


class SessionGetOrCreateResponse(BaseModel):
    id: str
    user_id: str
    taxonomy_version_id: str
    channel: str
    status: str
    current_question_order: int
    is_existing: bool
