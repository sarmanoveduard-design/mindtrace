from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Session as SessionModel
from app.models.entities import User
from app.models.entities import TaxonomyVersion


ACTIVE_SESSION_STATUSES = {
    "created",
    "in_progress",
    "processing",
}


def get_active_taxonomy_or_raise(
    db: Session,
) -> TaxonomyVersion:
    stmt = (
        select(TaxonomyVersion)
        .where(TaxonomyVersion.status == "active")
        .limit(1)
    )
    taxonomy = db.execute(stmt).scalar_one_or_none()

    if taxonomy is None:
        raise ValueError("Active taxonomy version not found.")

    return taxonomy


def ensure_user_exists(
    db: Session,
    *,
    user_id: str,
) -> None:
    user = db.get(User, user_id)
    if user is not None:
        return

    row = User(
        id=user_id,
        display_name=f"User {user_id[:8]}",
    )
    db.add(row)
    db.flush()


def get_or_create_session(
    db: Session,
    *,
    user_id: str,
    channel: str,
) -> tuple[SessionModel, bool]:
    existing_stmt = (
        select(SessionModel)
        .where(SessionModel.user_id == user_id)
        .where(SessionModel.status.in_(ACTIVE_SESSION_STATUSES))
        .order_by(SessionModel.created_at.desc())
        .limit(1)
    )
    existing = db.execute(existing_stmt).scalar_one_or_none()

    if existing is not None:
        return existing, True

    ensure_user_exists(db, user_id=user_id)

    taxonomy = get_active_taxonomy_or_raise(db)

    session = SessionModel(
        user_id=user_id,
        taxonomy_version_id=taxonomy.id,
        channel=channel,
        status="created",
        current_question_order=1,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session, False
