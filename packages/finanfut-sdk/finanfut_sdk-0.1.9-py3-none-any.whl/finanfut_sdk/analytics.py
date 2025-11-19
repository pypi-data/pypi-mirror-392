"""Analytics and developer logs module."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional

import requests

from .utils.errors import map_api_error

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]
JsonDict = Dict[str, Any]


class AnalyticsClient:
    """Access developer logs and request analytics."""

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

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> JsonDict:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._header_provider(),
                params={k: v for k, v in (params or {}).items() if v is not None},
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise map_api_error(500, {"error": {"message": str(exc)}}) from exc

        try:
            payload: JsonDict = response.json()
        except ValueError as exc:
            raise map_api_error(
                response.status_code, {"error": {"message": "Invalid JSON response"}}
            ) from exc

        status = payload.get("status")
        if response.status_code >= 400 or (status and status != "ok"):
            raise map_api_error(response.status_code, payload)

        return payload
