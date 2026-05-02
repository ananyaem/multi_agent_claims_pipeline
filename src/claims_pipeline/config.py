from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "policy_terms.json"
TEST_CASES_PATH = ROOT / "test_cases.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    llm_model: str = "gemini-3-flash-preview"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = f"sqlite:///{ROOT / 'claims.db'}"
    llm_rate_limit_rpm: int = 60
    llm_request_timeout_sec: int = 120
    api_base_url: str = "http://127.0.0.1:8000"

    claims_queue: str = "claims:queue"
    llm_queue: str = "llm:queue"


@lru_cache
def get_settings() -> Settings:
    return Settings()
