"""Access tokens module implementation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import requests

from .utils.errors import map_api_error
from .utils.types import AccessToken

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]


class AccessTokensClient:
    """Manage rotating access tokens for the current account."""

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

    def list(self, *, timeout: Optional[float] = None) -> List[AccessToken]:
        """Return all active access tokens."""

        payload = self._request("GET", "/api/v1/access-tokens", timeout=timeout)
        data = payload.get("data")
        if isinstance(data, list):
            return [AccessToken.parse_obj(item) for item in data]
        return []

    def create(
        self,
        description: Optional[str] = None,
        *,
        timeout: Optional[float] = None,
    ) -> AccessToken:
        """Create and return a new access token descriptor."""

        body: Dict[str, Any] = {}
        if description:
            body["description"] = description
        payload = self._request("POST", "/api/v1/access-tokens", json=body or None, timeout=timeout)
        data: Dict[str, Any] = payload.get("data") or payload
        return AccessToken.parse_obj(data)

    def revoke(self, token_id: str, *, timeout: Optional[float] = None) -> None:
        """Revoke an existing access token."""

        self._request("DELETE", f"/api/v1/access-tokens/{token_id}", timeout=timeout)

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
        except requests.RequestException as exc:  # pragma: no cover
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
