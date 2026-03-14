"""Application configuration from environment."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    neon_rpc_url: str = "https://devnet.neonevm.org"
    private_key: str = ""
    compliance_registry_address: str = ""
    aegisflow_vault_address: str = ""
    openai_api_key: str = ""
    travel_rule_threshold: float = 1000.0
    kyt_api_url: str | None = None
    kyt_api_key: str | None = None
    database_url: str = "sqlite+aiosqlite:///./aegisflow.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
