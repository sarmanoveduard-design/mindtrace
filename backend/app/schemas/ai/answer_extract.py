from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

Adequacy = Literal["low", "medium", "high"]
Domain = Literal["thinking", "values"]
EvidenceKind = Literal["quote", "paraphrase"]
ContradictionType = Literal["internal"]
Severity = Literal["low", "medium", "high"]

AnswerQualityFlag = Literal[
    "too_short",
    "generic",
    "off_topic",
    "unclear",
    "contradictory_inside_answer",
    "emotionally_charged",
    "socially_desirable",
    "template_like",
]

RiskFlagCode = Literal[
    "insufficient_data",
    "generic_response",
    "off_topic_response",
    "social_desirability_risk",
    "high_emotional_distortion",
    "internal_contradiction_risk",
]


class EvidenceItem(BaseModel):
    text: str
    kind: EvidenceKind


class SignalItem(BaseModel):
    signal_code: str
    domain: Domain
    label: str
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[EvidenceItem]
    rationale: str


class ContradictionItem(BaseModel):
    type: ContradictionType
    description: str
    severity: Severity
    signal_codes: list[str] | None = None


class RiskFlagItem(BaseModel):
    code: RiskFlagCode
    severity: Severity
    description: str


class AnalysisMeta(BaseModel):
    is_usable: bool
    adequacy: Adequacy
    language_code: str | None
    answer_quality_flags: list[AnswerQualityFlag]


class AnswerExtractResult(BaseModel):
    schema_version: Literal["answer_extraction_v1"]
    taxonomy_version_id: UUID
    question_id: UUID
    question_code: str
    answer_id: UUID
    analysis: AnalysisMeta
    signals: list[SignalItem]
    contradictions: list[ContradictionItem]
    risk_flags: list[RiskFlagItem]
    summary: str
    overall_confidence: float = Field(ge=0.0, le=1.0)
