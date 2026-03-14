"""Treasury AI agent: proposes transfers/swaps based on rules + optional LLM."""
from datetime import datetime
from app.config import get_settings
from app.services.blockchain import get_limits, get_balance


def run_once() -> dict:
    """One iteration: fetch limits/balance, apply rules, optionally call LLM, append proposals."""
    settings = get_settings()
    limits = get_limits()
    # Mock balance for MVP (would be vault balance in production)
    balance = 0
    try:
        from app.services.blockchain import get_vault_contract
        w3 = __import__("app.services.blockchain", fromlist=["get_web3"]).get_web3()
        if settings.private_key:
            acc = w3.eth.account.from_key(settings.private_key)
            balance = get_balance(acc.address)
    except Exception:
        pass

    proposals = []
    # Rule: if daily remaining is high, could propose a rebalance (mock)
    max_per_tx = limits.get("maxPerTx", 0)
    daily_used = limits.get("dailyVolumeUsed", 0)
    daily_max = limits.get("maxDailyVolume", 0)
    daily_remaining = max(0, daily_max - daily_used)

    if daily_remaining > 0 and max_per_tx > 0:
        # Placeholder proposal
        proposal = {
            "action": "transfer",
            "amount": str(min(daily_remaining, max_per_tx) // 2),
            "recipient": "0x0000000000000000000000000000000000000001",
            "reason": "Treasury rebalance (mock rule)",
            "status": "pending",
        }
        proposals.append(proposal)

    # Optional: call OpenAI for reasoning
    if settings.openai_api_key:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.openai_api_key)
            msg = llm.invoke([HumanMessage(content=f"Given maxPerTx={max_per_tx}, dailyRemaining={daily_remaining}, suggest one sentence treasury action.")])
            if proposals:
                proposals[0]["reason"] = msg.content[:200] if hasattr(msg, "content") else str(msg)[:200]
        except Exception:
            pass

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "proposals_count": len(proposals),
        "proposals": proposals,
        "balance": balance,
        "daily_remaining": daily_remaining,
    }
