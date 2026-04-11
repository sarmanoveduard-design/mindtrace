from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Answer
from app.models.entities import Question
from app.models.entities import Session as SessionModel
from app.services.ai_dispatch import enqueue_answer_extract
from app.services.prompt_reads import get_active_prompt_version_or_raise


def save_answer_and_enqueue_extraction(
    db: Session,
    *,
    session_id: str,
    question_id: str,
    source: str,
    answer_text: str | None = None,
    answer_payload: dict[str, Any] | None = None,
    client_event_id: str | None = None,
) -> tuple[Answer, str]:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise ValueError("Session not found.")

    question = db.get(Question, question_id)
    if question is None:
        raise ValueError("Question not found.")

    if question.taxonomy_version_id != session.taxonomy_version_id:
        raise ValueError("Question does not belong to session taxonomy.")

    max_revision_stmt = (
        select(func.max(Answer.revision_no))
        .where(Answer.session_id == session_id)
        .where(Answer.question_id == question_id)
    )
    max_revision = db.execute(max_revision_stmt).scalar_one()
    next_revision = 1 if max_revision is None else int(max_revision) + 1

    current_answers_stmt = (
        select(Answer)
        .where(Answer.session_id == session_id)
        .where(Answer.question_id == question_id)
        .where(Answer.is_current.is_(True))
    )
    current_answers = db.execute(current_answers_stmt).scalars().all()
    for current_answer in current_answers:
        current_answer.is_current = False

    answer = Answer(
        session_id=session_id,
        question_id=question_id,
        revision_no=next_revision,
        answer_text=answer_text,
        answer_payload=answer_payload,
        source=source,
        is_current=True,
        ai_status="queued",
        client_event_id=client_event_id,
    )
    db.add(answer)
    db.flush()

    update_session_progress_after_answer(
        db,
        session=session,
    )

    db.commit()
    db.refresh(answer)

    prompt_version = get_active_prompt_version_or_raise(
        db,
        stage_code="answer_extract",
    )
    task_id = enqueue_answer_extract(
        answer_id=str(answer.id),
        prompt_version_id=str(prompt_version.id),
    )

    return answer, task_id


def update_session_progress_after_answer(
    db: Session,
    *,
    session: SessionModel,
) -> None:
    next_question_stmt = (
        select(Question)
        .where(Question.taxonomy_version_id == session.taxonomy_version_id)
        .where(Question.is_active.is_(True))
        .where(
            ~Question.id.in_(
                select(Answer.question_id).where(
                    and_(
                        Answer.session_id == session.id,
                        Answer.is_current.is_(True),
                    ),
                ),
            ),
        )
        .order_by(Question.order_no.asc())
        .limit(1)
    )
    next_question = db.execute(next_question_stmt).scalar_one_or_none()

    session.last_activity_at = func.now()

    if session.status == "created":
        session.status = "in_progress"

    if next_question is None:
        session.status = "processing"
    else:
        session.current_question_order = next_question.order_no
