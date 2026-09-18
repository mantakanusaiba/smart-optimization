from __future__ import annotations

from app.directives.apply import apply_directives
from app.errors import ReplayValidationError
from app.models.directives import DirectiveInterpretation
from app.models.request import OptimizeEnergyRequest
from app.models.response import HourlyPlanRow

TOL = 0.011


def fail(message: str) -> None:
    raise ReplayValidationError(message)


def validate_plan_by_replay(req: OptimizeEnergyRequest, directives: list[DirectiveInterpretation], plan: list[HourlyPlanRow]) -> None:
    if len(plan) != 24 or [row.hour for row in plan] != list(range(24)): fail("plan must contain ordered hours 0..23")
    inputs = apply_directives(req, directives)
    energy = req.battery.initial_energy_kwh
    for hour, row in enumerate(plan):
        if row.grid_kwh < -TOL or row.solar_used_kwh < -TOL or row.battery_kwh < -TOL: fail("negative energy quantity")
        if row.solar_used_kwh > inputs.effective_solar[hour] + TOL: fail("solar cap exceeded")
        charge = row.battery_kwh if row.battery_action == "charge" else 0.0
        discharge = row.battery_kwh if row.battery_action == "discharge" else 0.0
        if row.battery_action == "idle" and abs(row.battery_kwh) > TOL: fail("idle battery amount must be zero")
        if charge > inputs.charge_upper[hour] + TOL or discharge > inputs.discharge_upper[hour] + TOL: fail("battery rate constraint exceeded")
        if inputs.grid_upper[hour] is not None and row.grid_kwh > inputs.grid_upper[hour] + TOL: fail("grid cap exceeded")
        lhs = row.grid_kwh + row.solar_used_kwh + discharge
        rhs = req.hours[hour].demand_kwh + charge
        if abs(lhs - rhs) > TOL: fail("hourly energy balance failed")
        energy += charge - discharge
        if energy < inputs.active_minimum[hour] - TOL or energy > req.battery.capacity_kwh + TOL: fail("battery bound exceeded")
        if abs(row.battery_energy_after_kwh - energy) > TOL: fail("returned battery state does not match replay")
    if abs(energy - req.battery.initial_energy_kwh) > TOL: fail("end-of-day neutrality failed")
