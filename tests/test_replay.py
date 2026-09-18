import copy

import pytest

from app.errors import ReplayValidationError
from app.models.request import OptimizeEnergyRequest
from app.models.response import HourlyPlanRow
from app.services.optimize_service import optimize_service
from app.validation.replay import validate_plan_by_replay


@pytest.mark.asyncio
async def test_replay_rejects_corruption(samples, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    request = OptimizeEnergyRequest.model_validate(samples[1]["input"])
    response = await optimize_service(request)
    plan = [row.model_copy(deep=True) for row in response.hourly_plan]
    plan[0].grid_kwh += 1
    with pytest.raises(ReplayValidationError): validate_plan_by_replay(request, response.directive_interpretation, plan)
