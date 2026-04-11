from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Answer
from app.models.entities import Question
from app.models.entities import Session as SessionModel
from app.schemas.expert_session_detail import ExpertAnswerExtractionItem
from app.schemas.expert_session_detail import ExpertAnswerItem
from app.schemas.expert_session_detail import ExpertSessionDetailResponse
from app.services.ai_reads import get_latest_ready_final_profile
from app.services.ai_reads import get_latest_successful_answer_extract
from app.services.ai_reads import get_latest_successful_session_aggregate

router = APIRouter(prefix="/sessions", tags=["expert_session_detail"])


@router.get(
    "/{session_id}/expert-detail",
    response_model=ExpertSessionDetailResponse,
)
def get_expert_session_detail(
    session_id: str,
    db: Session = Depends(get_db),
) -> ExpertSessionDetailResponse:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    questions_stmt = (
        select(Question)
        .where(Question.taxonomy_version_id == session.taxonomy_version_id)
        .where(Question.is_active.is_(True))
        .order_by(Question.order_no.asc())
    )
    questions = db.execute(questions_stmt).scalars().all()
    questions_by_id = {str(question.id): question for question in questions}

    answers_stmt = (
        select(Answer)
        .where(Answer.session_id == session_id)
        .where(Answer.is_current.is_(True))
        .order_by(Answer.created_at.asc())
    )
    answers = db.execute(answers_stmt).scalars().all()

    answer_items: list[ExpertAnswerItem] = []
    for answer in answers:
        question = questions_by_id.get(str(answer.question_id))
        if question is None:
            continue

        extraction = get_latest_successful_answer_extract(
            db,
            answer_id=str(answer.id),
        )

        extraction_item = None
        if extraction is not None:
            extraction_item = ExpertAnswerExtractionItem(
                extraction_id=str(extraction.id),
                status=extraction.status,
                confidence_score=(
                    float(extraction.confidence_score)
                    if extraction.confidence_score is not None
                    else None
                ),
                normalized_output=extraction.normalized_output,
            )

        answer_items.append(
            ExpertAnswerItem(
                answer_id=str(answer.id),
                question_id=str(answer.question_id),
                question_code=question.code,
                question_title=question.title,
                revision_no=answer.revision_no,
                ai_status=answer.ai_status,
                answer_text=answer.answer_text,
                answer_payload=answer.answer_payload,
                extraction=extraction_item,
            ),
        )

    aggregate = get_latest_successful_session_aggregate(
        db,
        session_id=session_id,
    )
    final_profile = get_latest_ready_final_profile(
        db,
        session_id=session_id,
    )

    return ExpertSessionDetailResponse(
        session_id=str(session.id),
        taxonomy_version_id=str(session.taxonomy_version_id),
        status=session.status,
        answers=answer_items,
        session_aggregate=(
            aggregate.aggregate_json if aggregate is not None else None
        ),
        final_profile=(
            final_profile.profile_json if final_profile is not None else None
        ),
    )
