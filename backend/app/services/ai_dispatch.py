from __future__ import annotations

from app.tasks.ai_tasks import answer_extract_task
from app.tasks.ai_tasks import final_profile_build_task
from app.tasks.ai_tasks import session_aggregate_task


def enqueue_answer_extract(
    *,
    answer_id: str,
    prompt_version_id: str,
) -> str:
    task = answer_extract_task.delay(
        answer_id=answer_id,
        prompt_version_id=prompt_version_id,
    )
    return str(task.id)


def enqueue_session_aggregate(
    *,
    session_id: str,
    prompt_version_id: str,
) -> str:
    task = session_aggregate_task.delay(
        session_id=session_id,
        prompt_version_id=prompt_version_id,
    )
    return str(task.id)


def enqueue_final_profile_build(
    *,
    session_id: str,
    prompt_version_id: str,
) -> str:
    task = final_profile_build_task.delay(
        session_id=session_id,
        prompt_version_id=prompt_version_id,
    )
    return str(task.id)
