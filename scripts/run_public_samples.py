from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all official GridWise public samples through the HTTP API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    cases = json.loads((Path(__file__).parents[1] / "public" / "public_sample_cases.json").read_text(encoding="utf-8"))["cases"]
    passed = 0
    with httpx.Client(base_url=args.base_url, timeout=30) as client:
        for case in cases:
            print(case["id"])
            try:
                response = client.post("/optimize-energy", json=case["input"])
                response.raise_for_status()
                actual, expected = response.json(), case["expected_output"]
                semantics = all(
                    {k: got[k] for k in ("note_index", "applies", "directive_type", "structured_adjustment")}
                    == {k: wanted[k] for k in ("note_index", "applies", "directive_type", "structured_adjustment")}
                    for got, wanted in zip(actual["directive_interpretation"], expected["directive_interpretation"], strict=True)
                )
                plan = actual["hourly_plan"]
                totals = abs(sum(row["grid_kwh"] for row in plan) - actual["total_grid_kwh"]) <= .01
                cost = abs(actual["total_cost_bdt"] - expected["total_cost_bdt"]) <= .01
                replay_shape = len(plan) == 24 and [row["hour"] for row in plan] == list(range(24))
                print(f"  interpretation: {'PASS' if semantics else 'FAIL'}")
                print(f"  replay shape:   {'PASS' if replay_shape else 'FAIL'}")
                print(f"  totals:         {'PASS' if totals else 'FAIL'}")
                print(f"  cost:           {'PASS' if cost else 'FAIL'}")
                if semantics and replay_shape and totals and cost: passed += 1
            except Exception as exc:
                print(f"  ERROR: {type(exc).__name__}")
    print(f"\n{passed}/{len(cases)} public cases passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
