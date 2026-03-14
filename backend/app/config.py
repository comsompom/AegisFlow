"""Application configuration from environment. Solana-only for hackathon."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Solana (required for hackathon — build on Solana)
    solana_rpc_url: str = "https://api.devnet.solana.com"
    solana_program_id: str = ""
    solana_keypair_path: str = ""  # path to keypair JSON (e.g. ~/.config/solana/id.json)
    solana_private_key: str = ""   # alternative: base58 or base64 secret key for signer
    # App
    openai_api_key: str = ""
    travel_rule_threshold: float = 1000.0
    kyt_api_url: str | None = None
    kyt_api_key: str | None = None
    database_url: str = "sqlite:///./aegisflow.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
