from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Question
from app.models.entities import TaxonomyVersion
from app.schemas.taxonomy import ActiveQuestionsResponse
from app.schemas.taxonomy import QuestionItemResponse
from app.schemas.taxonomy import TaxonomyActiveResponse

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("/active", response_model=TaxonomyActiveResponse)
def get_active_taxonomy(db: Session = Depends(get_db)) -> TaxonomyActiveResponse:
    stmt = (
        select(TaxonomyVersion)
        .where(TaxonomyVersion.status == "active")
        .limit(1)
    )
    taxonomy = db.execute(stmt).scalar_one_or_none()

    if taxonomy is None:
        raise HTTPException(
            status_code=404,
            detail="Active taxonomy version not found.",
        )

    return TaxonomyActiveResponse(
        id=str(taxonomy.id),
        code=taxonomy.code,
        version_label=taxonomy.version_label,
        title=taxonomy.title,
        description=taxonomy.description,
        status=taxonomy.status,
    )


@router.get(
    "/active/questions",
    response_model=ActiveQuestionsResponse,
)
def get_active_taxonomy_questions(
    db: Session = Depends(get_db),
) -> ActiveQuestionsResponse:
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

    questions_stmt = (
        select(Question)
        .where(Question.taxonomy_version_id == taxonomy.id)
        .where(Question.is_active.is_(True))
        .order_by(Question.order_no.asc())
    )
    questions = db.execute(questions_stmt).scalars().all()

    return ActiveQuestionsResponse(
        taxonomy_version_id=str(taxonomy.id),
        questions=[
            QuestionItemResponse(
                id=str(question.id),
                code=question.code,
                order_no=question.order_no,
                title=question.title,
                description=question.description,
                question_type=question.question_type,
                is_required=question.is_required,
                is_active=question.is_active,
            )
            for question in questions
        ],
    )
