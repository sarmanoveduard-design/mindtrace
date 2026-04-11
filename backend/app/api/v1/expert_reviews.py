from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import ExpertReview
from app.models.entities import Session as SessionModel
from app.schemas.expert_review import ExpertReviewCreateRequest
from app.schemas.expert_review import ExpertReviewCreateResponse

router = APIRouter(prefix="/sessions", tags=["expert_reviews"])


@router.post(
    "/{session_id}/expert-reviews",
    response_model=ExpertReviewCreateResponse,
)
def create_expert_review(
    session_id: str,
    payload: ExpertReviewCreateRequest,
    db: Session = Depends(get_db),
) -> ExpertReviewCreateResponse:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    row = ExpertReview(
        session_id=session_id,
        expert_user_id=payload.expert_user_id,
        score=payload.score,
        comment=payload.comment,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return ExpertReviewCreateResponse(
        id=str(row.id),
        session_id=str(row.session_id),
        expert_user_id=str(row.expert_user_id),
        score=row.score,
        comment=row.comment,
    )
