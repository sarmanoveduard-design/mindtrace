from __future__ import annotations

from pydantic import BaseModel


class TaxonomyActiveResponse(BaseModel):
    id: str
    code: str
    version_label: str
    title: str
    description: str | None
    status: str


class QuestionItemResponse(BaseModel):
    id: str
    code: str
    order_no: int
    title: str
    description: str | None
    question_type: str
    is_required: bool
    is_active: bool


class ActiveQuestionsResponse(BaseModel):
    taxonomy_version_id: str
    questions: list[QuestionItemResponse]
