# GridWise — AI-Assisted Campus Energy Optimization

GridWise accepts a complete 24-hour campus energy scenario and 1–3 operator notes, interprets each note with a language-capable model, applies deterministic guardrails, finds a minimum-cost schedule with SciPy HiGHS, independently replays that schedule, and returns the exact official JSON response. The included control-center frontend is optional; judging endpoints remain directly callable.

## Architecture

```text
POST /optimize-energy
  → Pydantic request validation
  → concurrent LLM note interpretation
  → deterministic normalization + guardrails
  → directive application
  → scipy.optimize.linprog(method="highs")
  → 24-hour plan builder
  → independent replay validation
  → totals recomputed from returned plan
  → exact response schema
```

The LLM handles language understanding only. Python owns exact hours, percentage/fraction conversion, type enforcement, numeric safety, and constraints. The optimizer owns cost minimization. Replay validates the exact serialized plan.

## Stack

Python 3.11+, FastAPI, Uvicorn, Pydantic v2, HTTPX, NumPy, SciPy HiGHS, Pytest, and a dependency-free modular HTML/CSS/JavaScript frontend.

## Configuration

Copy `.env.example` to `.env` and provide values without committing the file:

```text
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=your-provider-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT_SECONDS=5.0
PORT=8000
```

`openai` is the production provider mode. It uses strict JSON Schema output and one bounded correction retry. `LLM_PROVIDER=deterministic` is an explicitly non-production offline mode for public-sample testing and UI demonstrations; do not use it as the submitted model configuration.

## Local setup

```powershell
cd project
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:LLM_PROVIDER = "openai"
$env:LLM_MODEL = "gpt-4.1-mini"
$env:LLM_API_KEY = "..."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000` for the frontend or call the API directly.

## API

```bash
curl http://127.0.0.1:8000/health
```

Expected: `{"status":"ok"}`.

```bash
curl -X POST http://127.0.0.1:8000/optimize-energy \
  -H "Content-Type: application/json" \
  --data @scenario.json
```

The request contains exactly `scenario_id`, `operator_notes`, `hours`, and `battery`. The response contains exactly `scenario_id`, `directive_interpretation`, `hourly_plan`, `total_grid_kwh`, `total_cost_bdt`, `peak_grid_kwh`, and `plan_summary`.

## Tests

```powershell
$env:LLM_PROVIDER = "deterministic"
.\.venv\Scripts\python.exe -m pytest -q
```

The suite covers health, request validation, normalization, all ten public samples, cost equivalence, and replay corruption rejection.

Run the official pack through a running service:

```powershell
$env:LLM_PROVIDER = "deterministic"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
.\.venv\Scripts\python.exe scripts\run_public_samples.py
```

Expected final line: `10/10 public cases passed`.

## Docker

```bash
docker build -t gridwise:latest .
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e LLM_MODEL=gpt-4.1-mini \
  -e LLM_API_KEY=your-provider-key \
  gridwise:latest
```

The image binds to `0.0.0.0:8000` and contains no credentials.

## Frontend

The integrated UI is an operator-facing AI energy assistant. Operators can configure the campus energy profile, describe operating constraints conversationally, review how each instruction was understood, build the live optimized plan, explore the 24-hour energy profile and battery state, and inspect the hourly schedule. Technical API and model internals stay behind the interface, while health status, responsive navigation, loading feedback, and recoverable errors keep the experience production-ready. Public samples remain available to the automated test suite but are not exposed in the product interface.

## Reliability and security

- Bounded concurrent note calls and hard timeout
- Strict semantic and final-directive validation
- No silent directive relaxation
- Sanitized errors with no provider payloads or secrets
- Final totals recomputed from the returned plan
- Static routes expose only intended frontend assets

## Known limitations

- Production requires a reachable configured model provider.
- The endpoint must support strict `json_schema` response formatting.
- External deployment and registry credentials are the submitting team's responsibility.

## Credits

FastAPI, Pydantic, HTTPX, NumPy, SciPy/HiGHS, Uvicorn, and Pytest. Public examples are from the supplied BUP CSE Fest 2026 GridWise sample pack.
