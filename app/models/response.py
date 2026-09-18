from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .directives import DirectiveInterpretation


class HourlyPlanRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hour: int
    grid_kwh: float
    solar_used_kwh: float
    battery_action: Literal["charge", "discharge", "idle"]
    battery_kwh: float
    battery_energy_after_kwh: float


class OptimizeEnergyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    directive_interpretation: list[DirectiveInterpretation]
    hourly_plan: list[HourlyPlanRow]
    total_grid_kwh: float
    total_cost_bdt: float
    peak_grid_kwh: float
    plan_summary: str
