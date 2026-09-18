from __future__ import annotations

import asyncio

from pydantic import ValidationError

from app.config import get_settings
from app.directives.normalize import normalize_directive
from app.errors import GridWiseError, InterpretationError
from app.llm.client import request_semantic_json
from app.llm.deterministic import interpret_deterministically
from app.models.llm_semantics import SemanticDirective
from app.models.request import BatteryInput


async def interpret_note(note: str, battery: BatteryInput) -> SemanticDirective:
    settings = get_settings()
    if settings.llm_provider == "deterministic":
        return interpret_deterministically(note)
    correction = None
    for attempt in range(2):
        try:
            data = await request_semantic_json(note, battery.capacity_kwh, battery.minimum_energy_kwh, settings, correction)
            semantic = SemanticDirective.model_validate(data)
            normalize_directive(semantic, 0, battery)
            return semantic
        except (ValidationError, GridWiseError) as exc:
            if attempt == 0:
                correction = str(exc)[:500]
                continue
            raise InterpretationError("model output failed deterministic validation") from exc
    raise InterpretationError("operator note interpretation failed")


async def interpret_all_notes(notes: list[str], battery: BatteryInput) -> list[SemanticDirective]:
    return list(await asyncio.gather(*(interpret_note(note, battery) for note in notes)))
