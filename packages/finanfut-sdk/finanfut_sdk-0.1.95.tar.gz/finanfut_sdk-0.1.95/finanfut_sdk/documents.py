"""Documents client implementation."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import (
    DocumentAnswer,
    DocumentDetail,
    DocumentFile,
    DocumentProcessingResponse,
    DocumentRunsResponse,
    DocumentType,
    DocumentTypeDetail,
    ParsedDocumentResponse,
)

Payload = Dict[str, Any]


class DocumentsClient(BaseApiClient):
    """Manage the document QA pipeline and processing endpoints."""

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
        application_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> List[DocumentFile]:
        """Return the latest documents for the current application."""

        params: Dict[str, Any] = {}
        if application_id is not None:
            params["application_id"] = application_id
        if status is not None:
            params["document_status"] = status
        if limit is not None:
            params["limit"] = limit
        payload = self._request("GET", "/api/v1/documents", params=params, timeout=timeout)
        data = self._extract_data(payload)
        if isinstance(data, list):
            return [DocumentFile.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [DocumentFile.parse_obj(data)]
        return []

    def upload(
        self,
        *,
        file_path: Optional[Union[str, Path]] = None,
        content: Optional[Union[str, bytes]] = None,
        text: Optional[str] = None,
        document_id: Optional[str] = None,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        auto_classify: bool = True,
        classification_dry_run: bool = False,
        timeout: Optional[float] = None,
    ) -> DocumentDetail:
        """Upload a document either from disk, raw bytes, or pasted text."""

        payload = self._build_upload_payload(
            file_path=file_path,
            content=content,
            text=text,
            document_id=document_id,
            file_name=file_name,
            mime_type=mime_type,
        )
        params = {
            "auto_classify": str(bool(auto_classify)).lower(),
            "classification_dry_run": str(bool(classification_dry_run)).lower(),
        }
        response = self._request(
            "POST",
            "/api/v1/agents/document-qa/files",
            params=params,
            json=payload,
            timeout=timeout,
        )
        data = self._extract_data(response)
        return DocumentDetail.parse_obj(data)

    def update(self, document_id: str, **kwargs: Any) -> DocumentDetail:
        """Convenience wrapper to update an existing document."""

        return self.upload(document_id=document_id, **kwargs)

    def get(
        self,
        document_id: str,
        *,
        include_binary: bool = False,
        timeout: Optional[float] = None,
    ) -> DocumentDetail:
        payload = self._request(
            "GET",
            f"/api/v1/agents/document-qa/files/{document_id}",
            params={"include_binary": str(bool(include_binary)).lower()},
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return DocumentDetail.parse_obj(data)

    def delete(self, document_id: str, *, timeout: Optional[float] = None) -> None:
        self._request(
            "DELETE",
            f"/api/v1/agents/document-qa/files/{document_id}",
            timeout=timeout,
            expect_json=False,
        )

    def ask(
        self,
        document_id: str,
        question: str,
        *,
        timeout: Optional[float] = None,
    ) -> DocumentAnswer:
        payload = self._request(
            "POST",
            "/api/v1/agents/document-qa/query",
            json={"document_id": document_id, "question": question},
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return DocumentAnswer.parse_obj(data)

    def process(
        self,
        document_id: str,
        *,
        reprocess: bool = False,
        document_type_override: Optional[str] = None,
        dry_run: bool = False,
        timeout: Optional[float] = None,
    ) -> DocumentProcessingResponse:
        body: Payload = {"document_id": document_id, "reprocess": reprocess}
        if document_type_override is not None:
            body["document_type_override"] = document_type_override
        path = "/api/v1/documents/dry-run" if dry_run else "/api/v1/documents/process"
        payload = self._request("POST", path, json=body, timeout=timeout)
        data = self._extract_data(payload)
        return DocumentProcessingResponse.parse_obj(data)

    def list_processing_runs(
        self, document_id: str, *, timeout: Optional[float] = None
    ) -> DocumentRunsResponse:
        payload = self._request(
            "GET", f"/api/v1/documents/{document_id}/runs", timeout=timeout
        )
        data = self._extract_data(payload)
        return DocumentRunsResponse.parse_obj(data)

    def get_parsed(
        self, document_id: str, *, timeout: Optional[float] = None
    ) -> ParsedDocumentResponse:
        payload = self._request(
            "GET", f"/api/v1/documents/{document_id}/parsed", timeout=timeout
        )
        data = self._extract_data(payload)
        return ParsedDocumentResponse.parse_obj(data)

    def list_types(self, *, timeout: Optional[float] = None) -> List[DocumentType]:
        payload = self._request(
            "GET", "/api/v1/documents/document-pipeline/types", timeout=timeout
        )
        data = self._extract_data(payload)
        items = (data.get("items") if isinstance(data, dict) else data) or []
        return [DocumentType.parse_obj(item) for item in items]

    def get_type(
        self, type_identifier: str, *, timeout: Optional[float] = None
    ) -> DocumentTypeDetail:
        payload = self._request(
            "GET",
            f"/api/v1/documents/document-pipeline/types/{type_identifier}",
            timeout=timeout,
        )
        data = self._extract_data(payload)
        return DocumentTypeDetail.parse_obj(data)

    def _build_upload_payload(
        self,
        *,
        file_path: Optional[Union[str, Path]],
        content: Optional[Union[str, bytes]],
        text: Optional[str],
        document_id: Optional[str],
        file_name: Optional[str],
        mime_type: Optional[str],
    ) -> Payload:
        payload: Payload = {}
        if document_id is not None:
            payload["id"] = document_id

        if file_path is not None:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {path}")
            payload["file_name"] = file_name or path.name
            payload["mime_type"] = mime_type or mimetypes.guess_type(path.name)[0]
            payload["content_base64"] = self._encode_bytes(path.read_bytes())
            return payload

        if content is not None:
            raw_bytes = content.encode("utf-8") if isinstance(content, str) else content
            payload["file_name"] = file_name or "document"
            if mime_type is not None:
                payload["mime_type"] = mime_type
            payload["content_base64"] = self._encode_bytes(raw_bytes)
            return payload

        if text is not None:
            if not text.strip():
                raise ValueError("text content cannot be empty")
            payload["file_name"] = file_name or "pasted-text.txt"
            payload["mime_type"] = mime_type or "text/plain"
            payload["text_content"] = text
            return payload

        raise ValueError("file_path, content, or text must be provided")

    @staticmethod
    def _encode_bytes(raw: bytes) -> str:
        if not raw:
            raise ValueError("The provided content is empty")
        return base64.b64encode(raw).decode("ascii")
