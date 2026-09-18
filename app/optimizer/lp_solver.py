from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from app.directives.apply import OptimizationInputs
from app.errors import OptimizationError
from app.models.request import OptimizeEnergyRequest

N = 24
TOTAL = 120
idx_grid = lambda h: h
idx_solar = lambda h: N + h
idx_charge = lambda h: 2 * N + h
idx_discharge = lambda h: 3 * N + h
idx_energy = lambda h: 4 * N + h


def solve_lp(req: OptimizeEnergyRequest, inputs: OptimizationInputs) -> np.ndarray:
    c = np.zeros(TOTAL)
    for hour in range(N): c[idx_grid(hour)] = req.hours[hour].tariff_bdt_per_kwh
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    for hour in range(N):
        balance = np.zeros(TOTAL)
        balance[idx_grid(hour)] = 1
        balance[idx_solar(hour)] = 1
        balance[idx_discharge(hour)] = 1
        balance[idx_charge(hour)] = -1
        rows.append(balance); rhs.append(req.hours[hour].demand_kwh)
        transition = np.zeros(TOTAL)
        transition[idx_energy(hour)] = 1
        transition[idx_charge(hour)] = -1
        transition[idx_discharge(hour)] = 1
        if hour == 0: transition_rhs = req.battery.initial_energy_kwh
        else: transition[idx_energy(hour - 1)] = -1; transition_rhs = 0.0
        rows.append(transition); rhs.append(transition_rhs)
    terminal = np.zeros(TOTAL); terminal[idx_energy(23)] = 1
    rows.append(terminal); rhs.append(req.battery.initial_energy_kwh)
    bounds = []
    for hour in range(N): bounds.append((0, inputs.grid_upper[hour]))
    for hour in range(N): bounds.append((0, inputs.effective_solar[hour]))
    for hour in range(N): bounds.append((0, inputs.charge_upper[hour]))
    for hour in range(N): bounds.append((0, inputs.discharge_upper[hour]))
    for hour in range(N): bounds.append((inputs.active_minimum[hour], req.battery.capacity_kwh))
    result = linprog(c, A_eq=np.asarray(rows), b_eq=np.asarray(rhs), bounds=bounds, method="highs")
    if not result.success or result.x is None:
        raise OptimizationError(f"LP solve failed: {result.message}")
    return result.x
