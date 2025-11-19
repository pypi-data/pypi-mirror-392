"""Interact module for unified API calls."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import requests

from .utils.errors import map_api_error
from .utils.types import InteractionResponse, build_interaction_response

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]


class InteractClient:
    """Client wrapper for the `/api/v1/interact` endpoint."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
        dry_run: bool = False,
    ) -> None:
        self._base_url = api_url.rstrip("/")
        self._session = session or requests.Session()
        self._header_provider = header_provider
        self._dry_run = dry_run

    def query(
        self,
        query: str,
        *,
        application_agent_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        context_id: Optional[str] = None,
        mode: str = "sync",
        stream: bool = False,
        extras: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> InteractionResponse:
        """Execute a synchronous interaction request."""

        payload = self._build_payload(
            query=query,
            application_agent_id=application_agent_id,
            intent_id=intent_id,
            context_id=context_id,
            mode=mode,
            stream=stream,
            extras=extras,
        )

        response = self._execute(payload, timeout=timeout)
        data = response.get("data") or {}
        meta = response.get("meta") or {}
        return build_interaction_response(data, meta)

    def async_query(
        self,
        query: str,
        *,
        application_agent_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        context_id: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """Start an asynchronous interaction and return a request identifier.

        The returned ``request_id`` can be consumed via :class:`RequestsClient`
        helpers such as :meth:`RequestsClient.wait`.
        """

        payload = self._build_payload(
            query=query,
            application_agent_id=application_agent_id,
            intent_id=intent_id,
            context_id=context_id,
            mode="async",
            stream=False,
            extras=extras,
        )
        response = self._execute(payload, timeout=timeout)
        request_id = (
            (response.get("data") or {}).get("request_id")
            or (response.get("meta") or {}).get("request_id")
            or response.get("request_id")
        )
        if not request_id:
            raise map_api_error(500, {"error": {"message": "Backend response is missing request_id"}})
        return str(request_id)

    def stream(self, *_: Any, **__: Any) -> InteractionResponse:
        """Stream the interaction response back to the caller."""

        raise NotImplementedError("Streaming interactions are not yet supported.")

    def _build_payload(
        self,
        *,
        query: str,
        application_agent_id: Optional[str],
        intent_id: Optional[str],
        context_id: Optional[str],
        mode: str,
        stream: bool,
        extras: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"query": query, "mode": mode, "stream": stream}
        if application_agent_id:
            payload["application_agent_id"] = application_agent_id
        if intent_id:
            payload["intent_id"] = intent_id
        if context_id:
            payload["context_id"] = context_id
        if self._dry_run:
            payload["dry_run"] = True
        if extras:
            payload.update(extras)
        return payload

    def _execute(self, payload: Dict[str, Any], timeout: Optional[float]) -> Dict[str, Any]:
        url = f"{self._base_url}/api/v1/interact"
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=self._header_provider(),
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise map_api_error(500, {"error": {"message": str(exc)}}) from exc

        return self._parse_response(response)

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise map_api_error(response.status_code, {"error": {"message": "Invalid JSON response"}}) from exc

        if response.status_code >= 400 or payload.get("status") != "ok":
            raise map_api_error(response.status_code, payload)

        return payload
