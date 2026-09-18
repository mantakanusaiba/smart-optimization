from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.errors import GridWiseError
from app.models.request import OptimizeEnergyRequest
from app.models.response import OptimizeEnergyResponse
from app.services.optimize_service import optimize_service

logger = logging.getLogger("gridwise")
app = FastAPI(title="GridWise Energy Optimizer", version="1.0.0", docs_url="/docs", redoc_url=None)


@app.exception_handler(RequestValidationError)
async def request_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Request format is invalid.", "errors": [{"location": list(error["loc"]), "message": error["msg"]} for error in exc.errors()]})


@app.exception_handler(GridWiseError)
async def controlled_error(_: Request, exc: GridWiseError) -> JSONResponse:
    logger.warning("Controlled GridWise failure: %s", type(exc).__name__)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.public_message})


@app.exception_handler(Exception)
async def internal_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled GridWise failure")
    return JSONResponse(status_code=500, content={"detail": "Optimization service could not complete the request."})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/optimize-energy", response_model=OptimizeEnergyResponse)
async def optimize_energy(request: OptimizeEnergyRequest) -> OptimizeEnergyResponse:
    return await optimize_service(request)


frontend = Path(__file__).resolve().parents[1]
app.mount("/src", StaticFiles(directory=frontend / "src"), name="frontend-src")
app.mount("/public", StaticFiles(directory=frontend / "public"), name="frontend-public")


@app.get("/", include_in_schema=False)
async def frontend_index() -> FileResponse:
    return FileResponse(frontend / "index.html")


@app.get("/styles.css", include_in_schema=False)
async def frontend_styles() -> FileResponse:
    return FileResponse(frontend / "styles.css", media_type="text/css")
