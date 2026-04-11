from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ExpertAnswerExtractionItem(BaseModel):
    extraction_id: str | None
    status: str | None
    confidence_score: float | None
    normalized_output: dict[str, Any] | None


class ExpertAnswerItem(BaseModel):
    answer_id: str
    question_id: str
    question_code: str
    question_title: str
    revision_no: int
    ai_status: str
    answer_text: str | None
    answer_payload: dict[str, Any] | None
    extraction: ExpertAnswerExtractionItem | None


class ExpertSessionDetailResponse(BaseModel):
    session_id: str
    taxonomy_version_id: str
    status: str
    answers: list[ExpertAnswerItem]
    session_aggregate: dict[str, Any] | None
    final_profile: dict[str, Any] | None
