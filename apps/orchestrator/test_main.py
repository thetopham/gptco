from fastapi.testclient import TestClient

from apps.orchestrator.main import app, SPEND_CAP_USD

client = TestClient(app)


def test_index_returns_metadata():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "gptco-orchestrator"
    assert set(payload["endpoints"]) >= {"/healthz", "/plan", "/gate", "/execute"}


def test_plan_returns_tasks_and_echoes_input():
    response = client.post(
        "/plan",
        json={"okr": "Increase demo volume", "tier": "A1"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["okr"] == "Increase demo volume"
    assert payload["tier"] == "A1"
    assert isinstance(payload["tasks"], list) and len(payload["tasks"]) == 2
    assert {task["id"] for task in payload["tasks"]} == {"t1", "t2"}


def test_gate_blocks_unknown_tier():
    response = client.post(
        "/gate",
        json={"tier": "AX", "action": {"tool": "draft.email", "risk": 1}},
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"


def test_gate_blocks_redline_action():
    response = client.post(
        "/gate",
        json={
            "tier": "A5",
            "action": {"tool": "draft.email", "action": "payment.execute"},
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"


def test_gate_auto_when_tool_allowed_and_low_risk():
    response = client.post(
        "/gate",
        json={"tier": "A1", "action": {"tool": "draft.email", "risk": 1}},
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "AUTO"


def test_gate_marks_unlisted_tool_for_review():
    response = client.post(
        "/gate",
        json={"tier": "A1", "action": {"tool": "crm.update", "risk": 1}},
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "REVIEW"


def test_gate_blocks_when_cost_exceeds_cap():
    response = client.post(
        "/gate",
        json={
            "tier": "A5",
            "action": {
                "tool": "invoice.issue",
                "risk": 1,
                "cost_estimate_usd": SPEND_CAP_USD + 1,
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"


def test_execute_returns_pending_review_for_high_risk():
    response = client.post(
        "/execute",
        json={
            "tier": "A1",
            "action": {"tool": "draft.email", "risk": 3, "payload": {"body": "Hi"}},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "pending_review",
        "reason": "Requires human approval",
    }


def test_execute_blocks_on_redline():
    response = client.post(
        "/execute",
        json={
            "tier": "A2",
            "action": {
                "tool": "crm.update",
                "action": "payment.execute",
                "payload": {"updates": {}},
            },
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Blocked by policy"


def test_execute_runs_tool_and_returns_result():
    response = client.post(
        "/execute",
        json={
            "tier": "A1",
            "action": {
                "tool": "draft.email",
                "risk": 1,
                "payload": {"subject": "Hello", "body": "Welcome"},
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["tool"] == "draft.email"
    assert "Subject: Hello" in payload["result"]["draft"]


def test_execute_errors_for_unknown_tool_when_auto_allowed():
    response = client.post(
        "/execute",
        json={
            "tier": "A5",
            "action": {
                "tool": "nonexistent.tool",
                "risk": 1,
                "payload": {},
            },
        },
    )
    assert response.status_code == 400
    assert "Unknown tool" in response.json()["detail"]
