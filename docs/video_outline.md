# GridWise three-minute video outline

## 0:00–0:30 — Problem and objective

- Show the control-center overview and one operator note.
- Explain that GridWise converts natural-language operating intent into a safe, minimum-cost 24-hour campus schedule.

## 0:30–1:20 — Architecture

- Show the animated pipeline.
- LLM: semantic understanding of every note.
- Python normalization and guardrails: exact hours, quantities, and six allowed directive types.
- SciPy HiGHS: linear-programming optimization.
- Independent replay validator: verifies the exact returned plan.

## 1:20–2:10 — Implementation

- Load SAMPLE-10 and show the reserve plus grid-cap interpretations.
- Highlight start-inclusive/end-exclusive hours.
- Show energy balance, battery bounds, rate limits, grid caps, and end-of-day neutrality.
- Open the 24-hour chart, battery SOC, timeline, and schedule table.

## 2:10–2:40 — API demonstration

- Call `GET /health` and show `{"status":"ok"}`.
- Submit `POST /optimize-energy` from the frontend.
- Briefly open the request/response JSON inspector.
- Show `10/10 public cases passed` from the sample runner.

## 2:40–3:00 — Reproducibility

- Show the pinned requirements, `.env.example`, tests, Dockerfile, and README quickstart.
- State that secrets remain server-side and the judging endpoints require no UI, login, VPN, or manual approval.
