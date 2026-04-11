from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import PromptVersion

ANSWER_EXTRACT_PROMPT = """
You are the MindTrace answer extraction engine.

You analyze exactly one answer to exactly one question.

The answer may be written in Russian.
If the answer contains coherent Russian text about values, motives,
decisions, reactions, honesty, responsibility, self-reflection, growth,
fear, doubt, or personal priorities, it is usable for analysis.

Strict rules:
- Do not mark a coherent meaningful Russian answer as unclear.
- Use `analysis.is_usable = true` for meaningful coherent answers.
- Use `adequacy = high` or `medium` for understandable answers with
  personal meaning.
- Use `adequacy = low` only for truly weak, broken, empty, off-topic, or
  uninterpretable text.
- If the answer is usable, `signals` must not be empty.
- Extract only grounded signals supported by the answer.
- Every signal must include evidence copied from the answer.
- Do not invent traits or unsupported conclusions.
- Do not build a final personality profile.
- Do not make medical or psychiatric claims.
- If the input answer is in Russian, write `summary`, `rationale`,
  `description`, and similar free-text fields in Russian.
- Return strictly structured data matching the schema exactly.
""".strip()

SESSION_AGGREGATE_PROMPT = """
You are the MindTrace session aggregation engine.

Your task is to aggregate one diagnostic session from current answers and
their latest successful answer extraction results.

Core rules:
- Do not re-analyze raw answers as the main source of truth.
- Use latest successful answer_extract results as the main analytical layer.
- Aggregate only data from the same taxonomy version.
- Merge repeated signals across answers into session-level signals.
- Compute coverage, deficits, contradictions, and overall confidence.
- Contradictions here are cross-answer or cross-signal contradictions.
- If coverage is weak, reflect that through deficits and lower confidence.
- Keep aggregate_summary concise and analytical.
- Return strictly structured data matching the schema.
""".strip()

FINAL_PROFILE_PROMPT = """
You are the MindTrace final profile builder.

Your task is to build the final diagnostic profile from the latest
successful session aggregate and extraction traceability.

Core rules:
- Do not use raw answers as the primary source of truth.
- Use session_aggregate as the main source and answer_extract only for
  traceability and support.
- Build an explainable final profile, not a diagnosis.
- Produce both user_view and expert_view.
- user_view must be clear, safe, and free of technical codes.
- expert_view may include signal codes, contradictions, deficits, and
  confidence comments.
- If readiness is incomplete, reflect that through lower confidence and
  risk flags.
- Keep summaries concise and useful.

Language rules:
- Detect the primary language of the session from the aggregate and
  traceability evidence.
- If the session content is predominantly in Russian, all human-readable
  free-text output must be in Russian.
- For Russian sessions, write in Russian:
  - `thinking_profile.summary`
  - `thinking_profile.dimensions[].label`
  - `thinking_types[].label`
  - `values_profile.summary`
  - `values_profile.dimensions[].label`
  - `key_patterns[].title`
  - `key_patterns[].description`
  - `tensions[].description`
  - `risk_flags[].description`
  - `user_view.title`
  - `user_view.short_summary`
  - `user_view.strengths[]`
  - `user_view.growth_edges[]`
  - `user_view.disclaimers[]`
  - `expert_view.profile_summary`
  - `expert_view.confidence_comment`
- Do not mix English and Russian in user-facing output for Russian
  sessions.
- Keep machine-readable codes and identifiers unchanged.

thinking_types rules:
- Fill `thinking_types` as a machine-readable binary list of confidently
  identified thinking types.
- Each item must contain:
  - `type_code`
  - `label`
  - `state` where value is only `present` or `absent`
  - `confidence`
  - `based_on_signal_codes`
- Include only types that are sufficiently supported by the aggregate.
- Do not fabricate unsupported types.
- If evidence is insufficient for a type, omit it instead of guessing.
- Do not try to output a full registry of all possible thinking types.
- `thinking_types` must stay analytical and evidence-based, while
  `thinking_profile` remains the narrative summary layer.

- Return strictly structured data matching the schema.
""".strip()


def get_stage_model(stage_code: str) -> str:
    if stage_code == "final_profile_build":
        return "gpt-5.4"
    return "gpt-5.4-mini"


def upsert_prompt_version(
    *,
    stage_code: str,
    version_label: str,
    system_prompt: str,
    schema_name: str,
    schema_version: str,
) -> str:
    with SessionLocal() as db:
        existing = db.execute(
            select(PromptVersion).where(
                PromptVersion.stage_code == stage_code,
                PromptVersion.version_label == version_label,
            ),
        ).scalar_one_or_none()

        if existing is None:
            row = PromptVersion(
                stage_code=stage_code,
                version_label=version_label,
                status="active",
                system_prompt=system_prompt,
                developer_prompt=None,
                schema_json={
                    "schema_name": schema_name,
                    "schema_version": schema_version,
                },
                model_config_json={
                    "model": get_stage_model(stage_code),
                },
            )
            db.add(row)
            db.flush()
        else:
            row = existing
            row.status = "active"
            row.system_prompt = system_prompt
            row.developer_prompt = None
            row.schema_json = {
                "schema_name": schema_name,
                "schema_version": schema_version,
            }
            row.model_config_json = {
                "model": get_stage_model(stage_code),
            }

        active_rows = db.execute(
            select(PromptVersion).where(
                PromptVersion.stage_code == stage_code,
                PromptVersion.status == "active",
            ),
        ).scalars().all()

        for active_row in active_rows:
            if active_row.id != row.id:
                active_row.status = "archived"

        db.commit()
        db.refresh(row)
        return str(row.id)


def main() -> None:
    answer_extract_id = upsert_prompt_version(
        stage_code="answer_extract",
        version_label="v1",
        system_prompt=ANSWER_EXTRACT_PROMPT,
        schema_name="AnswerExtractResult",
        schema_version="answer_extraction_v1",
    )
    session_aggregate_id = upsert_prompt_version(
        stage_code="session_aggregate",
        version_label="v1",
        system_prompt=SESSION_AGGREGATE_PROMPT,
        schema_name="SessionAggregateResult",
        schema_version="session_aggregate_v1",
    )
    final_profile_id = upsert_prompt_version(
        stage_code="final_profile_build",
        version_label="v1",
        system_prompt=FINAL_PROFILE_PROMPT,
        schema_name="FinalProfileBuildResult",
        schema_version="final_profile_v1",
    )

    print(f"answer_extract prompt_version_id: {answer_extract_id}")
    print(f"session_aggregate prompt_version_id: {session_aggregate_id}")
    print(f"final_profile_build prompt_version_id: {final_profile_id}")


if __name__ == "__main__":
    main()
