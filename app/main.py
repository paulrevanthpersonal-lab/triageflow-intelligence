from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ml import ModelBundle, predict, train
from .models import BatchInput, FeedbackInput, Prediction, TicketInput
from .store import initialize, operational_metrics, recent_classifications, save_classification, save_feedback

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
BUNDLE: ModelBundle | None = None

DEMO_TICKETS = [
    TicketInput(
        subject="VPN disconnects for remote sales team",
        description=(
            "Multiple departments report repeated VPN disconnects and 95 employees "
            "have only a limited workaround."
        ),
        requester="Service Desk",
        affected_users=95,
        business_service="Remote Access",
    ),
    TicketInput(
        subject="Conditional Access block after device replacement",
        description=(
            "Three administrators cannot sign in after replacing managed devices "
            "and privileged work is stopped."
        ),
        requester="Executive Support",
        affected_users=3,
        business_service="Identity Platform",
    ),
    TicketInput(
        subject="Customer API returns intermittent server errors",
        description=(
            "Several employees see intermittent API failures, but retrying allows most requests to complete."
        ),
        requester="Application Desk",
        affected_users=8,
        business_service="Customer Operations",
    ),
    TicketInput(
        subject="Unexpected administrator identity detected",
        description=(
            "Security monitoring found an unapproved privileged identity and the "
            "affected scope is under investigation."
        ),
        requester="SOC Analyst",
        affected_users=1,
        business_service="Corporate IT",
    ),
    TicketInput(
        subject="Shared drive permissions missing for project team",
        description=(
            "A small team cannot access a shared project folder, but an alternate "
            "collaboration path is available."
        ),
        requester="Collaboration Desk",
        affected_users=5,
        business_service="Corporate IT",
    ),
    TicketInput(
        subject="Nightly import rejected data rows",
        description=(
            "The nightly data load rejected several rows and reporting is stale for one business team."
        ),
        requester="Data Operations",
        affected_users=8,
        business_service="Finance Systems",
    ),
    TicketInput(
        subject="Cloud function times out during peak demand",
        description=(
            "An entire office sees cloud function timeouts and a limited manual workaround is available."
        ),
        requester="Cloud Operations",
        affected_users=140,
        business_service="Corporate IT",
    ),
    TicketInput(
        subject="Laptop battery drains within one hour",
        description="One employee reports rapid battery drain and requests an endpoint hardware diagnostic.",
        requester="Field Support",
        affected_users=1,
        business_service="Corporate IT",
    ),
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    global BUNDLE
    initialize()
    BUNDLE = train()
    if not recent_classifications(1):
        for index, ticket in enumerate(DEMO_TICKETS, start=1):
            payload = ticket.model_dump()
            result = predict(BUNDLE, payload, f"TF-DEMO{index:02d}")
            save_classification(payload, result)
    yield


app = FastAPI(
    title="TriageFlow Intelligence",
    summary="Explainable help-desk ticket classification and routing API",
    description=(
        "Classifies support tickets by category and priority, exposes confidence "
        "and rationale, and keeps a human feedback trail."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(WEB / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "triageflow-intelligence", "model_ready": BUNDLE is not None}


def classify_one(payload: TicketInput) -> dict:
    if BUNDLE is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    ticket_id = f"TF-{uuid4().hex[:8].upper()}"
    data = payload.model_dump()
    result = predict(BUNDLE, data, ticket_id)
    save_classification(data, result)
    return result


@app.post("/api/classify", response_model=Prediction, status_code=201)
def classify(payload: TicketInput) -> dict:
    return classify_one(payload)


@app.post("/api/classify/batch", response_model=list[Prediction], status_code=201)
def classify_batch(payload: BatchInput) -> list[dict]:
    return [classify_one(ticket) for ticket in payload.tickets]


@app.get("/api/queue")
def queue(limit: int = Query(default=25, ge=1, le=100)) -> list[dict]:
    return recent_classifications(limit)


@app.post("/api/feedback", status_code=201)
def feedback(payload: FeedbackInput) -> dict:
    try:
        return save_feedback(payload.model_dump())
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Classification not found") from error


@app.get("/api/metrics")
def metrics() -> dict:
    if BUNDLE is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {"model": BUNDLE.metrics, "operations": operational_metrics(), "data_hash": BUNDLE.data_hash}


@app.get("/api/model-card")
def model_card() -> dict:
    if BUNDLE is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {
        "name": "TF-IDF logistic regression multi-task classifier",
        "version": "1.0.0",
        "intended_use": "Decision support for synthetic or privacy-reviewed internal help-desk tickets.",
        "not_for": [
            "Autonomous closure",
            "Employee performance evaluation",
            "Emergency or life-safety dispatch",
        ],
        "human_review_policy": "P1 tickets and low-confidence predictions require human validation.",
        "training_data": "Deterministic synthetic dataset; no real employee or customer information.",
        "metrics": BUNDLE.metrics,
    }
