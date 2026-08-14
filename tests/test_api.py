from fastapi.testclient import TestClient

from app.main import app


def test_health_and_dashboard():
    with TestClient(app) as client:
        assert client.get("/health").json()["model_ready"] is True
        assert "TriageFlow Intelligence" in client.get("/").text


def test_network_ticket_routes_to_network_operations():
    payload = {
        "subject": "Remote office cannot resolve internal DNS",
        "description": "An entire office cannot resolve internal hostnames and 140 users have no workaround.",
        "requester": "Service Desk",
        "affected_users": 140,
        "business_service": "Corporate Network",
    }
    with TestClient(app) as client:
        result = client.post("/api/classify", json=payload)
        assert result.status_code == 201
        body = result.json()
        assert body["category"] == "Network & Connectivity"
        assert body["assignment_group"] == "Network Operations"
        assert body["rationale_terms"]


def test_security_ticket_is_explainable_and_reviewed():
    payload = {
        "subject": "Suspicious sign-in and external forwarding rule",
        "description": (
            "Security monitoring detected an unusual login and a confidential mailbox forwarding rule."
        ),
        "affected_users": 1,
    }
    with TestClient(app) as client:
        body = client.post("/api/classify", json=payload).json()
        assert body["category"] == "Security & Compliance"
        assert len(body["category_alternatives"]) == 3
        assert body["knowledge_article"].startswith("KB-745")


def test_high_impact_ticket_predicts_urgent_priority():
    payload = {
        "subject": "Company-wide production platform outage",
        "description": (
            "All customer-facing teams are stopped, 850 employees are affected, and no workaround exists."
        ),
        "affected_users": 850,
        "business_service": "Customer Operations",
    }
    with TestClient(app) as client:
        body = client.post("/api/classify", json=payload).json()
        assert body["priority"] in {"P1", "P2"}
        if body["priority"] == "P1":
            assert body["needs_human_review"] is True


def test_feedback_round_trip():
    payload = {
        "subject": "Laptop battery drains in one hour",
        "description": (
            "One employee reports rapid battery drain and needs a hardware diagnostic appointment."
        ),
        "affected_users": 1,
    }
    with TestClient(app) as client:
        ticket = client.post("/api/classify", json=payload).json()
        response = client.post("/api/feedback", json={"ticket_id": ticket["ticket_id"], "accepted": True})
        assert response.status_code == 201
        assert response.json()["status"] == "recorded"


def test_unknown_feedback_ticket_returns_404():
    with TestClient(app) as client:
        response = client.post("/api/feedback", json={"ticket_id": "TF-MISSING", "accepted": False})
        assert response.status_code == 404


def test_batch_classification_and_limit():
    tickets = [
        {
            "subject": "Mailbox quota warning",
            "description": "One employee cannot receive new email due to mailbox quota.",
        },
        {
            "subject": "Database connections exhausted",
            "description": "The finance application cannot obtain database connections for several users.",
        },
    ]
    with TestClient(app) as client:
        response = client.post("/api/classify/batch", json={"tickets": tickets})
        assert response.status_code == 201
        assert len(response.json()) == 2


def test_queue_contains_saved_predictions():
    with TestClient(app) as client:
        client.post(
            "/api/classify",
            json={
                "subject": "Printer repeatedly jams",
                "description": "The office printer reports a hardware jam for five employees.",
            },
        )
        queue = client.get("/api/queue?limit=5").json()
        assert 1 <= len(queue) <= 5
        assert {"ticket_id", "category", "priority"} <= set(queue[0])


def test_metrics_meet_quality_floor():
    with TestClient(app) as client:
        model = client.get("/api/metrics").json()["model"]
        assert model["dataset_rows"] == 384
        assert model["category_macro_f1"] >= 0.80
        assert model["priority_macro_f1"] >= 0.80


def test_model_card_has_boundaries():
    with TestClient(app) as client:
        card = client.get("/api/model-card").json()
        assert "Autonomous closure" in card["not_for"]
        assert "human" in card["human_review_policy"].lower()


def test_validation_rejects_empty_or_oversized_inputs():
    with TestClient(app) as client:
        assert client.post("/api/classify", json={"subject": "x", "description": "short"}).status_code == 422
        assert client.get("/api/queue?limit=101").status_code == 422


def test_openapi_exposes_core_routes():
    with TestClient(app) as client:
        paths = client.get("/openapi.json").json()["paths"]
        assert {"/api/classify", "/api/classify/batch", "/api/feedback", "/api/model-card"} <= set(paths)
