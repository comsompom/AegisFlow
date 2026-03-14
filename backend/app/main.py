"""AegisFlow Backend API — compliance, AI agent, blockchain client."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import compliance, transfers, audit, ai_agent, health

app = FastAPI(
    title="AegisFlow API",
    description="Compliance, treasury, and blockchain API for AegisFlow",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["compliance"])
app.include_router(transfers.router, prefix="/api/transfers", tags=["transfers"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(ai_agent.router, prefix="/api/ai", tags=["ai-agent"])


@app.get("/")
def root():
    return {"service": "AegisFlow API", "docs": "/docs"}
