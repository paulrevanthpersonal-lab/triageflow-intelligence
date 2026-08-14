import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "tickets.csv"
ARTIFACT_PATH = ROOT / "artifacts" / "ticket_classifier.joblib"

ASSIGNMENT_GROUPS = {
    "Access & Identity": "Identity Operations",
    "Cloud & Infrastructure": "Cloud Platform Engineering",
    "Data & Database": "Data Services",
    "Email & Collaboration": "Collaboration Services",
    "Hardware & Devices": "Endpoint Engineering",
    "Network & Connectivity": "Network Operations",
    "Security & Compliance": "Security Operations Center",
    "Software & Applications": "Application Support",
}

SLA_MINUTES = {"P1": 15, "P2": 60, "P3": 240, "P4": 480}

KNOWLEDGE = {
    "Access & Identity": (
        "KB-104 · Restore identity and access",
        [
            "Confirm the affected identity and recent access changes.",
            "Review sign-in logs, MFA state, and policy evaluation.",
            "Use least-privilege recovery and verify a clean sign-in.",
        ],
    ),
    "Cloud & Infrastructure": (
        "KB-207 · Triage cloud workload health",
        [
            "Check service health, deployment history, and resource state.",
            "Correlate application, platform, and dependency telemetry.",
            "Apply the smallest reversible recovery action and validate.",
        ],
    ),
    "Data & Database": (
        "KB-318 · Investigate data service degradation",
        [
            "Preserve query, connection, and timing evidence.",
            "Inspect capacity, locks, schema changes, and replication health.",
            "Validate correctness as well as service availability.",
        ],
    ),
    "Email & Collaboration": (
        "KB-412 · Recover collaboration services",
        [
            "Confirm scope across users, clients, and locations.",
            "Check message trace, policy, quota, and service advisories.",
            "Verify send, receive, calendar, and file collaboration paths.",
        ],
    ),
    "Hardware & Devices": (
        "KB-526 · Diagnose endpoint failure",
        [
            "Capture device model, asset tag, symptoms, and recent changes.",
            "Run power, storage, memory, driver, and peripheral checks.",
            "Protect user data before repair, replacement, or reimage.",
        ],
    ),
    "Network & Connectivity": (
        "KB-631 · Isolate network path failure",
        [
            "Test link, IP configuration, DNS, route, and target reachability.",
            "Compare wired, wireless, VPN, and location-specific behavior.",
            "Record packet or resolver evidence before changing configuration.",
        ],
    ),
    "Security & Compliance": (
        "KB-745 · Contain and investigate security signals",
        [
            "Preserve evidence and establish affected identities and assets.",
            "Contain using the approved playbook without destroying artifacts.",
            "Escalate to the security owner and document chain of custody.",
        ],
    ),
    "Software & Applications": (
        "KB-852 · Troubleshoot application errors",
        [
            "Reproduce the exact user path and capture correlation details.",
            "Compare version, configuration, permissions, and dependencies.",
            "Validate the fix with the original user workflow and telemetry.",
        ],
    ),
}


@dataclass
class ModelBundle:
    category_model: Pipeline
    priority_model: Pipeline
    metrics: dict
    data_hash: str


def _load_rows() -> list[dict]:
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _dataset_hash() -> str:
    return hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()[:12]


def _pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=8000, sublinear_tf=True)),
            (
                "classifier",
                LogisticRegression(C=4.0, class_weight="balanced", max_iter=1200, random_state=42),
            ),
        ]
    )


def train(force: bool = False) -> ModelBundle:
    data_hash = _dataset_hash()
    if ARTIFACT_PATH.exists() and not force:
        bundle = joblib.load(ARTIFACT_PATH)
        if bundle.data_hash == data_hash:
            return bundle

    rows = _load_rows()
    text = [f"{row['subject']} {row['description']} affected users {row['affected_users']}" for row in rows]
    categories = [row["category"] for row in rows]
    priorities = [row["priority"] for row in rows]
    indices = list(range(len(rows)))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=0.25,
        random_state=42,
        stratify=[f"{c}|{p}" for c, p in zip(categories, priorities, strict=True)],
    )
    x_train = [text[i] for i in train_idx]
    x_test = [text[i] for i in test_idx]

    category_model = _pipeline().fit(x_train, [categories[i] for i in train_idx])
    priority_model = _pipeline().fit(x_train, [priorities[i] for i in train_idx])
    category_pred = category_model.predict(x_test)
    priority_pred = priority_model.predict(x_test)
    metrics = {
        "dataset_rows": len(rows),
        "holdout_rows": len(test_idx),
        "category_accuracy": round(
            float(accuracy_score([categories[i] for i in test_idx], category_pred)), 3
        ),
        "category_macro_f1": round(
            float(f1_score([categories[i] for i in test_idx], category_pred, average="macro")), 3
        ),
        "priority_accuracy": round(
            float(accuracy_score([priorities[i] for i in test_idx], priority_pred)), 3
        ),
        "priority_macro_f1": round(
            float(f1_score([priorities[i] for i in test_idx], priority_pred, average="macro")), 3
        ),
        "category_report": classification_report(
            [categories[i] for i in test_idx], category_pred, output_dict=True, zero_division=0
        ),
        "priority_report": classification_report(
            [priorities[i] for i in test_idx], priority_pred, output_dict=True, zero_division=0
        ),
    }
    bundle = ModelBundle(category_model, priority_model, metrics, data_hash)
    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(bundle, ARTIFACT_PATH)
    return bundle


def _alternatives(model: Pipeline, text: str, limit: int = 3) -> list[dict]:
    probabilities = model.predict_proba([text])[0]
    classes = model.named_steps["classifier"].classes_
    ranked = np.argsort(probabilities)[::-1][:limit]
    return [{"label": str(classes[i]), "confidence": round(float(probabilities[i]), 3)} for i in ranked]


def _rationale_terms(model: Pipeline, text: str, label: str, limit: int = 6) -> list[str]:
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    vector = vectorizer.transform([text])
    class_index = list(classifier.classes_).index(label)
    contributions = vector.multiply(classifier.coef_[class_index]).toarray()[0]
    features = vectorizer.get_feature_names_out()
    ranked = np.argsort(contributions)[::-1]
    return [str(features[i]) for i in ranked if contributions[i] > 0][:limit]


def predict(bundle: ModelBundle, payload: dict, ticket_id: str) -> dict:
    text = (
        f"{payload['subject']} {payload['description']} affected users {payload['affected_users']} "
        f"business service {payload['business_service']}"
    )
    category_alternatives = _alternatives(bundle.category_model, text)
    priority_alternatives = _alternatives(bundle.priority_model, text)
    category = category_alternatives[0]["label"]
    priority = priority_alternatives[0]["label"]
    category_confidence = category_alternatives[0]["confidence"]
    priority_confidence = priority_alternatives[0]["confidence"]
    article, actions = KNOWLEDGE[category]
    human_review = category_confidence < 0.64 or priority_confidence < 0.56 or priority == "P1"
    return {
        "ticket_id": ticket_id,
        "category": category,
        "category_confidence": category_confidence,
        "priority": priority,
        "priority_confidence": priority_confidence,
        "assignment_group": ASSIGNMENT_GROUPS[category],
        "sla_target_minutes": SLA_MINUTES[priority],
        "needs_human_review": human_review,
        "rationale_terms": _rationale_terms(bundle.category_model, text, category),
        "category_alternatives": category_alternatives,
        "priority_alternatives": priority_alternatives,
        "recommended_actions": actions,
        "knowledge_article": article,
        "summary": (
            f"Route to {ASSIGNMENT_GROUPS[category]} as {priority}; "
            f"{'human validation required' if human_review else 'eligible for assisted routing'}."
        ),
    }
