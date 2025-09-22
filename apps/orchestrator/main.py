from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GPTco Orchestrator", version="0.1.0")

class PlanRequest(BaseModel):
    okr: str
    tier: str = "A1"

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/plan")
def plan(req: PlanRequest):
    # placeholder planner
    tasks = [
        {"id":"t1","desc":"Draft outreach sequence","pod":"growth"},
        {"id":"t2","desc":"Create CRM segment","pod":"sales"}
    ]
    return {"okr": req.okr, "tier": req.tier, "tasks": tasks}
