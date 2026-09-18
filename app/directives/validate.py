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
    SUPPORTED_DIRECTIVES,
)
from app.models.request import BatteryInput


EXPECTED_TYPES = {
    "solar_reduction": SolarReductionAdjustment,
    "minimum_battery_reserve": MinimumBatteryReserveAdjustment,
    "no_charge_window": NoChargeAdjustment,
    "no_discharge_window": NoDischargeAdjustment,
    "max_grid_window": MaxGridAdjustment,
}


def validate_directives(directives: list[DirectiveInterpretation], note_count: int, battery: BatteryInput) -> None:
    if len(directives) != note_count or [item.note_index for item in directives] != list(range(note_count)):
        raise DirectiveValidationError("exactly one ordered directive is required per note")
    for item in directives:
        if item.directive_type not in SUPPORTED_DIRECTIVES:
            raise DirectiveValidationError("unsupported directive type")
        if item.directive_type == "no_op":
            if item.applies or item.structured_adjustment is not None:
                raise DirectiveValidationError("no_op must not apply and must have null adjustment")
            continue
        if not item.applies or not isinstance(item.structured_adjustment, EXPECTED_TYPES[item.directive_type]):
            raise DirectiveValidationError("directive adjustment shape does not match its type")
        hours = item.structured_adjustment.hours
        if hours != sorted(set(hours)) or any(type(hour) is not int or not 0 <= hour <= 23 for hour in hours):
            raise DirectiveValidationError("directive hours must be unique ascending integers in 0..23")
        if isinstance(item.structured_adjustment, SolarReductionAdjustment):
            value = item.structured_adjustment.factor
            if not math.isfinite(value) or not 0 <= value <= 1: raise DirectiveValidationError("invalid solar factor")
        if isinstance(item.structured_adjustment, MinimumBatteryReserveAdjustment):
            value = item.structured_adjustment.minimum_energy_kwh
            if not math.isfinite(value) or not 0 <= value <= battery.capacity_kwh: raise DirectiveValidationError("invalid reserve")
        if isinstance(item.structured_adjustment, MaxGridAdjustment):
            value = item.structured_adjustment.max_grid_kwh
            if not math.isfinite(value) or value < 0: raise DirectiveValidationError("invalid grid cap")
