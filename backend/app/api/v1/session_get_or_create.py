from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.session_get_or_create import SessionGetOrCreateRequest
from app.schemas.session_get_or_create import SessionGetOrCreateResponse
from app.services.session_get_or_create import get_or_create_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post(
    "/get-or-create",
    response_model=SessionGetOrCreateResponse,
)
def get_or_create_session_endpoint(
    payload: SessionGetOrCreateRequest,
    db: Session = Depends(get_db),
) -> SessionGetOrCreateResponse:
    try:
        session, is_existing = get_or_create_session(
            db,
            user_id=payload.user_id,
            channel=payload.channel,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SessionGetOrCreateResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        taxonomy_version_id=str(session.taxonomy_version_id),
        channel=session.channel,
        status=session.status,
        current_question_order=session.current_question_order,
        is_existing=is_existing,
    )
