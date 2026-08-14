from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "Access & Identity",
    "Cloud & Infrastructure",
    "Data & Database",
    "Email & Collaboration",
    "Hardware & Devices",
    "Network & Connectivity",
    "Security & Compliance",
    "Software & Applications",
]
Priority = Literal["P1", "P2", "P3", "P4"]


class TicketInput(BaseModel):
    subject: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=12, max_length=3000)
    requester: str = Field(default="Employee", min_length=2, max_length=80)
    affected_users: int = Field(default=1, ge=1, le=100000)
    business_service: str = Field(default="Corporate IT", min_length=2, max_length=100)


class Alternative(BaseModel):
    label: str
    confidence: float


class Prediction(BaseModel):
    ticket_id: str
    category: Category
    category_confidence: float
    priority: Priority
    priority_confidence: float
    assignment_group: str
    sla_target_minutes: int
    needs_human_review: bool
    rationale_terms: list[str]
    category_alternatives: list[Alternative]
    priority_alternatives: list[Alternative]
    recommended_actions: list[str]
    knowledge_article: str
    summary: str


class FeedbackInput(BaseModel):
    ticket_id: str = Field(min_length=6, max_length=32)
    accepted: bool
    corrected_category: Category | None = None
    corrected_priority: Priority | None = None
    note: str = Field(default="", max_length=500)


class BatchInput(BaseModel):
    tickets: list[TicketInput] = Field(min_length=1, max_length=25)
