from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Session as SessionModel
from app.models.entities import TaxonomyVersion
from app.models.entities import User
from app.schemas.session import SessionCreateRequest
from app.schemas.session import SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

ACTIVE_SESSION_STATUSES = (
    "created",
    "in_progress",
    "processing",
)


@router.post("", response_model=SessionResponse)
def create_or_continue_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    taxonomy_stmt = (
        select(TaxonomyVersion)
        .where(TaxonomyVersion.status == "active")
        .limit(1)
    )
    taxonomy = db.execute(taxonomy_stmt).scalar_one_or_none()

    if taxonomy is None:
        raise HTTPException(
            status_code=404,
            detail="Active taxonomy version not found.",
        )

    session_stmt = (
        select(SessionModel)
        .where(SessionModel.user_id == payload.user_id)
        .where(SessionModel.taxonomy_version_id == taxonomy.id)
        .where(SessionModel.status.in_(ACTIVE_SESSION_STATUSES))
        .limit(1)
    )
    existing_session = db.execute(session_stmt).scalar_one_or_none()

    if existing_session is not None:
        return SessionResponse(
            id=str(existing_session.id),
            user_id=str(existing_session.user_id),
            taxonomy_version_id=str(existing_session.taxonomy_version_id),
            channel=existing_session.channel,
            status=existing_session.status,
            current_question_order=existing_session.current_question_order,
        )

    session = SessionModel(
        user_id=payload.user_id,
        taxonomy_version_id=taxonomy.id,
        channel=payload.channel,
        status="created",
        current_question_order=1,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        taxonomy_version_id=str(session.taxonomy_version_id),
        channel=session.channel,
        status=session.status,
        current_question_order=session.current_question_order,
    )
