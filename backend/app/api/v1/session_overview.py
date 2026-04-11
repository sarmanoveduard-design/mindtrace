from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.session_questions import get_session_questions
from app.api.v1.session_status import get_session_status
from app.db.session import get_db
from app.schemas.ai.final_profile import FinalProfileBuildResult
from app.schemas.session_overview import SessionOverviewResponse
from app.services.ai_reads import get_latest_ready_final_profile

router = APIRouter(prefix="/sessions", tags=["session_overview"])


@router.get(
    "/{session_id}/overview",
    response_model=SessionOverviewResponse,
)
def get_session_overview(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionOverviewResponse:
    status = get_session_status(
        session_id=session_id,
        db=db,
    )
    questions = get_session_questions(
        session_id=session_id,
        db=db,
    )

    final_profile_row = get_latest_ready_final_profile(
        db,
        session_id=session_id,
    )

    final_profile: FinalProfileBuildResult | None = None
    if final_profile_row is not None:
        if final_profile_row.profile_json is None:
            raise HTTPException(
                status_code=500,
                detail="Final profile row has no profile_json.",
            )
        final_profile = FinalProfileBuildResult.model_validate(
            final_profile_row.profile_json,
        )

    return SessionOverviewResponse(
        status=status,
        questions=questions,
        final_profile=final_profile,
    )
