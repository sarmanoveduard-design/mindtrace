from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai.final_profile import FinalProfileBuildResult
from app.services.ai_reads import get_latest_ready_final_profile

router = APIRouter(prefix="/sessions", tags=["final_profiles"])


@router.get(
    "/{session_id}/final-profile",
    response_model=FinalProfileBuildResult,
)
def get_latest_final_profile(
    session_id: str,
    db: Session = Depends(get_db),
) -> FinalProfileBuildResult:
    row = get_latest_ready_final_profile(
        db,
        session_id=session_id,
    )
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Final profile not found.",
        )

    return FinalProfileBuildResult.model_validate(row.profile_json)
