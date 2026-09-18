from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HourInput(StrictModel):
    hour: int = Field(ge=0, le=23)
    demand_kwh: float = Field(ge=0)
    solar_kwh: float = Field(ge=0)
    tariff_bdt_per_kwh: float = Field(ge=0)

    @field_validator("demand_kwh", "solar_kwh", "tariff_bdt_per_kwh")
    @classmethod
    def finite_numbers(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        return value


class BatteryInput(StrictModel):
    capacity_kwh: float = Field(ge=0)
    initial_energy_kwh: float = Field(ge=0)
    minimum_energy_kwh: float = Field(ge=0)
    max_charge_kwh_per_hour: float = Field(ge=0)
    max_discharge_kwh_per_hour: float = Field(ge=0)

    @field_validator("*")
    @classmethod
    def finite_numbers(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        return value

    @model_validator(mode="after")
    def consistent_energy(self) -> "BatteryInput":
        if self.initial_energy_kwh > self.capacity_kwh:
            raise ValueError("initial energy cannot exceed capacity")
        if self.minimum_energy_kwh > self.capacity_kwh:
            raise ValueError("minimum energy cannot exceed capacity")
        return self


class OptimizeEnergyRequest(StrictModel):
    scenario_id: str = Field(min_length=1, max_length=200)
    operator_notes: list[str] = Field(min_length=1, max_length=3)
    hours: list[HourInput] = Field(min_length=24, max_length=24)
    battery: BatteryInput

    @field_validator("scenario_id")
    @classmethod
    def nonblank_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("scenario_id cannot be blank")
        return value

    @field_validator("operator_notes")
    @classmethod
    def nonblank_notes(cls, notes: list[str]) -> list[str]:
        if any(not note.strip() for note in notes):
            raise ValueError("operator notes cannot be blank")
        return notes

    @model_validator(mode="after")
    def complete_day(self) -> "OptimizeEnergyRequest":
        found = [row.hour for row in self.hours]
        if len(set(found)) != 24 or set(found) != set(range(24)):
            raise ValueError("hours must contain each integer from 0 through 23 exactly once")
        self.hours.sort(key=lambda row: row.hour)
        return self
