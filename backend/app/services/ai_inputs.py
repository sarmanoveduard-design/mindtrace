from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Answer
from app.models.entities import Question
from app.models.entities import Session as SessionModel
from app.services.ai_reads import get_latest_successful_answer_extract
from app.services.ai_reads import get_latest_successful_session_aggregate
from app.services.ai_reads import list_current_answer_ids_for_session


def build_answer_extract_input(
    db: Session,
    *,
    answer_id: str,
) -> dict:
    answer = db.get(Answer, answer_id)
    if answer is None:
        raise ValueError("Answer not found.")

    question = db.get(Question, answer.question_id)
    if question is None:
        raise ValueError("Question not found.")

    session = db.get(SessionModel, answer.session_id)
    if session is None:
        raise ValueError("Session not found.")

    return {
        "answer_id": str(answer.id),
        "session_id": str(answer.session_id),
        "question_id": str(answer.question_id),
        "taxonomy_version_id": str(session.taxonomy_version_id),
        "answer_text": answer.answer_text,
        "answer_payload": answer.answer_payload,
        "question": {
            "id": str(question.id),
            "code": question.code,
            "order_no": question.order_no,
            "title": question.title,
            "description": question.description,
            "question_type": question.question_type,
            "is_required": question.is_required,
        },
        "session": {
            "id": str(session.id),
            "status": session.status,
            "channel": session.channel,
        },
    }


def build_session_aggregate_input(
    db: Session,
    *,
    session_id: str,
) -> dict:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise ValueError("Session not found.")

    questions_stmt = (
        select(Question)
        .where(Question.taxonomy_version_id == session.taxonomy_version_id)
        .where(Question.is_active.is_(True))
        .order_by(Question.order_no.asc())
    )
    taxonomy_questions = db.execute(questions_stmt).scalars().all()

    answer_ids = list_current_answer_ids_for_session(db, session_id=session_id)

    answers_payload: list[dict] = []
    extractions_payload: list[dict] = []

    for answer_id in answer_ids:
        answer = db.get(Answer, answer_id)
        if answer is None:
            continue

        question = db.get(Question, answer.question_id)
        if question is None:
            continue

        extraction = get_latest_successful_answer_extract(db, answer_id=answer_id)

        answers_payload.append(
            {
                "answer_id": str(answer.id),
                "question_id": str(answer.question_id),
                "question_code": question.code,
                "answer_text": answer.answer_text,
                "answer_payload": answer.answer_payload,
            },
        )

        if extraction is not None:
            extractions_payload.append(
                {
                    "answer_id": str(answer.id),
                    "question_id": str(answer.question_id),
                    "question_code": question.code,
                    "extraction_id": str(extraction.id),
                    "normalized_output": extraction.normalized_output,
                    "confidence_score": (
                        float(extraction.confidence_score)
                        if extraction.confidence_score is not None
                        else None
                    ),
                },
            )

    return {
        "session_id": str(session.id),
        "taxonomy_version_id": str(session.taxonomy_version_id),
        "taxonomy_questions": [
            {
                "id": str(question.id),
                "code": question.code,
                "order_no": question.order_no,
                "title": question.title,
                "is_required": question.is_required,
                "is_active": question.is_active,
            }
            for question in taxonomy_questions
        ],
        "answers": answers_payload,
        "answer_extractions": extractions_payload,
    }


def build_final_profile_input(
    db: Session,
    *,
    session_id: str,
) -> dict:
    session = db.get(SessionModel, session_id)
    if session is None:
        raise ValueError("Session not found.")

    aggregate = get_latest_successful_session_aggregate(
        db,
        session_id=session_id,
    )
    if aggregate is None:
        raise ValueError("Session aggregate not found.")

    answer_ids = list_current_answer_ids_for_session(db, session_id=session_id)

    extraction_trace: list[dict] = []
    for answer_id in answer_ids:
        extraction = get_latest_successful_answer_extract(db, answer_id=answer_id)
        if extraction is None:
            continue

        extraction_trace.append(
            {
                "answer_id": str(extraction.answer_id),
                "question_id": str(extraction.question_id),
                "normalized_output": extraction.normalized_output,
                "confidence_score": (
                    float(extraction.confidence_score)
                    if extraction.confidence_score is not None
                    else None
                ),
            },
        )

    return {
        "session_id": str(session.id),
        "taxonomy_version_id": str(session.taxonomy_version_id),
        "session_aggregate": aggregate.aggregate_json,
        "answer_extract_trace": extraction_trace,
    }
