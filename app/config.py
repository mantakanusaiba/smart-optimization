from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str
    llm_timeout_seconds: float
    port: int


def get_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai").strip().lower(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini").strip(),
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "5.0")),
        port=int(os.getenv("PORT", "8000")),
    )
