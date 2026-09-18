from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .llm_semantics import DirectiveType


class Adjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SolarReductionAdjustment(Adjustment):
    hours: list[int]
    factor: float


class MinimumBatteryReserveAdjustment(Adjustment):
    hours: list[int]
    minimum_energy_kwh: float


class NoChargeAdjustment(Adjustment):
    hours: list[int]


class NoDischargeAdjustment(Adjustment):
    hours: list[int]


class MaxGridAdjustment(Adjustment):
    hours: list[int]
    max_grid_kwh: float


StructuredAdjustment = (
    SolarReductionAdjustment
    | MinimumBatteryReserveAdjustment
    | NoChargeAdjustment
    | NoDischargeAdjustment
    | MaxGridAdjustment
    | None
)


class DirectiveInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note_index: int
    applies: bool
    directive_type: DirectiveType
    structured_adjustment: StructuredAdjustment
    explanation: str


SUPPORTED_DIRECTIVES: set[str] = {
    "solar_reduction", "minimum_battery_reserve", "no_charge_window",
    "no_discharge_window", "max_grid_window", "no_op",
}
