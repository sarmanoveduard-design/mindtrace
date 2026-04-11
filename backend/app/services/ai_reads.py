from __future__ import annotations

from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Answer
from app.models.entities import AnswerExtraction
from app.models.entities import FinalProfile
from app.models.entities import SessionAggregate


def get_latest_successful_answer_extract(
    db: Session,
    *,
    answer_id: str,
) -> AnswerExtraction | None:
    stmt = (
        select(AnswerExtraction)
        .where(AnswerExtraction.answer_id == answer_id)
        .where(AnswerExtraction.stage_code == "answer_extract")
        .where(AnswerExtraction.status == "done")
        .order_by(desc(AnswerExtraction.created_at))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_latest_successful_session_aggregate(
    db: Session,
    *,
    session_id: str,
) -> SessionAggregate | None:
    stmt = (
        select(SessionAggregate)
        .where(SessionAggregate.session_id == session_id)
        .where(SessionAggregate.stage_code == "session_aggregate")
        .where(SessionAggregate.status == "done")
        .order_by(desc(SessionAggregate.created_at))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_latest_ready_final_profile(
    db: Session,
    *,
    session_id: str,
) -> FinalProfile | None:
    stmt = (
        select(FinalProfile)
        .where(FinalProfile.session_id == session_id)
        .where(FinalProfile.status == "ready")
        .order_by(desc(FinalProfile.created_at))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_current_answer_ids_for_session(
    db: Session,
    *,
    session_id: str,
) -> list[str]:
    stmt = (
        select(Answer.id)
        .where(Answer.session_id == session_id)
        .where(Answer.is_current.is_(True))
        .order_by(Answer.created_at.asc())
    )
    return [str(answer_id) for answer_id in db.execute(stmt).scalars().all()]
