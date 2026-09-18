"""Offline development interpreter. Production must use a configured language model."""
from __future__ import annotations

import re

from app.errors import InterpretationError
from app.models.llm_semantics import SemanticDirective


def _clock(value: str, meridiem: str | None) -> int:
    value = value.lower().strip()
    if value == "noon": return 12
    hour = int(value)
    if meridiem:
        meridiem = meridiem.lower()
        if meridiem == "pm" and hour != 12: hour += 12
        if meridiem == "am" and hour == 12: hour = 0
    return hour


def _window(note: str) -> tuple[int, int]:
    pattern = r"(?:from\s+)?(noon|\d{1,2})(?:\s*(am|pm))?\s*(?:until|to|and)\s*(noon|\d{1,2})(?:\s*(am|pm))?"
    match = re.search(pattern, note, re.I)
    if not match: raise InterpretationError("development interpreter could not parse time window")
    start_meridiem = match.group(2) or match.group(4)
    return _clock(match.group(1), start_meridiem), _clock(match.group(3), match.group(4))


def interpret_deterministically(note: str) -> SemanticDirective:
    lower = note.lower()
    irrelevant = ("next week", "next month", "tomorrow", "booking", "registration", "book-return", "club notices")
    if any(term in lower for term in irrelevant):
        return SemanticDirective(applies=False, directive_type="no_op", time_mode="none", quantity_kind="none", explanation="This note does not affect today's 24-hour energy schedule.")
    start, end = _window(lower)
    base = dict(applies=True, time_mode="window", start_hour=start, end_hour=end, explicit_hours=None)
    if "solar" in lower:
        percent = re.search(r"(\d+(?:\.\d+)?)\s*%", lower)
        if "half" in lower: value, kind = .5, "remaining_fraction"
        elif percent: value, kind = float(percent.group(1)), "reduction_percent" if "reduction" in lower else "remaining_percent"
        else: raise InterpretationError("development interpreter could not parse solar quantity")
        return SemanticDirective(**base, directive_type="solar_reduction", quantity_value=value, quantity_kind=kind, explanation="Solar availability is adjusted during the specified interval.")
    if ("not discharge" in lower or "do not discharge" in lower or "discharging is disabled" in lower):
        return SemanticDirective(**base, directive_type="no_discharge_window", quantity_value=None, quantity_kind="none", explanation="Battery discharge is prohibited during the specified interval.")
    if ("charger" in lower or "charging" in lower) and any(term in lower for term in ("isolated", "unavailable", "disabled")):
        return SemanticDirective(**base, directive_type="no_charge_window", quantity_value=None, quantity_kind="none", explanation="Battery charging is unavailable during the specified interval.")
    if "battery" in lower and any(term in lower for term in ("at least", "remain", "stored")):
        percent = re.search(r"(\d+(?:\.\d+)?)\s*%", lower)
        amount = re.search(r"(\d+(?:\.\d+)?)\s*kwh", lower)
        if percent: value, kind = float(percent.group(1)), "battery_capacity_percent"
        elif amount: value, kind = float(amount.group(1)), "absolute_kwh"
        else: raise InterpretationError("development interpreter could not parse reserve quantity")
        return SemanticDirective(**base, directive_type="minimum_battery_reserve", quantity_value=value, quantity_kind=kind, explanation="A minimum battery reserve is required during the specified interval.")
    if "grid" in lower or "transformer" in lower:
        amount = re.search(r"(\d+(?:\.\d+)?)\s*kwh", lower)
        if not amount: raise InterpretationError("development interpreter could not parse grid cap")
        return SemanticDirective(**base, directive_type="max_grid_window", quantity_value=float(amount.group(1)), quantity_kind="absolute_kwh", explanation="Grid import is capped during the specified interval.")
    return SemanticDirective(applies=False, directive_type="no_op", time_mode="none", quantity_kind="none", explanation="This note does not affect today's 24-hour energy schedule.")
