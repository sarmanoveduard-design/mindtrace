from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.answer import AnswerCreateRequest
from app.schemas.answer import AnswerCreateResponse
from app.services.answer_writes import save_answer_and_enqueue_extraction

router = APIRouter(prefix="/sessions", tags=["answers"])


@router.post(
    "/{session_id}/answers",
    response_model=AnswerCreateResponse,
)
def create_answer(
    session_id: str,
    payload: AnswerCreateRequest,
    db: Session = Depends(get_db),
) -> AnswerCreateResponse:
    try:
        answer, task_id = save_answer_and_enqueue_extraction(
            db,
            session_id=session_id,
            question_id=payload.question_id,
            source=payload.source,
            answer_text=payload.answer_text,
            answer_payload=payload.answer_payload,
            client_event_id=payload.client_event_id,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 404 if detail in {
            "Session not found.",
            "Question not found.",
            "Active prompt version not found.",
        } else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return AnswerCreateResponse(
        answer_id=str(answer.id),
        session_id=str(answer.session_id),
        question_id=str(answer.question_id),
        revision_no=answer.revision_no,
        ai_status=answer.ai_status,
        celery_task_id=task_id,
    )
