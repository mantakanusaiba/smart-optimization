import copy

import pytest
from pydantic import ValidationError

from app.models.request import OptimizeEnergyRequest


def test_valid_request_is_sorted(samples):
    payload = copy.deepcopy(samples[0]["input"])
    payload["hours"].reverse()
    request = OptimizeEnergyRequest.model_validate(payload)
    assert [row.hour for row in request.hours] == list(range(24))


@pytest.mark.parametrize("mutation", ["short_hours", "duplicate_hour", "empty_notes", "too_many_notes", "bad_battery"])
def test_invalid_requests(samples, mutation):
    payload = copy.deepcopy(samples[0]["input"])
    if mutation == "short_hours": payload["hours"].pop()
    elif mutation == "duplicate_hour": payload["hours"][0]["hour"] = 1
    elif mutation == "empty_notes": payload["operator_notes"] = []
    elif mutation == "too_many_notes": payload["operator_notes"] = ["x"] * 4
    else: payload["battery"]["initial_energy_kwh"] = payload["battery"]["capacity_kwh"] + 1
    with pytest.raises(ValidationError): OptimizeEnergyRequest.model_validate(payload)
