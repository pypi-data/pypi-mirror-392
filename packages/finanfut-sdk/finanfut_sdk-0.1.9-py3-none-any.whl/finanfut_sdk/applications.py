"""Applications module implementation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import requests

from .utils.errors import map_api_error
from .utils.types import Application

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]


class ApplicationsClient:
    """Manage applications linked to the account."""

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

    def list(self, *, timeout: Optional[float] = None) -> List[Application]:
        """List available applications for the API key."""

        payload = self._request("GET", "/api/v1/applications", timeout=timeout)
        data = payload.get("data")
        if isinstance(data, list):
            return [Application.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [Application.parse_obj(data)]
        return []

    def get(self, application_id: str, *, timeout: Optional[float] = None) -> Application:
        """Fetch a single application by identifier."""

        payload = self._request(
            "GET", f"/api/v1/applications/{application_id}", timeout=timeout
        )
        data: Dict[str, Any] = payload.get("data") or payload
        return Application.parse_obj(data)

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
