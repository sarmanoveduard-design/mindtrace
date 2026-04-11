from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

ScoreField = Field(ge=0.0, le=1.0)

Severity = Literal["low", "medium", "high"]

PatternCode = Literal[
    "reflective_orientation",
    "growth_orientation",
    "deliberative_decision_making",
    "external_validation_sensitivity",
]

TensionCode = Literal[
    "autonomy_vs_approval",
    "growth_vs_security",
    "reflection_vs_overthinking",
]

RiskFlagCode = Literal[
    "low_profile_confidence",
    "insufficient_values_coverage",
    "high_internal_tension",
    "profile_instability_risk",
]


class ReadinessMeta(BaseModel):
    is_complete: bool
    coverage_ratio: float = ScoreField
    minimum_coverage_reached: bool
    can_be_shown_to_user: bool
    can_be_reviewed_by_expert: bool


class ProfileDimensionItem(BaseModel):
    dimension_code: str
    label: str
    score: float = ScoreField
    confidence: float = ScoreField
    support_count: int
    based_on_signal_codes: list[str]


class ProfileSection(BaseModel):
    summary: str
    dimensions: list[ProfileDimensionItem]


class ThinkingTypeItem(BaseModel):
    type_code: str
    label: str
    state: Literal["present", "absent"]
    confidence: float = ScoreField
    based_on_signal_codes: list[str]


class PatternItem(BaseModel):
    code: PatternCode
    title: str
    description: str
    strength: Severity


class TensionItem(BaseModel):
    code: TensionCode
    description: str
    severity: Severity
    dimension_codes: list[str] | None = None


class FinalRiskFlagItem(BaseModel):
    code: RiskFlagCode
    severity: Severity
    description: str


class EvidenceBasisMeta(BaseModel):
    usable_answers: int
    aggregated_signals: int
    strong_dimensions: int
    contradiction_count: int


class UserView(BaseModel):
    title: str
    short_summary: str
    strengths: list[str]
    growth_edges: list[str]
    disclaimers: list[str]


class ExpertView(BaseModel):
    profile_summary: str
    supporting_signal_codes: list[str]
    notable_contradictions: list[str]
    unresolved_deficits: list[str]
    confidence_comment: str


class FinalProfileBuildResult(BaseModel):
    schema_version: Literal["final_profile_v1"]
    taxonomy_version_id: UUID
    session_id: UUID
    readiness: ReadinessMeta
    thinking_profile: ProfileSection
    thinking_types: list[ThinkingTypeItem] = Field(default_factory=list)
    values_profile: ProfileSection
    key_patterns: list[PatternItem]
    tensions: list[TensionItem]
    risk_flags: list[FinalRiskFlagItem]
    evidence_basis: EvidenceBasisMeta
    user_view: UserView
    expert_view: ExpertView
    overall_confidence: float = ScoreField
