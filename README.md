# GridWise Energy Optimizer

GridWise is an LLM-assisted smart-campus energy optimization service developed for the **BUP CSE Fest 2026 Hackathon Preliminary Round**.

It receives a 24-hour campus energy scenario and 1–3 natural-language operator notes, converts each note into a supported machine-checkable directive using a language model, validates the result deterministically, and produces a minimum-cost 24-hour energy schedule using linear programming.

## Live Service

**Base URL**

```text
https://smart-optimization.onrender.com
```

**Swagger UI**

```text
https://smart-optimization.onrender.com/docs
```

**OpenAPI Schema**

```text
https://smart-optimization.onrender.com/openapi.json
```

Required endpoints:

```text
GET  /health
POST /optimize-energy
```

---

## System Architecture

```text
24-hour energy scenario + operator notes
                  |
                  v
         Pydantic validation
                  |
                  v
        LLM interpretation
        (Gemini 3.8 Flash)
                  |
                  v
 deterministic normalization and guardrails
                  |
                  v
       directive application
                  |
                  v
  SciPy HiGHS linear-program optimizer
                  |
                  v
       24-hour energy plan
                  |
                  v
      replay/final validation
                  |
                  v
          JSON response
```

The language model is used only for understanding the operator notes. Exact time conversion, numeric normalization, supported-directive validation, optimization constraints, battery rules, and final schedule validation are handled deterministically in Python.

---

## Supported Directives

Each operator note is mapped to exactly one of the following directive types:

| Directive | Meaning |
|---|---|
| `solar_reduction` | Reduce usable solar during selected hours |
| `minimum_battery_reserve` | Require a minimum stored battery level |
| `no_charge_window` | Disable battery charging during selected hours |
| `no_discharge_window` | Disable battery discharging during selected hours |
| `max_grid_window` | Limit grid import during selected hours |
| `no_op` | Ignore notes unrelated to the 24-hour energy schedule |

Time windows follow a start-inclusive, end-exclusive convention.

Example:

```text
1 PM to 3 PM -> [13, 14]
```

For solar reduction, `factor` represents the usable solar fraction remaining.

Example:

```text
80% reduction -> factor = 0.2
```

---

## Optimization Model

For every hour:

```text
grid_kwh + solar_used_kwh + battery_discharge
=
demand_kwh + battery_charge
```

The optimizer minimizes:

```text
sum(grid_kwh[h] * tariff_bdt_per_kwh[h])
```

subject to:

- battery capacity limits,
- minimum battery energy,
- hourly charge/discharge limits,
- solar availability,
- operator directives,
- non-negative grid import,
- hourly energy balance,
- final battery energy equal to the initial battery energy.

Optimization is implemented using:

```python
scipy.optimize.linprog(method="highs")
```

---

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- HTTPX
- NumPy
- SciPy / HiGHS
- python-dotenv

### LLM

- Google Gemini API
- Model: `gemini-3.8-flash`
- OpenAI-compatible Gemini endpoint
- Structured JSON response
- HTTPX client

### Frontend

- HTML
- CSS
- JavaScript

### Testing

- Pytest
- pytest-asyncio
- Official public sample cases

---

## Environment Variables

Create a `.env` file using `.env.example`.

```env
LLM_PROVIDER=openai
LLM_MODEL=gemini-3.8-flash
LLM_API_KEY=YOUR_GEMINI_API_KEY
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_TIMEOUT_SECONDS=10.0
PORT=8000
```

`LLM_PROVIDER=openai` refers to the OpenAI-compatible API format used by the client. The actual model provider is Google Gemini.

Do not commit the real `.env` file or API key.

---

## Local Setup

### Windows PowerShell

```powershell
git clone <YOUR_REPOSITORY_URL>
cd project

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Copy-Item .env.example .env
```

Add the Gemini API key to `.env`, then start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Local API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## API Usage

### Health Check

```http
GET /health
```

Example:

```powershell
curl.exe "https://smart-optimization.onrender.com/health"
```

Expected response:

```json
{
  "status": "ok"
}
```

---

### Optimize Energy

```http
POST /optimize-energy
Content-Type: application/json
```

The request contains:

- `scenario_id`
- `operator_notes`
- `hours`
- `battery`

Example request structure:

```json
{
  "scenario_id": "SAMPLE-01",
  "operator_notes": [
    "Do not charge the battery from 2 PM until 4 PM."
  ],
  "hours": [
    {
      "hour": 0,
      "demand_kwh": 90,
      "solar_kwh": 0,
      "tariff_bdt_per_kwh": 6
    }
  ],
  "battery": {
    "capacity_kwh": 220,
    "initial_energy_kwh": 110,
    "minimum_energy_kwh": 40,
    "max_charge_kwh_per_hour": 50,
    "max_discharge_kwh_per_hour": 50
  }
}
```

The real request must contain exactly 24 hourly records covering hours `0` through `23`.

Example response structure:

```json
{
  "scenario_id": "SAMPLE-01",
  "directive_interpretation": [
    {
      "note_index": 0,
      "applies": true,
      "directive_type": "no_charge_window",
      "structured_adjustment": {
        "hours": [14, 15]
      },
      "explanation": "Battery charging is disabled during the requested time window."
    }
  ],
  "hourly_plan": [
    {
      "hour": 0,
      "grid_kwh": 90,
      "solar_used_kwh": 0,
      "battery_action": "idle",
      "battery_kwh": 0,
      "battery_energy_after_kwh": 110
    }
  ],
  "total_grid_kwh": 0,
  "total_cost_bdt": 0,
  "peak_grid_kwh": 0,
  "plan_summary": "Optimized 24-hour schedule."
}
```

The actual response contains exactly 24 `hourly_plan` rows.

---

## Test the Deployed API

If `scenario.json` contains one valid request:

```powershell
curl.exe -X POST "https://smart-optimization.onrender.com/optimize-energy" `
  -H "Content-Type: application/json" `
  --data-binary "@scenario.json"
```

The official public sample file contains multiple cases. Send only the `input` object of an individual case to `/optimize-energy`.

For example, to extract the first public case:

```powershell
$data = Get-Content ".\public_samples\BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json" -Raw | ConvertFrom-Json
$data.cases[0].input | ConvertTo-Json -Depth 20 | Set-Content ".\scenario.json"
```

Then:

```powershell
curl.exe -X POST "https://smart-optimization.onrender.com/optimize-energy" `
  -H "Content-Type: application/json" `
  --data-binary "@scenario.json"
```

---

## Tests

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The repository also supports deterministic local testing of the public examples:

```powershell
$env:LLM_PROVIDER = "deterministic"
.\.venv\Scripts\python.exe -m pytest -q
```

The deterministic mode is intended for local testing only. Production uses the configured language model for operator-note interpretation.

---

## Docker

Build the image:

```bash
docker build -t gridwise:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e LLM_MODEL=gemini-3.8-flash \
  -e LLM_API_KEY=YOUR_GEMINI_API_KEY \
  -e LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai \
  -e LLM_TIMEOUT_SECONDS=10.0 \
  gridwise:latest
```

Then verify:

```bash
curl http://127.0.0.1:8000/health
```

---

## Project Structure

```text
project/
├── app/
│   ├── llm/
│   ├── main.py
│   ├── config.py
│   └── ...
├── src/
├── tests/
├── scripts/
├── public_samples/
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── index.html
├── styles.css
└── README.md
```

---

## Frontend

The included frontend provides a simple interface for:

- entering the 24-hour energy profile,
- configuring battery parameters,
- entering up to three operator notes,
- running the optimization,
- viewing interpreted directives,
- viewing optimization results,
- inspecting the 24-hour schedule.

The automated judge can call the JSON API directly without using the frontend.

---

## Deployment

The production service is hosted on Render:

```text
https://smart-optimization.onrender.com
```

Render start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Production secrets such as `LLM_API_KEY` are configured through Render environment variables and are not stored in the repository.

---

## Credits

Built with FastAPI, Pydantic, HTTPX, NumPy, SciPy/HiGHS, Pytest, Google Gemini API, and Render.

Challenge specification and public sample cases are provided by **BUP CSE Fest 2026**.
