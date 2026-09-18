from __future__ import annotations

import numpy as np

from app.models.response import HourlyPlanRow
from app.optimizer.lp_solver import idx_charge, idx_discharge, idx_energy, idx_grid, idx_solar


def clean(value: float, tolerance: float = 1e-7) -> float:
    value = 0.0 if abs(value) < tolerance else float(value)
    return round(value, 6)


def build_hourly_plan(solution: np.ndarray) -> list[HourlyPlanRow]:
    plan: list[HourlyPlanRow] = []
    for hour in range(24):
        charge, discharge = clean(solution[idx_charge(hour)]), clean(solution[idx_discharge(hour)])
        if charge > 1e-6 and discharge > 1e-6:
            net = charge - discharge
            charge, discharge = (clean(net), 0.0) if net >= 0 else (0.0, clean(-net))
        action = "charge" if charge > 1e-6 else "discharge" if discharge > 1e-6 else "idle"
        amount = charge if action == "charge" else discharge if action == "discharge" else 0.0
        plan.append(HourlyPlanRow(hour=hour, grid_kwh=clean(solution[idx_grid(hour)]), solar_used_kwh=clean(solution[idx_solar(hour)]), battery_action=action, battery_kwh=amount, battery_energy_after_kwh=clean(solution[idx_energy(hour)])))
    return plan
