from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GPTco Orchestrator", version="0.1.0")

class PlanRequest(BaseModel):
    okr: str
    tier: str = "A1"

@app.get("/")
def index():
    return {"service":"gptco-orchestrator","endpoints":["/healthz","/plan","/gate","/execute"]}


@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/plan")
def plan(req: PlanRequest):
    tasks = [
        {"id":"t1","desc":"Draft outreach sequence","pod":"growth"},
        {"id":"t2","desc":"Create CRM segment","pod":"sales"}
    ]
    return {"okr": req.okr, "tier": req.tier, "tasks": tasks}

import os, time, yaml
from typing import Any, Dict
from fastapi import HTTPException
from pydantic import BaseModel

# --- load policies once (hot-reload on container restart) ---
POLICY_TIERS_PATH = os.getenv("POLICY_TIERS_PATH", "configs/policy/autonomy_tiers.yaml")
REDLINES_PATH     = os.getenv("REDLINES_PATH", "configs/policy/redlines.yaml")
SPEND_CAP_USD     = float(os.getenv("SPEND_CAP_USD", "50"))

with open(POLICY_TIERS_PATH, "r", encoding="utf-8") as f:
    TIERS = yaml.safe_load(f)

with open(REDLINES_PATH, "r", encoding="utf-8") as f:
    REDLINES = yaml.safe_load(f)["redlines"]

def redline(action: Dict[str, Any]) -> bool:
    """Very simple matcher for demo."""
    a = action.get("action")
    data = action.get("data")
    site = action.get("website")
    for r in REDLINES:
        if r.get("action") and r["action"] == a:
            return True
        if r.get("data") and r["data"] == data:
            return True
        if r.get("website") and site and r["website"].replace("*","") in site:
            return True
    return False

def gate_action(action: Dict[str, Any], tier: str) -> str:
    if tier not in TIERS:
        return "BLOCK"
    if redline(action):
        return "BLOCK"
    # allowlist check
    allowed = set(TIERS[tier].get("allow_tools", []))
    if "*" not in allowed and action.get("tool") not in allowed:
        return "REVIEW"
    # cost check (if tool estimates cost)
    cost = float(action.get("cost_estimate_usd", 0))
    if cost > SPEND_CAP_USD:
        return "BLOCK"
    # risk threshold (0–5 scale; stubbed)
    risk = int(action.get("risk", 1))
    auto_threshold = int(TIERS[tier].get("auto_threshold", 0))
    return "AUTO" if risk <= auto_threshold else "REVIEW"

class GateRequest(BaseModel):
    tier: str
    action: Dict[str, Any]

@app.post("/gate")
def gate(req: GateRequest):
    decision = gate_action(req.action, req.tier)
    return {"decision": decision}

# --- EXECUTION STUBS ---

# pretend tool registry (use your YAML manifests later)
TOOL_IMPLS = {
    "draft.email": lambda payload: {"draft": f"Subject: {payload.get('subject','Hello')}\n\n{payload.get('body','...')}"},
    "ticket.create": lambda payload: {"ticket_id": f"T-{int(time.time())}"},
    "crm.update": lambda payload: {"success": True, "diff": payload.get("updates",{})},
}

class ExecRequest(BaseModel):
    tier: str
    action: Dict[str, Any]  # {tool: "crm.update", payload: {...}, cost_estimate_usd: 0.001, risk: 2}

@app.post("/execute")
def execute(req: ExecRequest):
    decision = gate_action(req.action, req.tier)
    if decision == "BLOCK":
        raise HTTPException(403, detail="Blocked by policy")
    if decision == "REVIEW":
        # in prod: create an approval card (Slack/Email) and return pending
        return {"status":"pending_review", "reason":"Requires human approval"}
    tool = req.action.get("tool")
    payload = req.action.get("payload", {})
    impl = TOOL_IMPLS.get(tool)
    if not impl:
        raise HTTPException(400, detail=f"Unknown tool: {tool}")
    result = impl(payload)
    # TODO: write to audit log table
    return {"status": "ok", "tool": tool, "result": result}
