"""Contexts module implementation."""

from __future__ import annotations

from typing import Any, List, Mapping, MutableMapping, Optional, Sequence, Union

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import (
    ContextDetail,
    ContextDocumentLink,
    ContextList,
    ContextSessionDetail,
    ContextSessionList,
    ContextSessionMessage,
)

DocumentReference = Union[str, Mapping[str, Any], ContextDocumentLink]


class ContextsClient(BaseApiClient):
    """Manage persistent contexts that aggregate document links."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        timeout: Optional[float] = None,
    ) -> ContextList:
        """Return paginated contexts for the authenticated application."""

        payload = self._request(
            "GET",
            "/api/v1/contexts",
            params={"offset": offset, "limit": limit},
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return ContextList.parse_obj(data)

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        documents: Optional[Sequence[DocumentReference]] = None,
        timeout: Optional[float] = None,
    ) -> ContextDetail:
        """Create a new context with optional linked documents."""

        body: MutableMapping[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        if metadata is not None:
            body["metadata"] = dict(metadata)
        if documents is not None:
            body["documents"] = self._normalize_documents(documents)

        payload = self._request("POST", "/api/v1/contexts", json=body, timeout=timeout)
        data = self._extract_data(payload)
        return ContextDetail.parse_obj(data)

    def get(self, context_id: Union[str, ContextDetail], *, timeout: Optional[float] = None) -> ContextDetail:
        """Retrieve a single context."""

        identifier = context_id.id if isinstance(context_id, ContextDetail) else context_id
        payload = self._request("GET", f"/api/v1/contexts/{identifier}", timeout=timeout)
        data = self._extract_data(payload)
        return ContextDetail.parse_obj(data)

    def update(
        self,
        context_id: Union[str, ContextDetail],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        documents: Optional[Sequence[DocumentReference]] = None,
        timeout: Optional[float] = None,
    ) -> ContextDetail:
        """Update the context metadata or its associated documents."""

        identifier = context_id.id if isinstance(context_id, ContextDetail) else context_id
        body: MutableMapping[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        if metadata is not None:
            body["metadata"] = dict(metadata)
        if documents is not None:
            body["documents"] = self._normalize_documents(documents)

        payload = self._request(
            "PATCH",
            f"/api/v1/contexts/{identifier}",
            json=body,
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return ContextDetail.parse_obj(data)

    def delete(self, context_id: Union[str, ContextDetail], *, timeout: Optional[float] = None) -> None:
        """Remove a context and its document associations."""

        identifier = context_id.id if isinstance(context_id, ContextDetail) else context_id
        self._request(
            "DELETE",
            f"/api/v1/contexts/{identifier}",
            timeout=timeout,
            expect_json=False,
        )

    def _normalize_documents(self, documents: Sequence[DocumentReference]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for entry in documents:
            if isinstance(entry, ContextDocumentLink):
                normalized.append(
                    {
                        "document_id": str(entry.document_id),
                        "metadata": dict(entry.metadata),
                    }
                )
                continue
            if isinstance(entry, Mapping):
                document_id = entry.get("document_id") or entry.get("id")
                metadata = entry.get("metadata") or entry.get("metadata_")
                normalized.append(
                    {
                        "document_id": str(document_id),
                        "metadata": dict(metadata or {}),
                    }
                )
                continue
            normalized.append({"document_id": str(entry), "metadata": {}})
        return normalized


class ContextSessionsClient(BaseApiClient):
    """Manage runtime sessions that reuse existing contexts."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        timeout: Optional[float] = None,
    ) -> ContextSessionList:
        payload = self._request(
            "GET",
            "/api/v1/context-sessions",
            params={"offset": offset, "limit": limit},
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return ContextSessionList.parse_obj(data)

    def create(
        self,
        *,
        name: str,
        context_id: Optional[str] = None,
        status: str = "active",
        metadata: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ContextSessionDetail:
        body: MutableMapping[str, Any] = {"name": name, "status": status}
        if context_id is not None:
            body["context_id"] = context_id
        if metadata is not None:
            body["metadata"] = dict(metadata)
        payload = self._request("POST", "/api/v1/context-sessions", json=body, timeout=timeout)
        data = self._extract_data(payload)
        return ContextSessionDetail.parse_obj(data)

    def get(self, session_id: str, *, timeout: Optional[float] = None) -> ContextSessionDetail:
        payload = self._request(
            "GET", f"/api/v1/context-sessions/{session_id}", timeout=timeout
        )
        data = self._extract_data(payload)
        return ContextSessionDetail.parse_obj(data)

    def append_message(
        self,
        session_id: str,
        *,
        agent_name: str,
        intent: Optional[str] = None,
        role: str = "assistant",
        query: Optional[str] = None,
        answer: Optional[str] = None,
        tokens_used: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        context_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ContextSessionMessage:
        body: MutableMapping[str, Any] = {
            "agent_name": agent_name,
            "role": role,
            "tokens_used": tokens_used,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
        if intent is not None:
            body["intent"] = intent
        if query is not None:
            body["query"] = query
        if answer is not None:
            body["answer"] = answer
        if context_id is not None:
            body["context_id"] = context_id
        if metadata is not None:
            body["metadata"] = dict(metadata)

        payload = self._request(
            "POST",
            f"/api/v1/context-sessions/{session_id}/messages",
            json=body,
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return ContextSessionMessage.parse_obj(data)

    def delete(self, session_id: str, *, timeout: Optional[float] = None) -> None:
        self._request(
            "DELETE",
            f"/api/v1/context-sessions/{session_id}",
            timeout=timeout,
            expect_json=False,
        )
