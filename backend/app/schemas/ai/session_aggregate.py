from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

CoverageRatio = Field(ge=0.0, le=1.0)
ScoreField = Field(ge=0.0, le=1.0)

Domain = Literal["thinking", "values"]
DeficitDomain = Literal["thinking", "values", "general"]
Severity = Literal["low", "medium", "high"]
ContradictionType = Literal["cross_answer", "cross_signal"]

DeficitCode = Literal[
    "low_reflection_coverage",
    "low_values_coverage",
    "insufficient_decision_signals",
    "insufficient_confidence",
    "too_many_unusable_answers",
]

RiskFlagCode = Literal[
    "low_session_coverage",
    "high_answer_noise",
    "cross_answer_inconsistency",
    "low_aggregate_confidence",
    "values_profile_unstable",
]


class CoverageMeta(BaseModel):
    answered_questions: int
    required_questions: int
    usable_answer_count: int
    coverage_ratio: float = CoverageRatio
    is_minimum_coverage_reached: bool


class AggregatedSignalItem(BaseModel):
    signal_code: str
    domain: Domain
    label: str
    score: float = ScoreField
    confidence: float = ScoreField
    support_count: int
    question_codes: list[str]
    evidence_summary: list[str]
    source_answer_ids: list[UUID]


class DeficitItem(BaseModel):
    code: DeficitCode
    domain: DeficitDomain
    description: str
    severity: Severity
    recommended_question_codes: list[str] | None = None


class AggregateContradictionItem(BaseModel):
    type: ContradictionType
    description: str
    severity: Severity
    signal_codes: list[str] | None = None
    question_codes: list[str] | None = None


class AggregateRiskFlagItem(BaseModel):
    code: RiskFlagCode
    severity: Severity
    description: str


class SessionAggregateResult(BaseModel):
    schema_version: Literal["session_aggregate_v1"]
    taxonomy_version_id: UUID
    session_id: UUID
    coverage: CoverageMeta
    signals: list[AggregatedSignalItem]
    deficits: list[DeficitItem]
    contradictions: list[AggregateContradictionItem]
    risk_flags: list[AggregateRiskFlagItem]
    aggregate_summary: str
    overall_confidence: float = ScoreField
