from __future__ import annotations

from datetime import datetime
from datetime import timezone

from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import AnswerExtraction
from app.models.entities import Answer
from app.models.entities import FinalProfile
from app.models.entities import Session as SessionModel
from app.models.entities import SessionAggregate
from app.services.ai_contracts import validate_ai_result


def save_answer_extract_result(
    db: Session,
    *,
    answer_id: str,
    session_id: str,
    question_id: str,
    prompt_version_id: str,
    model_name: str,
    input_snapshot: dict[str, Any],
    raw_output_text: str | None,
    token_usage_json: dict[str, Any] | None,
    payload: dict[str, Any],
) -> AnswerExtraction:
    result = validate_ai_result("answer_extract", payload)
    normalized_output = result.model_dump(mode="json")

    row = AnswerExtraction(
        answer_id=answer_id,
        session_id=session_id,
        question_id=question_id,
        stage_code="answer_extract",
        prompt_version_id=prompt_version_id,
        status="done",
        model_name=model_name,
        input_snapshot=input_snapshot,
        raw_output_text=raw_output_text,
        normalized_output=normalized_output,
        confidence_score=result.overall_confidence,
        token_usage_json=token_usage_json or {},
    )
    db.add(row)

    answer = db.get(Answer, answer_id)
    if answer is None:
        raise ValueError("Answer not found.")

    answer.ai_status = "done"

    db.commit()
    db.refresh(row)
    return row


def save_session_aggregate_result(
    db: Session,
    *,
    session_id: str,
    prompt_version_id: str,
    raw_output_text: str | None,
    payload: dict[str, Any],
) -> SessionAggregate:
    result = validate_ai_result("session_aggregate", payload)
    aggregate_json = result.model_dump(mode="json")

    row = SessionAggregate(
        session_id=session_id,
        stage_code="session_aggregate",
        prompt_version_id=prompt_version_id,
        status="done",
        aggregate_json=aggregate_json,
        coverage_json=result.coverage.model_dump(mode="json"),
        confidence_json={
            "overall_confidence": result.overall_confidence,
        },
        raw_output_text=raw_output_text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_final_profile_result(
    db: Session,
    *,
    session_id: str,
    prompt_version_id: str,
    raw_output_text: str | None,
    payload: dict[str, Any],
) -> FinalProfile:
    result = validate_ai_result("final_profile_build", payload)
    profile_json = result.model_dump(mode="json")

    row = FinalProfile(
        session_id=session_id,
        prompt_version_id=prompt_version_id,
        status="ready",
        profile_json=profile_json,
        summary_text=result.user_view.short_summary,
        confidence_json={
            "overall_confidence": result.overall_confidence,
        },
        raw_output_text=raw_output_text,
    )
    db.add(row)

    session = db.get(SessionModel, session_id)
    if session is None:
        raise ValueError("Session not found.")

    session.status = "ready"
    session.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return row
