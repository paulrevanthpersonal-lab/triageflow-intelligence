# Interview Guide

## 60-second explanation

TriageFlow Intelligence is a modern reconstruction of an intelligent help-desk classification project I completed during my B.Tech. It converts unstructured ticket language into category, priority, assignment-group, and knowledge recommendations. I used two explainable TF-IDF and logistic-regression pipelines, exposed them through FastAPI, and designed a human-review policy for critical or uncertain predictions. The repository also includes a deterministic synthetic dataset, holdout evaluation, feedback persistence, responsive operator UI, tests, CI, and a model card.

## Design questions

**Why two models?** Category and operational urgency have different signals and different error costs, so separate models make their metrics and thresholds easier to govern.

**Why not use a large language model?** A linear model is fast, inexpensive, reproducible, and explainable for a constrained taxonomy. An LLM could assist summarization later, but it should not hide routing evidence.

**How do you prevent harmful automation?** P1 predictions and low-confidence results require human validation. The interface shows confidence, alternatives, influential terms, and recommended actions rather than directly changing production systems.

**What would production require?** Approved historical data, data minimization, SSO/RBAC, calibrated probabilities, model registry, drift baselines, queue integrations, PostgreSQL, observability, security testing, and controlled retraining.

## Demonstration path

1. Open Command Center and explain the decision lifecycle.
2. Classify the VPN example and inspect confidence and rationale.
3. Open Review Queue to show human-control boundaries.
4. Open Model Observability and explain the holdout metrics.
5. Close with the Model Card and known limitations.
