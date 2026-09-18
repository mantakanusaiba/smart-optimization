import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def samples():
    return json.loads((Path(__file__).parents[1] / "public" / "public_sample_cases.json").read_text(encoding="utf-8"))["cases"]
