"""initial mindtrace schema

Revision ID: 20260410_0001
Revises:
Create Date: 2026-04-10 00:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260410_0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "mindtrace"
JSONB_EMPTY = sa.text("'{}'::jsonb")
UUID_DEFAULT = sa.text("gen_random_uuid()")
NOW = sa.text("now()")


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("supabase_auth_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_username", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column(
            "role",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'user'"),
        ),
        sa.Column(
            "locale",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'ru'"),
        ),
        sa.Column(
            "timezone",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'UTC'"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'expert', 'admin')",
            name="ck_users_role",
        ),
        sa.UniqueConstraint(
            "supabase_auth_id",
            name="uq_users_supabase_auth_id",
        ),
        sa.UniqueConstraint(
            "telegram_user_id",
            name="uq_users_telegram_user_id",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_users_role",
        "users",
        ["role"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "taxonomy_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("version_label", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "schema_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "rules_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_taxonomy_versions_status",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            [f"{SCHEMA}.users.id"],
            ondelete="SET NULL",
            name="fk_taxonomy_versions_created_by_users",
        ),
        sa.UniqueConstraint("code", name="uq_taxonomy_versions_code"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_taxonomy_versions_status",
        "taxonomy_versions",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "questions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("taxonomy_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("question_type", sa.Text(), nullable=False),
        sa.Column(
            "is_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "ui_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "validation_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "question_type IN ('text', 'single_choice', 'multi_choice', 'scale')",
            name="ck_questions_question_type",
        ),
        sa.CheckConstraint(
            "order_no > 0",
            name="ck_questions_order_no",
        ),
        sa.ForeignKeyConstraint(
            ["taxonomy_version_id"],
            [f"{SCHEMA}.taxonomy_versions.id"],
            ondelete="CASCADE",
            name="fk_questions_taxonomy_version_id_taxonomy_versions",
        ),
        sa.UniqueConstraint(
            "taxonomy_version_id",
            "code",
            name="uq_questions_taxonomy_version_id_code",
        ),
        sa.UniqueConstraint(
            "taxonomy_version_id",
            "order_no",
            name="uq_questions_taxonomy_version_id_order_no",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_questions_taxonomy_version_id_order_no",
        "questions",
        ["taxonomy_version_id", "order_no"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_questions_taxonomy_version_id_is_active",
        "questions",
        ["taxonomy_version_id", "is_active"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("taxonomy_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'created'"),
        ),
        sa.Column(
            "current_question_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "meta_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "channel IN ('web', 'telegram', 'mini_app')",
            name="ck_sessions_channel",
        ),
        sa.CheckConstraint(
            "status IN ("
            "'created', "
            "'in_progress', "
            "'processing', "
            "'completed', "
            "'ready', "
            "'failed', "
            "'archived'"
            ")",
            name="ck_sessions_status",
        ),
        sa.CheckConstraint(
            "current_question_order > 0",
            name="ck_sessions_current_question_order",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{SCHEMA}.users.id"],
            ondelete="CASCADE",
            name="fk_sessions_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["taxonomy_version_id"],
            [f"{SCHEMA}.taxonomy_versions.id"],
            ondelete="RESTRICT",
            name="fk_sessions_taxonomy_version_id_taxonomy_versions",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_sessions_user_id_status",
        "sessions",
        ["user_id", "status"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_sessions_taxonomy_version_id_status",
        "sessions",
        ["taxonomy_version_id", "status"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_sessions_last_activity_at",
        "sessions",
        ["last_activity_at"],
        unique=False,
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX uq_sessions_active_user_taxonomy
        ON {SCHEMA}.sessions (user_id, taxonomy_version_id)
        WHERE status IN ('created', 'in_progress', 'processing')
        """,
    )

    op.create_table(
        "answers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column(
            "answer_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "ai_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("client_event_id", sa.Text(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "source IN ('web', 'telegram', 'mini_app')",
            name="ck_answers_source",
        ),
        sa.CheckConstraint(
            "ai_status IN ('pending', 'queued', 'processing', 'done', 'failed')",
            name="ck_answers_ai_status",
        ),
        sa.CheckConstraint(
            "revision_no > 0",
            name="ck_answers_revision_no",
        ),
        sa.CheckConstraint(
            "answer_text IS NOT NULL OR answer_payload IS NOT NULL",
            name="ck_answers_content",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_answers_session_id_sessions",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            [f"{SCHEMA}.questions.id"],
            ondelete="RESTRICT",
            name="fk_answers_question_id_questions",
        ),
        sa.UniqueConstraint(
            "session_id",
            "question_id",
            "revision_no",
            name="uq_answers_session_id_question_id_revision_no",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answers_session_id_question_id",
        "answers",
        ["session_id", "question_id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answers_session_id_is_current",
        "answers",
        ["session_id", "is_current"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answers_ai_status",
        "answers",
        ["ai_status"],
        unique=False,
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX uq_answers_client_event_id_not_null
        ON {SCHEMA}.answers (client_event_id)
        WHERE client_event_id IS NOT NULL
        """,
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX uq_answers_current_session_question
        ON {SCHEMA}.answers (session_id, question_id)
        WHERE is_current = true
        """,
    )

    op.create_table(
        "prompt_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("stage_code", sa.Text(), nullable=False),
        sa.Column("version_label", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("developer_prompt", sa.Text(), nullable=True),
        sa.Column(
            "schema_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "model_config_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "stage_code IN ("
            "'answer_precheck', "
            "'answer_extract', "
            "'session_aggregate', "
            "'final_profile_build', "
            "'final_profile_summary'"
            ")",
            name="ck_prompt_versions_stage_code",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_prompt_versions_status",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            [f"{SCHEMA}.users.id"],
            ondelete="SET NULL",
            name="fk_prompt_versions_created_by_users",
        ),
        sa.UniqueConstraint(
            "stage_code",
            "version_label",
            name="uq_prompt_versions_stage_code_version_label",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_prompt_versions_stage_code_status",
        "prompt_versions",
        ["stage_code", "status"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "answer_extractions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("answer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage_code", sa.Text(), nullable=False),
        sa.Column("prompt_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column(
            "input_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("raw_output_text", sa.Text(), nullable=True),
        sa.Column(
            "normalized_output",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column(
            "token_usage_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "stage_code IN ('answer_precheck', 'answer_extract')",
            name="ck_answer_extractions_stage_code",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'done', 'failed')",
            name="ck_answer_extractions_status",
        ),
        sa.CheckConstraint(
            "confidence_score IS NULL "
            "OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_answer_extractions_confidence_score",
        ),
        sa.ForeignKeyConstraint(
            ["answer_id"],
            [f"{SCHEMA}.answers.id"],
            ondelete="CASCADE",
            name="fk_answer_extractions_answer_id_answers",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_answer_extractions_session_id_sessions",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            [f"{SCHEMA}.questions.id"],
            ondelete="RESTRICT",
            name="fk_answer_extractions_question_id_questions",
        ),
        sa.ForeignKeyConstraint(
            ["prompt_version_id"],
            [f"{SCHEMA}.prompt_versions.id"],
            ondelete="RESTRICT",
            name="fk_answer_extractions_prompt_version_id_prompt_versions",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answer_extractions_answer_id_stage_code",
        "answer_extractions",
        ["answer_id", "stage_code"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answer_extractions_session_id",
        "answer_extractions",
        ["session_id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_answer_extractions_status",
        "answer_extractions",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE INDEX ix_answer_extractions_normalized_output_gin
        ON {SCHEMA}.answer_extractions
        USING gin (normalized_output)
        """,
    )

    op.create_table(
        "session_aggregates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "stage_code",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'session_aggregate'"),
        ),
        sa.Column("prompt_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "aggregate_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "coverage_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "confidence_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("raw_output_text", sa.Text(), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "stage_code IN ('session_aggregate')",
            name="ck_session_aggregates_stage_code",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'done', 'failed')",
            name="ck_session_aggregates_status",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_session_aggregates_session_id_sessions",
        ),
        sa.ForeignKeyConstraint(
            ["prompt_version_id"],
            [f"{SCHEMA}.prompt_versions.id"],
            ondelete="RESTRICT",
            name="fk_session_aggregates_prompt_version_id_prompt_versions",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_session_aggregates_status",
        "session_aggregates",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE INDEX ix_session_aggregates_session_id_created_at_desc
        ON {SCHEMA}.session_aggregates (session_id, created_at DESC)
        """,
    )
    op.execute(
        f"""
        CREATE INDEX ix_session_aggregates_aggregate_json_gin
        ON {SCHEMA}.session_aggregates
        USING gin (aggregate_json)
        """,
    )

    op.create_table(
        "final_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "profile_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column(
            "confidence_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("raw_output_text", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'ready', 'failed', 'reviewed')",
            name="ck_final_profiles_status",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_final_profiles_session_id_sessions",
        ),
        sa.ForeignKeyConstraint(
            ["prompt_version_id"],
            [f"{SCHEMA}.prompt_versions.id"],
            ondelete="RESTRICT",
            name="fk_final_profiles_prompt_version_id_prompt_versions",
        ),
        sa.UniqueConstraint("session_id", name="uq_final_profiles_session_id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_final_profiles_status",
        "final_profiles",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE INDEX ix_final_profiles_profile_json_gin
        ON {SCHEMA}.final_profiles
        USING gin (profile_json)
        """,
    )

    op.create_table(
        "expert_reviews",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("final_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("quality_score", sa.Integer(), nullable=True),
        sa.Column("notes_text", sa.Text(), nullable=True),
        sa.Column(
            "corrections_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'reviewed', 'approved', 'rejected')",
            name="ck_expert_reviews_status",
        ),
        sa.CheckConstraint(
            "quality_score IS NULL OR (quality_score BETWEEN 1 AND 5)",
            name="ck_expert_reviews_quality_score",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_expert_reviews_session_id_sessions",
        ),
        sa.ForeignKeyConstraint(
            ["final_profile_id"],
            [f"{SCHEMA}.final_profiles.id"],
            ondelete="CASCADE",
            name="fk_expert_reviews_final_profile_id_final_profiles",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_user_id"],
            [f"{SCHEMA}.users.id"],
            ondelete="RESTRICT",
            name="fk_expert_reviews_reviewer_user_id_users",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_expert_reviews_session_id",
        "expert_reviews",
        ["session_id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_expert_reviews_reviewer_user_id_status",
        "expert_reviews",
        ["reviewer_user_id", "status"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_expert_reviews_quality_score",
        "expert_reviews",
        ["quality_score"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "ai_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("job_type", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("100"),
        ),
        sa.Column(
            "attempt_no",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("3"),
        ),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column(
            "payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.CheckConstraint(
            "job_type IN ('answer_extract', 'session_aggregate', "
            "'final_profile')",
            name="ck_ai_jobs_job_type",
        ),
        sa.CheckConstraint(
            "entity_type IN ('answer', 'session', 'profile')",
            name="ck_ai_jobs_entity_type",
        ),
        sa.CheckConstraint(
            "status IN ("
            "'queued', "
            "'started', "
            "'retry', "
            "'succeeded', "
            "'failed', "
            "'dead'"
            ")",
            name="ck_ai_jobs_status",
        ),
        sa.CheckConstraint(
            "attempt_no >= 0",
            name="ck_ai_jobs_attempt_no",
        ),
        sa.CheckConstraint(
            "max_attempts > 0",
            name="ck_ai_jobs_max_attempts",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="CASCADE",
            name="fk_ai_jobs_session_id_sessions",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_ai_jobs_idempotency_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_jobs_status_scheduled_at",
        "ai_jobs",
        ["status", "scheduled_at"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_jobs_session_id",
        "ai_jobs",
        ["session_id"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=UUID_DEFAULT,
        ),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=JSONB_EMPTY,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=NOW,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            [f"{SCHEMA}.users.id"],
            ondelete="SET NULL",
            name="fk_audit_logs_actor_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.sessions.id"],
            ondelete="SET NULL",
            name="fk_audit_logs_session_id_sessions",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_audit_logs_entity_type_entity_id",
        "audit_logs",
        ["entity_type", "entity_id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_audit_logs_session_id",
        "audit_logs",
        ["session_id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("audit_logs", schema=SCHEMA)
    op.drop_table("ai_jobs", schema=SCHEMA)
    op.drop_table("expert_reviews", schema=SCHEMA)
    op.drop_table("final_profiles", schema=SCHEMA)
    op.drop_table("session_aggregates", schema=SCHEMA)
    op.drop_table("answer_extractions", schema=SCHEMA)
    op.drop_table("prompt_versions", schema=SCHEMA)
    op.drop_table("answers", schema=SCHEMA)
    op.drop_table("sessions", schema=SCHEMA)
    op.drop_table("questions", schema=SCHEMA)
    op.drop_table("taxonomy_versions", schema=SCHEMA)
    op.drop_table("users", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
