from __future__ import annotations

from typing import Any


def execute_ai_stage_mock(
    stage_code: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if stage_code == "answer_extract":
        return {
            "schema_version": "answer_extraction_v1",
            "taxonomy_version_id": payload["taxonomy_version_id"],
            "question_id": payload["question_id"],
            "question_code": payload["question"]["code"],
            "answer_id": payload["answer_id"],
            "analysis": {
                "is_usable": True,
                "adequacy": "high",
                "language_code": "ru",
                "answer_quality_flags": [],
            },
            "signals": [
                {
                    "signal_code": "reflection_depth",
                    "domain": "thinking",
                    "label": "high_reflection",
                    "score": 0.8,
                    "confidence": 0.82,
                    "evidence": [
                        {
                            "text": payload["answer_text"] or "answer",
                            "kind": "quote",
                        },
                    ],
                    "rationale": "Mock extraction result.",
                },
            ],
            "contradictions": [],
            "risk_flags": [],
            "summary": "Mock answer extraction result.",
            "overall_confidence": 0.8,
        }

    if stage_code == "session_aggregate":
        answer_extractions = payload["answer_extractions"]
        source_answer_ids = [
            item["answer_id"] for item in answer_extractions
        ]
        question_codes = [
            item["question_code"] for item in answer_extractions
        ]

        return {
            "schema_version": "session_aggregate_v1",
            "taxonomy_version_id": payload["taxonomy_version_id"],
            "session_id": payload["session_id"],
            "coverage": {
                "answered_questions": len(payload["answers"]),
                "required_questions": len(payload["answers"]),
                "usable_answer_count": len(answer_extractions),
                "coverage_ratio": 1.0 if payload["answers"] else 0.0,
                "is_minimum_coverage_reached": bool(payload["answers"]),
            },
            "signals": [
                {
                    "signal_code": "reflection_depth",
                    "domain": "thinking",
                    "label": "high_reflection",
                    "score": 0.8,
                    "confidence": 0.82,
                    "support_count": len(answer_extractions) or 1,
                    "question_codes": question_codes,
                    "evidence_summary": [
                        "Mock aggregated reflection signal",
                    ],
                    "source_answer_ids": source_answer_ids,
                },
            ],
            "deficits": [],
            "contradictions": [],
            "risk_flags": [],
            "aggregate_summary": "Mock session aggregate result.",
            "overall_confidence": 0.8,
        }

    if stage_code == "final_profile_build":
        return {
            "schema_version": "final_profile_v1",
            "taxonomy_version_id": payload["taxonomy_version_id"],
            "session_id": payload["session_id"],
            "readiness": {
                "is_complete": True,
                "coverage_ratio": 1.0,
                "minimum_coverage_reached": True,
                "can_be_shown_to_user": True,
                "can_be_reviewed_by_expert": True,
            },
            "thinking_profile": {
                "summary": "Mock thinking profile.",
                "dimensions": [
                    {
                        "dimension_code": "reflection_depth",
                        "label": "high",
                        "score": 0.8,
                        "confidence": 0.82,
                        "support_count": 1,
                        "based_on_signal_codes": [
                            "reflection_depth",
                        ],
                    },
                ],
            },
            "values_profile": {
                "summary": "Mock values profile.",
                "dimensions": [
                    {
                        "dimension_code": "security_vs_growth",
                        "label": "growth_leaning",
                        "score": 0.68,
                        "confidence": 0.72,
                        "support_count": 1,
                        "based_on_signal_codes": [
                            "security_vs_growth",
                        ],
                    },
                ],
            },
            "key_patterns": [
                {
                    "code": "reflective_orientation",
                    "title": "Выраженная рефлексивность",
                    "description": "Mock pattern.",
                    "strength": "high",
                },
            ],
            "tensions": [],
            "risk_flags": [],
            "evidence_basis": {
                "usable_answers": len(payload["answer_extract_trace"]),
                "aggregated_signals": 1,
                "strong_dimensions": 1,
                "contradiction_count": 0,
            },
            "user_view": {
                "title": "Ваш профиль MindTrace",
                "short_summary": "Mock final profile summary.",
                "strengths": [
                    "Mock strength",
                ],
                "growth_edges": [
                    "Mock growth edge",
                ],
                "disclaimers": [
                    "Mock disclaimer",
                ],
            },
            "expert_view": {
                "profile_summary": "Mock expert summary.",
                "supporting_signal_codes": [
                    "reflection_depth",
                ],
                "notable_contradictions": [],
                "unresolved_deficits": [],
                "confidence_comment": "Mock confidence comment.",
            },
            "overall_confidence": 0.8,
        }

    raise ValueError(f"Unsupported AI stage: {stage_code}")
