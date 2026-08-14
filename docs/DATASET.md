# Dataset and Data Statement

## Purpose

`data/tickets.csv` is a deterministic synthetic dataset created solely to make the training and evaluation workflow executable without exposing real support records.

## Schema

| Field | Meaning |
|---|---|
| `ticket_id` | Synthetic stable identifier |
| `subject` | Short ticket summary |
| `description` | Impact, symptom, urgency, and context |
| `affected_users` | Synthetic impact count |
| `category` | One of eight service categories |
| `priority` | P1, P2, P3, or P4 |
| `assignment_group` | Recommended resolver team |
| `resolution` | Synthetic example recovery outcome |

## Reproducibility

Run `python scripts/generate_dataset.py`. Seed `42` produces 384 rows: 48 per category and 96 per priority. The application records the first 12 characters of the dataset SHA-256 hash with its evaluation metrics.

## Privacy and bias boundary

No real TCS, university, employee, or customer ticket content is included. The template distribution is intentionally balanced and therefore does not represent a real organization's issue prevalence, writing patterns, location mix, or language mix.
