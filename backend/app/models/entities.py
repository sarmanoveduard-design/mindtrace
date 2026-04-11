from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base import Base
from app.models.base import DB_SCHEMA

JSONB_EMPTY = text("'{}'::jsonb")
UUID_DEFAULT = text("gen_random_uuid()")
NOW = text("now()")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'expert', 'admin')",
            name="users_role_check",
        ),
        Index("ix_users_role", "role"),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    supabase_auth_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        unique=True,
    )
    telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        unique=True,
    )
    telegram_username: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'user'"),
    )
    locale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'ru'"),
    )
    timezone: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'UTC'"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class TaxonomyVersion(Base):
    __tablename__ = "taxonomy_versions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="taxonomy_versions_status_check",
        ),
        Index("ix_taxonomy_versions_status", "status"),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    version_label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    schema_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    rules_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "taxonomy_version_id",
            "code",
            name="uq_questions_taxonomy_version_id_code",
        ),
        UniqueConstraint(
            "taxonomy_version_id",
            "order_no",
            name="uq_questions_taxonomy_version_id_order_no",
        ),
        CheckConstraint(
            "question_type IN ('text', 'single_choice', 'multi_choice', 'scale')",
            name="questions_question_type_check",
        ),
        CheckConstraint(
            "order_no > 0",
            name="questions_order_no_check",
        ),
        Index(
            "ix_questions_taxonomy_version_id_order_no",
            "taxonomy_version_id",
            "order_no",
        ),
        Index(
            "ix_questions_taxonomy_version_id_is_active",
            "taxonomy_version_id",
            "is_active",
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    taxonomy_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.taxonomy_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    order_no: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    question_type: Mapped[str] = mapped_column(Text, nullable=False)
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    ui_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    validation_rules: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('web', 'telegram', 'mini_app')",
            name="sessions_channel_check",
        ),
        CheckConstraint(
            "status IN ("
            "'created', "
            "'in_progress', "
            "'processing', "
            "'completed', "
            "'ready', "
            "'failed', "
            "'archived'"
            ")",
            name="sessions_status_check",
        ),
        CheckConstraint(
            "current_question_order > 0",
            name="sessions_current_question_order_check",
        ),
        Index("ix_sessions_user_id_status", "user_id", "status"),
        Index(
            "ix_sessions_taxonomy_version_id_status",
            "taxonomy_version_id",
            "status",
        ),
        Index("ix_sessions_last_activity_at", "last_activity_at"),
        Index(
            "uq_sessions_active_user_taxonomy",
            "user_id",
            "taxonomy_version_id",
            unique=True,
            postgresql_where=text(
                "status IN ('created', 'in_progress', 'processing')",
            ),
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    taxonomy_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.taxonomy_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'created'"),
    )
    current_question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    meta_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_id",
            "revision_no",
            name="uq_answers_session_id_question_id_revision_no",
        ),
        CheckConstraint(
            "source IN ('web', 'telegram', 'mini_app')",
            name="answers_source_check",
        ),
        CheckConstraint(
            "ai_status IN ('pending', 'queued', 'processing', 'done', 'failed')",
            name="answers_ai_status_check",
        ),
        CheckConstraint(
            "revision_no > 0",
            name="answers_revision_no_check",
        ),
        CheckConstraint(
            "answer_text IS NOT NULL OR answer_payload IS NOT NULL",
            name="answers_content_check",
        ),
        Index("ix_answers_session_id_question_id", "session_id", "question_id"),
        Index("ix_answers_session_id_is_current", "session_id", "is_current"),
        Index("ix_answers_ai_status", "ai_status"),
        Index(
            "uq_answers_client_event_id_not_null",
            "client_event_id",
            unique=True,
            postgresql_where=text("client_event_id IS NOT NULL"),
        ),
        Index(
            "uq_answers_current_session_question",
            "session_id",
            "question_id",
            unique=True,
            postgresql_where=text("is_current = true"),
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.questions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    revision_no: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    ai_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )
    client_event_id: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint(
            "stage_code",
            "version_label",
            name="uq_prompt_versions_stage_code_version_label",
        ),
        CheckConstraint(
            "stage_code IN ("
            "'answer_precheck', "
            "'answer_extract', "
            "'session_aggregate', "
            "'final_profile_build', "
            "'final_profile_summary'"
            ")",
            name="prompt_versions_stage_code_check",
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="prompt_versions_status_check",
        ),
        Index(
            "ix_prompt_versions_stage_code_status",
            "stage_code",
            "status",
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    stage_code: Mapped[str] = mapped_column(Text, nullable=False)
    version_label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    developer_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    schema_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    model_config_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id", ondelete="SET NULL"),
        nullable=True,
    )


class AnswerExtraction(Base):
    __tablename__ = "answer_extractions"
    __table_args__ = (
        CheckConstraint(
            "stage_code IN ('answer_precheck', 'answer_extract')",
            name="answer_extractions_stage_code_check",
        ),
        CheckConstraint(
            "status IN ('queued', 'processing', 'done', 'failed')",
            name="answer_extractions_status_check",
        ),
        CheckConstraint(
            "confidence_score IS NULL "
            "OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="answer_extractions_confidence_score_check",
        ),
        Index(
            "ix_answer_extractions_answer_id_stage_code",
            "answer_id",
            "stage_code",
        ),
        Index("ix_answer_extractions_session_id", "session_id"),
        Index("ix_answer_extractions_status", "status"),
        Index(
            "ix_answer_extractions_normalized_output_gin",
            "normalized_output",
            postgresql_using="gin",
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    answer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.answers.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.questions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    stage_code: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.prompt_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    input_snapshot: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    raw_output_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    normalized_output: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )
    token_usage_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class SessionAggregate(Base):
    __tablename__ = "session_aggregates"
    __table_args__ = (
        CheckConstraint(
            "stage_code IN ('session_aggregate')",
            name="session_aggregates_stage_code_check",
        ),
        CheckConstraint(
            "status IN ('queued', 'processing', 'done', 'failed')",
            name="session_aggregates_status_check",
        ),
        Index("ix_session_aggregates_status", "status"),
        Index(
            "ix_session_aggregates_aggregate_json_gin",
            "aggregate_json",
            postgresql_using="gin",
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    stage_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'session_aggregate'"),
    )
    prompt_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.prompt_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    aggregate_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    coverage_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    confidence_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    raw_output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class FinalProfile(Base):
    __tablename__ = "final_profiles"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_final_profiles_session_id"),
        CheckConstraint(
            "status IN ('queued', 'processing', 'ready', 'failed', 'reviewed')",
            name="final_profiles_status_check",
        ),
        Index("ix_final_profiles_status", "status"),
        Index(
            "ix_final_profiles_profile_json_gin",
            "profile_json",
            postgresql_using="gin",
        ),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    prompt_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.prompt_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    profile_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    raw_output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class ExpertReview(Base):
    __tablename__ = "expert_reviews"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'approved', 'rejected')",
            name="expert_reviews_status_check",
        ),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score BETWEEN 1 AND 5)",
            name="expert_reviews_quality_score_check",
        ),
        Index("ix_expert_reviews_session_id", "session_id"),
        Index(
            "ix_expert_reviews_reviewer_user_id_status",
            "reviewer_user_id",
            "status",
        ),
        Index("ix_expert_reviews_quality_score", "quality_score"),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    final_profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.final_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )
    quality_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    notes_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrections_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class AIJob(Base):
    __tablename__ = "ai_jobs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_ai_jobs_idempotency_key"),
        CheckConstraint(
            "job_type IN ('answer_extract', 'session_aggregate', 'final_profile')",
            name="ai_jobs_job_type_check",
        ),
        CheckConstraint(
            "entity_type IN ('answer', 'session', 'profile')",
            name="ai_jobs_entity_type_check",
        ),
        CheckConstraint(
            "status IN ("
            "'queued', "
            "'started', "
            "'retry', "
            "'succeeded', "
            "'failed', "
            "'dead'"
            ")",
            name="ai_jobs_status_check",
        ),
        CheckConstraint(
            "attempt_no >= 0",
            name="ai_jobs_attempt_no_check",
        ),
        CheckConstraint(
            "max_attempts > 0",
            name="ai_jobs_max_attempts_check",
        ),
        Index("ix_ai_jobs_status_scheduled_at", "status", "scheduled_at"),
        Index("ix_ai_jobs_session_id", "session_id"),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    job_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("100"),
    )
    attempt_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("3"),
    )
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index(
            "ix_audit_logs_entity_type_entity_id",
            "entity_type",
            "entity_id",
        ),
        Index("ix_audit_logs_session_id", "session_id"),
        Index("ix_audit_logs_created_at", "created_at"),
        {"schema": DB_SCHEMA},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=UUID_DEFAULT,
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    payload_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=JSONB_EMPTY,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
    )
