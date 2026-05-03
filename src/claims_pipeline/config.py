from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "assignment" / "policy_terms.json"
TEST_CASES_PATH = ROOT / "assignment" / "test_cases.json"


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
    # Directory for claim uploads (must be shared by api + claim-worker in Docker)
    upload_dir: str = ""
    max_upload_bytes: int = 20 * 1024 * 1024  # 20 MiB per file

    # Laplacian variance below this flags severe blur (computed from pixels, not UI).
    readability_hard_laplacian_floor: float = 35.0


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    return s


def upload_root_path() -> Path:
    s = get_settings()
    d = (s.upload_dir or "").strip()
    return Path(d) if d else (ROOT / "uploads")
