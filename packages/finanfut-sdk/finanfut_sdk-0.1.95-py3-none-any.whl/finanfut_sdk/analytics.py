"""Analytics and developer logs module."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

import requests

from ._base import BaseApiClient, HeaderProvider

JsonDict = Dict[str, Any]


class AnalyticsClient(BaseApiClient):
    """Access developer logs and request analytics."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def logs(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Return developer logs for the current application."""

        payload = self._request(
            "GET",
            "/api/v1/developer/logs",
            params=dict(filters or {}),
            timeout=timeout,
        )
        return self._coerce_list(payload.get("data"))

    def requests(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Return developer request diagnostics."""

        payload = self._request(
            "GET",
            "/api/v1/developer/requests",
            params=dict(filters or {}),
            timeout=timeout,
        )
        return self._coerce_list(payload.get("data"))

    def _coerce_list(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return [dict(item) for item in data]
        if isinstance(data, dict):
            return [dict(data)]
        return []
