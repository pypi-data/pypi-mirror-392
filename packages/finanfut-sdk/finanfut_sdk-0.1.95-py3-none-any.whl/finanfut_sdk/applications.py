"""Applications module implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import Application


class ApplicationsClient(BaseApiClient):
    """Manage applications linked to the account."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def list(self, *, timeout: Optional[float] = None) -> List[Application]:
        """List available applications for the API key."""

        payload = self._request("GET", "/api/v1/applications", timeout=timeout)
        data = self._extract_data(payload)
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
        data: Dict[str, Any] = self._extract_data(payload)
        return Application.parse_obj(data)
