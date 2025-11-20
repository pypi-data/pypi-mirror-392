"""Access tokens module implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import AccessToken


class AccessTokensClient(BaseApiClient):
    """Manage rotating access tokens for the current account."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def list(self, *, timeout: Optional[float] = None) -> List[AccessToken]:
        """Return all active access tokens."""

        payload = self._request("GET", "/api/v1/access-tokens", timeout=timeout)
        data = self._extract_data(payload)
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
        payload = self._request(
            "POST", "/api/v1/access-tokens", json=body or None, timeout=timeout
        )
        data: Dict[str, Any] = self._extract_data(payload)
        return AccessToken.parse_obj(data)

    def revoke(self, token_id: str, *, timeout: Optional[float] = None) -> None:
        """Revoke an existing access token."""

        self._request(
            "DELETE", f"/api/v1/access-tokens/{token_id}", timeout=timeout, expect_json=False
        )
