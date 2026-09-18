from __future__ import annotations

from dataclasses import dataclass

from app.models.directives import DirectiveInterpretation
from app.models.request import OptimizeEnergyRequest


@dataclass
class OptimizationInputs:
    effective_solar: list[float]
    active_minimum: list[float]
    charge_upper: list[float]
    discharge_upper: list[float]
    grid_upper: list[float | None]


def apply_directives(req: OptimizeEnergyRequest, directives: list[DirectiveInterpretation]) -> OptimizationInputs:
    battery = req.battery
    solar_factor = [1.0] * 24
    active_minimum = [battery.minimum_energy_kwh] * 24
    charge_upper = [battery.max_charge_kwh_per_hour] * 24
    discharge_upper = [battery.max_discharge_kwh_per_hour] * 24
    grid_upper: list[float | None] = [None] * 24
    for directive in directives:
        if not directive.applies: continue
        adjustment = directive.structured_adjustment
        assert adjustment is not None
        for hour in adjustment.hours:
            if directive.directive_type == "solar_reduction": solar_factor[hour] = min(solar_factor[hour], adjustment.factor)  # type: ignore[attr-defined]
            elif directive.directive_type == "minimum_battery_reserve": active_minimum[hour] = max(active_minimum[hour], adjustment.minimum_energy_kwh)  # type: ignore[attr-defined]
            elif directive.directive_type == "no_charge_window": charge_upper[hour] = 0.0
            elif directive.directive_type == "no_discharge_window": discharge_upper[hour] = 0.0
            elif directive.directive_type == "max_grid_window":
                cap = adjustment.max_grid_kwh  # type: ignore[attr-defined]
                grid_upper[hour] = cap if grid_upper[hour] is None else min(grid_upper[hour], cap)
    effective_solar = [req.hours[hour].solar_kwh * solar_factor[hour] for hour in range(24)]
    return OptimizationInputs(effective_solar, active_minimum, charge_upper, discharge_upper, grid_upper)
