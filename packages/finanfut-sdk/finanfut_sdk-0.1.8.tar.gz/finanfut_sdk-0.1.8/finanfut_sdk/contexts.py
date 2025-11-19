"""Contexts module implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, Union

import requests

from .utils.errors import map_api_error
from .utils.types import ContextDocument, ContextSession

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]
JsonDict = Dict[str, Any]


class ContextsClient:
    """Manage documents and sessions for context injection."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        self._base_url = api_url.rstrip("/")
        self._session = session or requests.Session()
        self._header_provider = header_provider

    def upload_document(
        self,
        file_path: Union[str, Path],
        *,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> ContextDocument:
        """Upload a new context document."""

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Context document not found: {path}")

        url = f"{self._base_url}/api/v1/contexts"
        headers = dict(self._header_provider())
        headers.pop("Content-Type", None)

        with path.open("rb") as file_handle:
            files = {
                "file": (
                    path.name,
                    file_handle,
                    content_type or "application/octet-stream",
                )
            }
            data = {
                key: "" if value is None else str(value)
                for key, value in (metadata or {}).items()
            }
            try:
                response = self._session.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=timeout,
                )
            except requests.RequestException as exc:  # pragma: no cover - network failure
                raise map_api_error(500, {"error": {"message": str(exc)}}) from exc

        payload = self._parse_response(response)
        data: JsonDict = payload.get("data") or payload
        return ContextDocument.parse_obj(data)

    def create_session(
        self,
        context_ids: Iterable[str],
        *,
        metadata: Optional[Dict[str, Any]] = None,
        extras: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ContextSession:
        """Create a new context session."""

        body: JsonDict = {"context_ids": list(context_ids)}
        if metadata:
            body["metadata"] = metadata
        if extras:
            body.update(extras)

        payload = self._request(
            "POST", "/api/v1/contexts/sessions", json=body, timeout=timeout
        )
        data: JsonDict = payload.get("data") or payload
        return ContextSession.parse_obj(data)

    def get(
        self,
        resource_id: str,
        *,
        resource_type: str = "document",
        timeout: Optional[float] = None,
    ) -> Union[ContextDocument, ContextSession]:
        """Retrieve a context document or session by identifier."""

        if resource_type not in {"document", "session"}:
            raise ValueError("resource_type must be 'document' or 'session'")

        path = (
            f"/api/v1/contexts/{resource_id}"
            if resource_type == "document"
            else f"/api/v1/contexts/sessions/{resource_id}"
        )
        payload = self._request("GET", path, timeout=timeout)
        data: JsonDict = payload.get("data") or payload

        if resource_type == "session" or "session_id" in data:
            return ContextSession.parse_obj(data)
        return ContextDocument.parse_obj(data)

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        json: Optional[JsonDict] = None,
    ) -> JsonDict:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._header_provider(),
                json=json,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise map_api_error(500, {"error": {"message": str(exc)}}) from exc

        return self._parse_response(response)

    def _parse_response(self, response: requests.Response) -> JsonDict:
        try:
            payload = response.json()
        except ValueError as exc:
            raise map_api_error(
                response.status_code, {"error": {"message": "Invalid JSON response"}}
            ) from exc

        status = payload.get("status")
        if response.status_code >= 400 or (status and status != "ok"):
            raise map_api_error(response.status_code, payload)

        return payload
