from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Answer
from app.models.entities import Question
from app.models.entities import Session as SessionModel
from app.schemas.session_status import SessionStatusQuestion
from app.schemas.session_status import SessionStatusResponse
from app.services.ai_reads import get_latest_ready_final_profile

router = APIRouter(prefix="/sessions", tags=["session_status"])


@router.get(
    "/{session_id}/status",
    response_model=SessionStatusResponse,
)
def get_session_status(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionStatusResponse:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    answered_stmt = (
        select(func.count())
        .select_from(Answer)
        .where(Answer.session_id == session_id)
        .where(Answer.is_current.is_(True))
    )
    answered_questions = db.execute(answered_stmt).scalar_one()

    total_stmt = (
        select(func.count())
        .select_from(Question)
        .where(Question.taxonomy_version_id == session.taxonomy_version_id)
        .where(Question.is_active.is_(True))
    )
    total_questions = db.execute(total_stmt).scalar_one()

    current_question_row = None
    if session.status != "ready" and int(answered_questions) < int(total_questions):
        current_question_stmt = (
            select(Question)
            .where(Question.taxonomy_version_id == session.taxonomy_version_id)
            .where(Question.is_active.is_(True))
            .where(Question.order_no == session.current_question_order)
            .limit(1)
        )
        current_question_row = db.execute(
            current_question_stmt,
        ).scalar_one_or_none()

    final_profile = get_latest_ready_final_profile(
        db,
        session_id=session_id,
    )

    current_question = None
    if current_question_row is not None:
        current_question = SessionStatusQuestion(
            id=str(current_question_row.id),
            code=current_question_row.code,
            order_no=current_question_row.order_no,
            title=current_question_row.title,
            description=current_question_row.description,
            question_type=current_question_row.question_type,
            is_required=current_question_row.is_required,
        )

    return SessionStatusResponse(
        session_id=str(session.id),
        taxonomy_version_id=str(session.taxonomy_version_id),
        status=session.status,
        channel=session.channel,
        current_question_order=session.current_question_order,
        answered_questions=int(answered_questions),
        total_questions=int(total_questions),
        has_final_profile=final_profile is not None,
        final_profile_status=final_profile.status if final_profile else None,
        current_question=current_question,
    )
