from __future__ import annotations

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.ai_pipeline import run_answer_extract_stage
from app.services.ai_pipeline import run_final_profile_build_stage
from app.services.ai_pipeline import run_session_aggregate_stage
from app.services.prompt_reads import get_active_prompt_version_or_raise


@celery_app.task(name="mindtrace.answer_extract")
def answer_extract_task(
    answer_id: str,
    prompt_version_id: str,
) -> str:
    with SessionLocal() as db:
        row = run_answer_extract_stage(
            db,
            answer_id=answer_id,
            prompt_version_id=prompt_version_id,
        )

        aggregate_prompt = get_active_prompt_version_or_raise(
            db,
            stage_code="session_aggregate",
        )

        session_aggregate_task.delay(
            session_id=str(row.session_id),
            prompt_version_id=str(aggregate_prompt.id),
        )

        return str(row.id)


@celery_app.task(name="mindtrace.session_aggregate")
def session_aggregate_task(
    session_id: str,
    prompt_version_id: str,
) -> str:
    with SessionLocal() as db:
        row = run_session_aggregate_stage(
            db,
            session_id=session_id,
            prompt_version_id=prompt_version_id,
        )

        coverage = {}
        if isinstance(row.aggregate_json, dict):
            coverage = row.aggregate_json.get("coverage", {})

        if coverage.get("is_minimum_coverage_reached"):
            final_prompt = get_active_prompt_version_or_raise(
                db,
                stage_code="final_profile_build",
            )

            final_profile_build_task.delay(
                session_id=str(row.session_id),
                prompt_version_id=str(final_prompt.id),
            )

        return str(row.id)


@celery_app.task(name="mindtrace.final_profile_build")
def final_profile_build_task(
    session_id: str,
    prompt_version_id: str,
) -> str:
    with SessionLocal() as db:
        row = run_final_profile_build_stage(
            db,
            session_id=session_id,
            prompt_version_id=prompt_version_id,
        )
        return str(row.id)
