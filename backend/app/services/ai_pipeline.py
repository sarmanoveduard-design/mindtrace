from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.entities import AnswerExtraction
from app.models.entities import FinalProfile
from app.models.entities import SessionAggregate
from app.services.ai_inputs import build_answer_extract_input
from app.services.ai_inputs import build_final_profile_input
from app.services.ai_inputs import build_session_aggregate_input
from app.services.ai_persistence import save_answer_extract_result
from app.services.ai_persistence import save_final_profile_result
from app.services.ai_persistence import save_session_aggregate_result
from app.services.openai_executor import OpenAIExecutor
from app.services.prompt_reads import get_prompt_model_name
from app.services.prompt_reads import get_prompt_version_or_raise


def run_answer_extract_stage(
    db: Session,
    *,
    answer_id: str,
    prompt_version_id: str,
) -> AnswerExtraction:
    prompt_version = get_prompt_version_or_raise(
        db,
        prompt_version_id=prompt_version_id,
        stage_code="answer_extract",
    )
    model_name = get_prompt_model_name(prompt_version)

    input_payload = build_answer_extract_input(
        db,
        answer_id=answer_id,
    )
    executor = OpenAIExecutor()
    result_payload = executor.execute_structured_stage(
        stage_code="answer_extract",
        system_prompt=prompt_version.system_prompt,
        input_payload=input_payload,
        model_name=model_name,
    )

    return save_answer_extract_result(
        db,
        answer_id=answer_id,
        session_id=input_payload["session_id"],
        question_id=input_payload["question_id"],
        prompt_version_id=prompt_version_id,
        model_name=model_name or "default",
        input_snapshot=input_payload,
        raw_output_text=None,
        token_usage_json={},
        payload=result_payload,
    )


def run_session_aggregate_stage(
    db: Session,
    *,
    session_id: str,
    prompt_version_id: str,
) -> SessionAggregate:
    prompt_version = get_prompt_version_or_raise(
        db,
        prompt_version_id=prompt_version_id,
        stage_code="session_aggregate",
    )
    model_name = get_prompt_model_name(prompt_version)

    input_payload = build_session_aggregate_input(
        db,
        session_id=session_id,
    )
    executor = OpenAIExecutor()
    result_payload = executor.execute_structured_stage(
        stage_code="session_aggregate",
        system_prompt=prompt_version.system_prompt,
        input_payload=input_payload,
        model_name=model_name,
    )

    return save_session_aggregate_result(
        db,
        session_id=session_id,
        prompt_version_id=prompt_version_id,
        raw_output_text=None,
        payload=result_payload,
    )


def run_final_profile_build_stage(
    db: Session,
    *,
    session_id: str,
    prompt_version_id: str,
) -> FinalProfile:
    prompt_version = get_prompt_version_or_raise(
        db,
        prompt_version_id=prompt_version_id,
        stage_code="final_profile_build",
    )
    model_name = get_prompt_model_name(prompt_version)

    input_payload = build_final_profile_input(
        db,
        session_id=session_id,
    )
    executor = OpenAIExecutor()
    result_payload = executor.execute_structured_stage(
        stage_code="final_profile_build",
        system_prompt=prompt_version.system_prompt,
        input_payload=input_payload,
        model_name=model_name,
    )

    return save_final_profile_result(
        db,
        session_id=session_id,
        prompt_version_id=prompt_version_id,
        raw_output_text=None,
        payload=result_payload,
    )
