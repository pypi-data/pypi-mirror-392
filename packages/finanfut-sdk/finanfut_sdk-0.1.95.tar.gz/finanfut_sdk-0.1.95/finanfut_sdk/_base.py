"""Shared HTTP utilities for API clients."""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional

import requests

from .utils.errors import map_api_error

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]


class BaseApiClient:
    """Base class wiring the HTTP session, headers and error handling."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session],
        header_provider: HeaderProvider,
    ) -> None:
        self._base_url = api_url.rstrip("/")
        self._session = session or requests.Session()
        self._header_provider = header_provider

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        expect_json: bool = True,
    ) -> Any:
        url = f"{self._base_url}{path}"
        resolved_headers = dict(self._header_provider(headers))
        if files:
            # Multipart requests must not send an explicit JSON content-type header.
            resolved_headers.pop("Content-Type", None)
        filtered_params = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = self._session.request(
                method,
                url,
                params=filtered_params or None,
                json=json,
                data=data,
                files=files,
                headers=resolved_headers,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise map_api_error(500, {"error": {"message": str(exc)}}) from exc

        if not expect_json:
            if response.status_code >= 400:
                raise map_api_error(response.status_code, self._error_payload(response))
            return {}

        if response.status_code == 204 or not response.content:
            if response.status_code >= 400:
                raise map_api_error(response.status_code, self._error_payload(response))
            return {}

        try:
            payload = response.json()
        except ValueError as exc:
            raise map_api_error(
                response.status_code,
                {"error": {"message": "Invalid JSON response"}},
            ) from exc

        if response.status_code >= 400:
            raise map_api_error(response.status_code, payload)

        if isinstance(payload, dict):
            status_flag = payload.get("status")
            if isinstance(status_flag, str):
                normalized = status_flag.lower()
                if normalized in {"error", "failed"}:
                    raise map_api_error(response.status_code, payload)

        return payload

    @staticmethod
    def _error_payload(response: requests.Response) -> Dict[str, Any]:
        message = response.text or f"Request failed with status code {response.status_code}"
        return {"error": {"message": message}}

    @staticmethod
    def _extract_data(payload: Any) -> Any:
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload
