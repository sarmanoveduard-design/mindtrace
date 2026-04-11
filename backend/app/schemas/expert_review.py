from __future__ import annotations

from pydantic import BaseModel


class ExpertReviewCreateRequest(BaseModel):
    expert_user_id: str
    score: int
    comment: str | None = None


class ExpertReviewCreateResponse(BaseModel):
    id: str
    session_id: str
    expert_user_id: str
    score: int
    comment: str | None
