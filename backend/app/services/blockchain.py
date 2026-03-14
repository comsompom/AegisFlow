"""Blockchain client: Solana (Anchor) for hackathon. All projects must be built on Solana."""
from app.services import blockchain_solana

get_web3 = None  # not used on Solana

def get_registry_contract():
    return blockchain_solana.get_registry_contract()


def get_vault_contract():
    return blockchain_solana.get_vault_contract()


def is_whitelisted(address: str) -> bool:
    return blockchain_solana.is_whitelisted(address)


def get_limits() -> dict:
    return blockchain_solana.get_limits()


def get_balance(address: str) -> int:
    return blockchain_solana.get_balance(address)
