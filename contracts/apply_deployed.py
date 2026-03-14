#!/usr/bin/env python3
"""After deploy.py succeeds, run this to print backend .env lines for contract addresses."""
import json
from pathlib import Path

deployed_path = Path(__file__).parent / "deployed.json"
if not deployed_path.exists():
    print("Run deploy.py first. deployed.json not found.")
    exit(1)
with open(deployed_path) as f:
    data = json.load(f)
c = data.get("contracts", {})
print("# Add these to backend/.env (contract addresses from deploy):")
print(f"COMPLIANCE_REGISTRY_ADDRESS={c.get('ComplianceRegistry', '')}")
print(f"AEGISFLOW_VAULT_ADDRESS={c.get('AegisFlowVault', '')}")
