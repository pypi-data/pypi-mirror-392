"""Typed models used across the FinanFut SDK."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage summary for an interaction."""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class ActionResult(BaseModel):
    """Represents an action returned by FinanFut agents."""

    name: str
    payload: Dict[str, Any]


class InteractionResponse(BaseModel):
    """High-level response returned by `/api/v1/interact`."""

    answer: Any
    actions: List[ActionResult] = Field(default_factory=list)
    tokens: Optional[TokenUsage] = None
    sandbox: bool = False
    request_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


def build_interaction_response(
    data: Mapping[str, Any], meta: Optional[Mapping[str, Any]] = None
) -> InteractionResponse:
    """Create an :class:`InteractionResponse` from backend payloads."""

    safe_meta = dict(meta or {})
    token_payload = (
        data.get("tokens")
        or data.get("token_usage")
        or safe_meta.get("token_usage")
        or safe_meta.get("tokens")
    )
    request_identifier = (
        data.get("request_id")
        or data.get("requestId")
        or safe_meta.get("request_id")
        or safe_meta.get("requestId")
    )
    return InteractionResponse.parse_obj(
        {
            "answer": data.get("answer"),
            "actions": data.get("actions") or [],
            "tokens": token_payload,
            "sandbox": bool(data.get("sandbox", safe_meta.get("sandbox", False))),
            "request_id": request_identifier,
            "meta": safe_meta,
        }
    )


class MemoryRecord(BaseModel):
    """Represents a memory entry."""

    record_id: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemorySettings(BaseModel):
    """Configuration for memory storage."""

    enabled: bool
    retention_days: Optional[int] = None
    max_records: Optional[int] = None


class BillingUsage(BaseModel):
    """Current usage metrics."""

    period: str
    tokens_used: int
    cost: float


class BillingPlan(BaseModel):
    """Generic billing plan descriptor."""

    plan_id: Optional[str] = None
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransactionRecord(BaseModel):
    """Billing transaction entry."""

    transaction_id: str
    amount: float
    currency: str
    created_at: str
    description: Optional[str] = None


class ContextDocument(BaseModel):
    """Document uploaded for context usage."""

    document_id: Optional[str] = None
    name: str
    content_type: str
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None


class ContextSession(BaseModel):
    """Session referencing uploaded documents."""

    session_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Agent(BaseModel):
    """Agent metadata."""

    agent_id: str
    name: str
    description: Optional[str] = None
    model: Optional[str] = None


class Intent(BaseModel):
    """Intent metadata."""

    intent_id: str
    name: str
    description: Optional[str] = None


class Application(BaseModel):
    """Application metadata."""

    application_id: str
    name: str
    status: str


class AccessToken(BaseModel):
    """Metadata describing a rotating access token."""

    token_id: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None
