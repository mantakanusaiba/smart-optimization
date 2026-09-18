from __future__ import annotations

import json

import httpx

from app.config import Settings
from app.errors import InterpretationError
from app.llm.prompts import SYSTEM_PROMPT, user_prompt


async def request_semantic_json(
    note: str,
    capacity: float,
    minimum: float,
    settings: Settings,
    correction: str | None = None,
) -> dict:

    if not settings.llm_api_key:
        raise InterpretationError("LLM_API_KEY is not configured")

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "applies",
            "directive_type",
            "time_mode",
            "start_hour",
            "end_hour",
            "explicit_hours",
            "quantity_value",
            "quantity_kind",
            "explanation",
        ],
        "properties": {
            "applies": {
                "type": "boolean"
            },

            "directive_type": {
                "enum": [
                    "solar_reduction",
                    "minimum_battery_reserve",
                    "no_charge_window",
                    "no_discharge_window",
                    "max_grid_window",
                    "no_op",
                ]
            },

            "time_mode": {
                "enum": [
                    "window",
                    "explicit_hours",
                    "none",
                ]
            },

            "start_hour": {
                "type": [
                    "integer",
                    "null",
                ]
            },

            "end_hour": {
                "type": [
                    "integer",
                    "null",
                ]
            },

            "explicit_hours": {
                "type": [
                    "array",
                    "null",
                ],
                "items": {
                    "type": "integer"
                },
            },

            "quantity_value": {
                "type": [
                    "number",
                    "null",
                ]
            },

            "quantity_kind": {
                "enum": [
                    "remaining_fraction",
                    "remaining_percent",
                    "reduction_fraction",
                    "reduction_percent",
                    "absolute_kwh",
                    "battery_capacity_fraction",
                    "battery_capacity_percent",
                    "none",
                ]
            },

            "explanation": {
                "type": "string"
            },
        },
    }

    payload = {
        "model": settings.llm_model,

        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt(
                    note,
                    capacity,
                    minimum,
                    correction,
                ),
            },
        ],

        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_directive",
                "strict": True,
                "schema": schema,
            },
        },
    }

    try:

        async with httpx.AsyncClient(
            timeout=settings.llm_timeout_seconds
        ) as client:

            response = await client.post(
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",

                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },

                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            content = data["choices"][0]["message"]["content"]

            return json.loads(content)

    except (
        httpx.HTTPError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:

        raise InterpretationError(
            "language model request failed"
        ) from exc