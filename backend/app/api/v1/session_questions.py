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
from app.schemas.session_questions import SessionQuestionItem
from app.schemas.session_questions import SessionQuestionsResponse

router = APIRouter(prefix="/sessions", tags=["session_questions"])


@router.get(
    "/{session_id}/questions",
    response_model=SessionQuestionsResponse,
)
def get_session_questions(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionQuestionsResponse:
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

    answers_stmt = (
        select(Answer)
        .where(Answer.session_id == session_id)
        .where(Answer.is_current.is_(True))
    )
    current_answers = db.execute(answers_stmt).scalars().all()
    answers_by_question_id = {
        str(answer.question_id): answer for answer in current_answers
    }

    items: list[SessionQuestionItem] = []
    for question in questions:
        answer = answers_by_question_id.get(str(question.id))

        items.append(
            SessionQuestionItem(
                id=str(question.id),
                code=question.code,
                order_no=question.order_no,
                title=question.title,
                description=question.description,
                question_type=question.question_type,
                is_required=question.is_required,
                is_active=question.is_active,
                has_answer=answer is not None,
                answer_id=str(answer.id) if answer is not None else None,
                revision_no=answer.revision_no if answer is not None else None,
                ai_status=answer.ai_status if answer is not None else None,
                is_current_question=(
                    session.status != "ready"
                    and question.order_no == session.current_question_order
                ),
            ),
        )

    return SessionQuestionsResponse(
        session_id=str(session.id),
        taxonomy_version_id=str(session.taxonomy_version_id),
        current_question_order=session.current_question_order,
        questions=items,
    )
