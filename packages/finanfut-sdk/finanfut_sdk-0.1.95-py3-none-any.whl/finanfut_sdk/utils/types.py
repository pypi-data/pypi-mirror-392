"""Typed models used across the FinanFut SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, Field, UUID4


class FinanFutModel(BaseModel):
    """Base model enforcing Pydantic v1 configuration across the SDK."""

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class TokenUsage(FinanFutModel):
    """Token usage summary for an interaction."""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class ActionResult(FinanFutModel):
    """Represents an action returned by FinanFut agents."""

    name: str
    payload: Dict[str, Any]


class InteractionResponse(FinanFutModel):
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


class MemoryRecord(FinanFutModel):
    """Represents a memory entry."""

    record_id: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class MemorySettings(FinanFutModel):
    """Configuration for memory storage."""

    enabled: bool
    retention_days: Optional[int] = None
    max_records: Optional[int] = None


class BillingUsage(FinanFutModel):
    """Current usage metrics."""

    period: str
    tokens_used: int
    cost: float


class BillingPlan(FinanFutModel):
    """Generic billing plan descriptor."""

    plan_id: Optional[str] = None
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class TransactionRecord(FinanFutModel):
    """Billing transaction entry."""

    transaction_id: str
    amount: float
    currency: str
    created_at: str
    description: Optional[str] = None


class Agent(FinanFutModel):
    """Agent metadata."""

    agent_id: str
    name: str
    description: Optional[str] = None
    ai_model_id: Optional[str] = None


class Intent(FinanFutModel):
    """Intent metadata."""

    intent_id: str
    name: str
    description: Optional[str] = None


class Application(FinanFutModel):
    """Application metadata."""

    application_id: str
    name: str
    status: str


class AccessToken(FinanFutModel):
    """Metadata describing a rotating access token."""

    token_id: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None


class DocumentFile(FinanFutModel):
    """Metadata about an uploaded document."""

    id: UUID4
    file_name: str
    mime_type: Optional[str] = None
    status: str
    chunk_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    document_type_id: Optional[UUID4] = None
    document_type: Optional[str] = None
    document_type_label: Optional[str] = None
    document_type_version: Optional[int] = None
    document_type_strict_validation: Optional[bool] = None
    document_type_embedding_enabled: Optional[bool] = None
    document_type_chunking_strategy: Optional[Dict[str, Any]] = None
    latest_processing_id: Optional[UUID4] = None
    processing_summary: Optional[str] = None
    processing_confidence: Optional[float] = None
    processing_version: int = 0
    classification_metadata: Optional[Dict[str, Any]] = None


class DocumentDetail(DocumentFile):
    """Full document payload returned after upload or lookup."""

    text_content: str = ""
    error: Optional[str] = None
    content_base64: Optional[str] = Field(default=None, repr=False)


class DocumentAnswer(FinanFutModel):
    """Answer payload returned by the document QA endpoint."""

    answer: str
    request_id: Optional[UUID4] = None


class DocumentType(FinanFutModel):
    """Descriptor for a pipeline document type."""

    id: UUID4
    name: str
    label: Optional[str] = None
    description: Optional[str] = None
    expected_format: Optional[str] = None
    parse_strategy: Optional[str] = None
    output_contract: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    version: int = 1
    strict_validation: Optional[bool] = None
    embedding_enabled: Optional[bool] = None
    chunking_strategy: Dict[str, Any] = Field(default_factory=dict)
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DocumentTypeDetail(DocumentType):
    """Detailed descriptor for a document type."""


class ValidationReport(FinanFutModel):
    """Validation status after running the processing pipeline."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DeclarativeAction(FinanFutModel):
    """Action emitted by the pipeline for downstream automation."""

    id: UUID4
    processing_record_id: UUID4
    document_id: UUID4
    application_id: UUID4
    name: str
    handler: str
    endpoint: Optional[str] = None
    description: Optional[str] = None
    version: int
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    processed_by_agent_id: Optional[UUID4] = None
    processed_by_agent_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DocumentProcessingRecord(FinanFutModel):
    """One processing run executed for a document."""

    id: UUID4
    document_id: UUID4
    application_id: UUID4
    document_type_id: Optional[UUID4] = None
    document_type_version: Optional[int] = None
    status: str
    summary: Optional[str] = None
    confidence: Optional[float] = None
    version: int
    processing_version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    parsed_content: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processor_agent_id: Optional[UUID4] = None
    processor_agent_name: Optional[str] = None
    execution_time_ms: Optional[int] = None
    tokens_used: int = 0
    parser_version: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DocumentProcessingResponse(FinanFutModel):
    """Full payload returned after requesting document processing."""

    record: DocumentProcessingRecord
    parsed_content: Optional[Dict[str, Any]] = None
    validation: ValidationReport
    dry_run: bool = False
    action: Optional[DeclarativeAction] = None


class DocumentRunsResponse(FinanFutModel):
    """Historical processing runs."""

    runs: List[DocumentProcessingRecord] = Field(default_factory=list)


class ParsedDocumentResponse(FinanFutModel):
    """Latest parsed content and associated action."""

    record: Optional[DocumentProcessingRecord] = None
    action: Optional[DeclarativeAction] = None


class ContextDocumentLink(FinanFutModel):
    """Context document relationship metadata."""

    document_id: UUID4
    position: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContextSummary(FinanFutModel):
    """High-level summary returned when listing contexts."""

    id: UUID4
    application_id: UUID4
    name: str
    description: Optional[str] = None
    status: str
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    document_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContextDetail(ContextSummary):
    """Context detail including linked documents."""

    documents: List[ContextDocumentLink] = Field(
        default_factory=list,
        alias="document_links",
    )


class ContextList(FinanFutModel):
    """Paginated response returned by the contexts API."""

    items: List[ContextSummary] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class ContextSessionSummary(FinanFutModel):
    """Summary of a context session."""

    id: UUID4
    name: str
    status: str
    context_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContextSessionMessage(FinanFutModel):
    """Message captured inside a context session."""

    id: UUID4
    session_id: UUID4
    context_id: Optional[UUID4] = None
    agent_name: str
    intent: Optional[str] = None
    role: str
    query: Optional[str] = None
    answer: Optional[str] = None
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ContextSessionDetail(ContextSessionSummary):
    """Detailed session with metadata and messages."""

    metadata: Dict[str, Any] = Field(default_factory=dict)
    messages: List[ContextSessionMessage] = Field(default_factory=list)


class ContextSessionList(FinanFutModel):
    """Response returned when listing context sessions."""

    items: List[ContextSessionSummary] = Field(default_factory=list)
