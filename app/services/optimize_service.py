from __future__ import annotations

from app.directives.apply import apply_directives
from app.directives.normalize import normalize_all_directives
from app.directives.validate import validate_directives
from app.llm.interpreter import interpret_all_notes
from app.models.request import OptimizeEnergyRequest
from app.models.response import OptimizeEnergyResponse
from app.optimizer.build_plan import build_hourly_plan
from app.optimizer.lp_solver import solve_lp
from app.validation.replay import validate_plan_by_replay


def compute_totals(req: OptimizeEnergyRequest, plan):
    total_grid = round(sum(row.grid_kwh for row in plan), 6)
    total_cost = round(sum(row.grid_kwh * req.hours[row.hour].tariff_bdt_per_kwh for row in plan), 6)
    peak = round(max(row.grid_kwh for row in plan), 6)
    return total_grid, total_cost, peak


async def optimize_service(req: OptimizeEnergyRequest) -> OptimizeEnergyResponse:
    semantics = await interpret_all_notes(req.operator_notes, req.battery)
    directives = normalize_all_directives(semantics, req.battery)
    validate_directives(directives, len(req.operator_notes), req.battery)
    inputs = apply_directives(req, directives)
    solution = solve_lp(req, inputs)
    plan = build_hourly_plan(solution)
    validate_plan_by_replay(req, directives, plan)
    total_grid, total_cost, peak = compute_totals(req, plan)
    summary = "Applied all operator directives, optimized the 24-hour energy schedule, respected operational limits, and restored the battery to its initial energy by the end of the day."
    return OptimizeEnergyResponse(scenario_id=req.scenario_id, directive_interpretation=directives, hourly_plan=plan, total_grid_kwh=total_grid, total_cost_bdt=total_cost, peak_grid_kwh=peak, plan_summary=summary)
