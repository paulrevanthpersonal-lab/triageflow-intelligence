# Model Card

## Model details

- **Name:** TriageFlow category and priority classifiers
- **Version:** 1.0.0
- **Model family:** TF-IDF n-grams with multinomial logistic regression
- **Tasks:** eight-class service category prediction and four-class operational priority prediction
- **Training:** deterministic seed, stratified 75/25 split, class-balanced loss

## Intended use

Decision support for privacy-reviewed internal IT help-desk tickets: suggested category, assignment group, priority, SLA target, and relevant knowledge article.

## Prohibited use

- Autonomous closure or remediation
- Employee ranking, performance evaluation, or disciplinary decisions
- Emergency, medical, safety, or security dispatch without trained human review
- Processing passwords, access tokens, health data, or unapproved personal information

## Data

The repository includes 384 deterministic synthetic tickets balanced across eight categories and four priorities. The examples approximate help-desk language but do not contain actual employee or customer records.

## Evaluation

`/api/metrics` exposes the holdout accuracy, macro F1, per-class report, dataset size, and immutable dataset hash. CI requires both category and priority macro F1 to remain at or above 0.80.

## Human oversight

P1 results always require review. Category confidence below 0.64 or priority confidence below 0.56 also requires review. Thresholds are demonstration policy values and require calibration against representative organizational data before production use.

## Limitations

- Synthetic language is cleaner and less diverse than real ticket text.
- Confidence is a model probability, not a correctness guarantee.
- Priority needs trusted business-service and asset-criticality context.
- English-only data does not support multilingual service desks.
- Feedback is stored but does not automatically retrain the model.
