from __future__ import annotations

from app.models.entities import PromptVersion
from sqlalchemy import select
from app.services.ai_contracts import AIStageCode
from sqlalchemy.orm import Session


def get_prompt_version_or_raise(
    db: Session,
    *,
    prompt_version_id: str,
    stage_code: AIStageCode,
) -> PromptVersion:
    prompt_version = db.get(PromptVersion, prompt_version_id)
    if prompt_version is None:
        raise ValueError("Prompt version not found.")

    if prompt_version.stage_code != stage_code:
        raise ValueError("Prompt version stage does not match stage_code.")

    if prompt_version.status != "active":
        raise ValueError("Prompt version is not active.")

    return prompt_version


def get_prompt_model_name(prompt_version: PromptVersion) -> str | None:
    model_config = prompt_version.model_config_json or {}
    model_name = model_config.get("model")

    if model_name is None:
        return None

    if not isinstance(model_name, str):
        raise ValueError("Prompt model must be a string.")

    return model_name


def get_active_prompt_version_or_raise(
    db: Session,
    *,
    stage_code: AIStageCode,
) -> PromptVersion:
    stmt = (
        select(PromptVersion)
        .where(PromptVersion.stage_code == stage_code)
        .where(PromptVersion.status == "active")
        .limit(1)
    )
    prompt_version = db.execute(stmt).scalar_one_or_none()

    if prompt_version is None:
        raise ValueError("Active prompt version not found.")

    return prompt_version
