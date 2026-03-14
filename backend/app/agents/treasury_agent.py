"""Treasury AI agent: proposes transfers/swaps based on rules + optional LLM."""
from datetime import datetime
from app.config import get_settings
from app.services.blockchain import get_limits, get_balance


def run_once() -> dict:
    """One iteration: fetch limits/balance, apply rules, optionally call LLM, append proposals."""
    settings = get_settings()
    limits = get_limits()
    # Vault PDA balance (Solana: lamports)
    balance = get_balance("")

    proposals = []
    max_per_tx = limits.get("maxPerTx", 0)
    daily_used = limits.get("dailyVolumeUsed", 0)
    daily_max = limits.get("maxDailyVolume", 0)
    daily_remaining = max(0, daily_max - daily_used)

    if daily_remaining > 0 and max_per_tx > 0:
        proposal = {
            "action": "transfer",
            "amount": str(min(daily_remaining, max_per_tx) // 2),
            "recipient": "11111111111111111111111111111111",
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
