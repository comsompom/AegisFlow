"""Neon EVM (Web3) client for ComplianceRegistry and AegisFlowVault."""
from web3 import Web3
from app.config import get_settings

# Minimal ABI for ComplianceRegistry
REGISTRY_ABI = [
    {"inputs": [{"name": "account", "type": "address"}], "name": "isWhitelisted", "outputs": [{"type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "isBlacklisted", "outputs": [{"type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "canReceive", "outputs": [{"type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "maxPerTx", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "maxDailyVolume", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "dailyVolumeUsed", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "addToWhitelist", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "removeFromWhitelist", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "addToBlacklist", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "_maxPerTx", "type": "uint256"}, {"name": "_maxDailyVolume", "type": "uint256"}], "name": "setLimits", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

VAULT_ABI = [
    {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "deposit", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "withdrawTo", "outputs": [{"type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
]


def get_web3() -> Web3:
    s = get_settings()
    return Web3(Web3.HTTPProvider(s.neon_rpc_url))


def get_registry_contract():
    w3 = get_web3()
    s = get_settings()
    if not s.compliance_registry_address:
        return None
    return w3.eth.contract(
        address=Web3.to_checksum_address(s.compliance_registry_address),
        abi=REGISTRY_ABI,
    )


def get_vault_contract():
    w3 = get_web3()
    s = get_settings()
    if not s.aegisflow_vault_address:
        return None
    return w3.eth.contract(
        address=Web3.to_checksum_address(s.aegisflow_vault_address),
        abi=VAULT_ABI,
    )


def is_whitelisted(address: str) -> bool:
    contract = get_registry_contract()
    if not contract:
        return False
    return contract.caller.isWhitelisted(Web3.to_checksum_address(address))


def get_limits() -> dict:
    contract = get_registry_contract()
    if not contract:
        return {"maxPerTx": 0, "maxDailyVolume": 0, "dailyVolumeUsed": 0}
    return {
        "maxPerTx": contract.caller.maxPerTx(),
        "maxDailyVolume": contract.caller.maxDailyVolume(),
        "dailyVolumeUsed": contract.caller.dailyVolumeUsed(),
    }


def get_balance(address: str) -> int:
    contract = get_vault_contract()
    if not contract:
        return 0
    return contract.caller.balanceOf(Web3.to_checksum_address(address))
