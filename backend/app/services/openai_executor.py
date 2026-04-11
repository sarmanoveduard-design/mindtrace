from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai_contracts import AIStageCode
from app.services.ai_contracts import get_ai_result_model


class OpenAIExecutor:
    def __init__(self) -> None:
        client_kwargs: dict[str, Any] = {
            "api_key": settings.openai_api_key,
        }
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url

        self.client = OpenAI(**client_kwargs)

    def execute_structured_stage(
        self,
        *,
        stage_code: AIStageCode,
        system_prompt: str,
        input_payload: dict[str, Any],
        model_name: str | None = None,
    ) -> dict[str, Any]:
        model_class = get_ai_result_model(stage_code)

        if stage_code == "answer_extract":
            question = input_payload.get("question", {})
            user_content = (
                "Analyze exactly one user answer.\n\n"
                f"QUESTION_CODE: {question.get('code')}\n"
                f"QUESTION_TITLE: {question.get('title')}\n"
                f"QUESTION_DESCRIPTION: {question.get('description')}\n\n"
                "ANSWER_TEXT:\n"
                f"{input_payload.get('answer_text')}\n\n"
                "FULL_INPUT_JSON:\n"
                f"{json.dumps(input_payload, ensure_ascii=False, indent=2)}"
            )
        else:
            user_content = (
                "Return a structured JSON result that matches the "
                "required schema exactly.\n\n"
                "INPUT_PAYLOAD_JSON:\n"
                f"{json.dumps(input_payload, ensure_ascii=False, indent=2)}"
            )

        response = self.client.responses.parse(
            model=model_name or settings.openai_default_model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            text_format=model_class,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI returned no parsed structured output.")

        if not isinstance(parsed, BaseModel):
            raise TypeError("Parsed OpenAI result is not a Pydantic model.")

        return parsed.model_dump(mode="json")
