from __future__ import annotations

import math

from app.errors import DirectiveValidationError
from app.models.directives import (
    DirectiveInterpretation,
    MaxGridAdjustment,
    MinimumBatteryReserveAdjustment,
    NoChargeAdjustment,
    NoDischargeAdjustment,
    SolarReductionAdjustment,
)
from app.models.llm_semantics import SemanticDirective
from app.models.request import BatteryInput


def normalize_window(start_hour: int, end_hour: int) -> list[int]:
    if not isinstance(start_hour, int) or not isinstance(end_hour, int):
        raise DirectiveValidationError("window bounds must be integers")
    if not 0 <= start_hour <= 23 or not 1 <= end_hour <= 24 or start_hour >= end_hour:
        raise DirectiveValidationError("invalid whole-hour window")
    return list(range(start_hour, end_hour))


def normalize_hours(semantic: SemanticDirective) -> list[int]:
    if semantic.time_mode == "window":
        if semantic.start_hour is None or semantic.end_hour is None:
            raise DirectiveValidationError("window requires start and end")
        return normalize_window(semantic.start_hour, semantic.end_hour)
    if semantic.time_mode == "explicit_hours":
        if semantic.explicit_hours is None:
            raise DirectiveValidationError("explicit hours are required")
        if any(type(hour) is not int or not 0 <= hour <= 23 for hour in semantic.explicit_hours):
            raise DirectiveValidationError("hours must be integers in 0..23")
        hours = sorted(set(semantic.explicit_hours))
        if not hours:
            raise DirectiveValidationError("affected hours cannot be empty")
        return hours
    raise DirectiveValidationError("a time window is required for this directive")


def normalize_solar_factor(value: float, kind: str) -> float:
    if kind == "remaining_fraction": factor = value
    elif kind == "remaining_percent": factor = value / 100.0
    elif kind == "reduction_fraction": factor = 1.0 - value
    elif kind == "reduction_percent": factor = 1.0 - value / 100.0
    else: raise DirectiveValidationError("invalid solar quantity kind")
    if not math.isfinite(factor) or not 0 <= factor <= 1:
        raise DirectiveValidationError("solar factor must be finite and in 0..1")
    return round(factor, 12)


def normalize_reserve(value: float, kind: str, capacity_kwh: float) -> float:
    if kind == "absolute_kwh": reserve = value
    elif kind == "battery_capacity_fraction": reserve = capacity_kwh * value
    elif kind == "battery_capacity_percent": reserve = capacity_kwh * value / 100.0
    else: raise DirectiveValidationError("invalid reserve quantity kind")
    if not math.isfinite(reserve) or reserve < 0 or reserve > capacity_kwh:
        raise DirectiveValidationError("reserve must be finite and within battery capacity")
    return reserve


def normalize_directive(semantic: SemanticDirective, note_index: int, battery: BatteryInput) -> DirectiveInterpretation:
    if semantic.directive_type == "no_op":
        return DirectiveInterpretation(note_index=note_index, applies=False, directive_type="no_op", structured_adjustment=None, explanation=semantic.explanation)
    if not semantic.applies:
        raise DirectiveValidationError("non-no-op directive must apply")
    hours = normalize_hours(semantic)
    value = semantic.quantity_value
    if semantic.directive_type == "solar_reduction":
        if value is None: raise DirectiveValidationError("solar reduction requires a quantity")
        adjustment = SolarReductionAdjustment(hours=hours, factor=normalize_solar_factor(value, semantic.quantity_kind))
    elif semantic.directive_type == "minimum_battery_reserve":
        if value is None: raise DirectiveValidationError("reserve requires a quantity")
        adjustment = MinimumBatteryReserveAdjustment(hours=hours, minimum_energy_kwh=normalize_reserve(value, semantic.quantity_kind, battery.capacity_kwh))
    elif semantic.directive_type == "no_charge_window": adjustment = NoChargeAdjustment(hours=hours)
    elif semantic.directive_type == "no_discharge_window": adjustment = NoDischargeAdjustment(hours=hours)
    elif semantic.directive_type == "max_grid_window":
        if value is None or semantic.quantity_kind != "absolute_kwh" or not math.isfinite(value) or value < 0:
            raise DirectiveValidationError("grid cap requires a non-negative absolute kWh value")
        adjustment = MaxGridAdjustment(hours=hours, max_grid_kwh=value)
    else: raise DirectiveValidationError("unsupported directive")
    return DirectiveInterpretation(note_index=note_index, applies=True, directive_type=semantic.directive_type, structured_adjustment=adjustment, explanation=semantic.explanation)


def normalize_all_directives(semantics: list[SemanticDirective], battery: BatteryInput) -> list[DirectiveInterpretation]:
    return [normalize_directive(item, index, battery) for index, item in enumerate(semantics)]
