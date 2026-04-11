from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel

from app.schemas.ai.answer_extract import AnswerExtractResult
from app.schemas.ai.final_profile import FinalProfileBuildResult
from app.schemas.ai.session_aggregate import SessionAggregateResult

AIStageCode = Literal[
    "answer_extract",
    "session_aggregate",
    "final_profile_build",
]

AI_SCHEMA_REGISTRY: dict[AIStageCode, type[BaseModel]] = {
    "answer_extract": AnswerExtractResult,
    "session_aggregate": SessionAggregateResult,
    "final_profile_build": FinalProfileBuildResult,
}


def get_ai_result_model(stage_code: AIStageCode) -> type[BaseModel]:
    return AI_SCHEMA_REGISTRY[stage_code]


def validate_ai_result(
    stage_code: AIStageCode,
    payload: dict[str, Any],
) -> BaseModel:
    model_class = get_ai_result_model(stage_code)
    return model_class.model_validate(payload)
