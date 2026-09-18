import os

import pytest

from app.models.request import OptimizeEnergyRequest
from app.services.optimize_service import optimize_service


@pytest.mark.asyncio
async def test_all_public_samples(samples, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    for case in samples:
        request = OptimizeEnergyRequest.model_validate(case["input"])
        response = await optimize_service(request)
        expected = case["expected_output"]
        got_directives = [item.model_dump() for item in response.directive_interpretation]
        expected_directives = expected["directive_interpretation"]
        for got, wanted in zip(got_directives, expected_directives, strict=True):
            assert got["note_index"] == wanted["note_index"]
            assert got["applies"] == wanted["applies"]
            assert got["directive_type"] == wanted["directive_type"]
            assert got["structured_adjustment"] == wanted["structured_adjustment"]
        assert response.total_cost_bdt == pytest.approx(expected["total_cost_bdt"], abs=.02)
