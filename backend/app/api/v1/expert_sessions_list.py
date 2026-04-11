from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Answer
from app.models.entities import FinalProfile
from app.models.entities import Question
from app.models.entities import Session as SessionModel
from app.schemas.expert_sessions_list import ExpertSessionListItem
from app.schemas.expert_sessions_list import ExpertSessionsListResponse

router = APIRouter(prefix="/expert", tags=["expert_sessions"])


@router.get(
    "/sessions",
    response_model=ExpertSessionsListResponse,
)
def get_expert_sessions_list(
    db: Session = Depends(get_db),
) -> ExpertSessionsListResponse:
    sessions_stmt = (
        select(SessionModel)
        .order_by(SessionModel.created_at.desc())
        .limit(50)
    )
    sessions = db.execute(sessions_stmt).scalars().all()

    items: list[ExpertSessionListItem] = []

    for session in sessions:
        answered_stmt = (
            select(func.count())
            .select_from(Answer)
            .where(Answer.session_id == session.id)
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

        final_profile_stmt = (
            select(FinalProfile)
            .where(FinalProfile.session_id == session.id)
            .order_by(FinalProfile.created_at.desc())
            .limit(1)
        )
        final_profile = db.execute(final_profile_stmt).scalar_one_or_none()

        items.append(
            ExpertSessionListItem(
                session_id=str(session.id),
                user_id=str(session.user_id),
                status=session.status,
                channel=session.channel,
                current_question_order=session.current_question_order,
                answered_questions=int(answered_questions),
                total_questions=int(total_questions),
                has_final_profile=final_profile is not None,
                final_profile_status=(
                    final_profile.status if final_profile is not None else None
                ),
            ),
        )

    return ExpertSessionsListResponse(sessions=items)
