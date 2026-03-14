"""Pre-execution compliance checks: KYC, KYT, AML."""
import httpx
from app.config import get_settings
from app.services.blockchain import is_whitelisted, get_limits


def check_kyc(recipient_address: str) -> tuple[bool, str]:
    """KYC: recipient must be whitelisted."""
    if not recipient_address:
        return False, "Recipient address required"
    if not is_whitelisted(recipient_address):
        return False, "Recipient not whitelisted (KYC)"
    return True, ""


def check_aml(amount: int) -> tuple[bool, str]:
    """AML: amount within maxPerTx and daily volume."""
    limits = get_limits()
    max_per_tx = limits.get("maxPerTx", 0)
    max_daily = limits.get("maxDailyVolume", 0)
    used = limits.get("dailyVolumeUsed", 0)
    if amount > max_per_tx:
        return False, f"Amount exceeds maxPerTx ({max_per_tx})"
    if used + amount > max_daily:
        return False, f"Would exceed daily volume limit ({max_daily - used} remaining)"
    return True, ""


async def check_kyt(destination_address: str, amount: int) -> tuple[bool, str]:
    """KYT: optional risk check via external API. If no API configured, allow."""
    s = get_settings()
    if not s.kyt_api_url:
        return True, ""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                s.kyt_api_url,
                json={"address": destination_address, "amount": amount},
                headers={"Authorization": f"Bearer {s.kyt_api_key}"} if s.kyt_api_key else {},
                timeout=5.0,
            )
            if r.status_code != 200:
                return False, "KYT check failed"
            data = r.json()
            risk = data.get("risk_score", 0)
            if risk > 0.8:  # threshold
                return False, "High risk destination (KYT)"
    except Exception as e:
        return False, f"KYT error: {e}"
    return True, ""


def run_compliance_checks(recipient_address: str, amount: int) -> tuple[bool, str]:
    """Sync KYC + AML only (for simple use)."""
    ok, msg = check_kyc(recipient_address)
    if not ok:
        return False, msg
    ok, msg = check_aml(amount)
    if not ok:
        return False, msg
    return True, ""
