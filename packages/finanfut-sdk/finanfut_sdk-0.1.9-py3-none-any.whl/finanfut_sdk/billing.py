"""Billing module implementation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional

import requests

from .utils.errors import map_api_error
from .utils.types import BillingPlan, BillingUsage, TransactionRecord

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]
JsonDict = Dict[str, Any]


class BillingClient:
    """Inspect plans, usage metrics, and billing transactions."""

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

    def get_plan(self, *, timeout: Optional[float] = None) -> BillingPlan:
        """Return the current billing plan descriptor."""

        payload = self._request("GET", "/api/v1/billing/plans", timeout=timeout)
        data: JsonDict = payload.get("data") or payload
        return BillingPlan.parse_obj(data)

    def get_usage(
        self,
        *,
        period: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> BillingUsage:
        """Return the billing usage for the requested period."""

        params: Dict[str, Any] = {}
        if period:
            params["period"] = period
        payload = self._request(
            "GET", "/api/v1/billing/usage", params=params, timeout=timeout
        )
        data: JsonDict = payload.get("data") or payload
        return BillingUsage.parse_obj(data)

    def list_transactions(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> List[TransactionRecord]:
        """Return historical transaction records."""

        payload = self._request(
            "GET",
            "/api/v1/billing/transactions",
            params=dict(filters or {}),
            timeout=timeout,
        )
        data = payload.get("data")
        if isinstance(data, list):
            return [TransactionRecord.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [TransactionRecord.parse_obj(data)]
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
