"""Billing module implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import BillingPlan, BillingUsage, TransactionRecord
JsonDict = Dict[str, Any]


class BillingClient(BaseApiClient):
    """Inspect plans, usage metrics, and billing transactions."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def get_plan(self, *, timeout: Optional[float] = None) -> BillingPlan:
        """Return the current billing plan descriptor."""

        payload = self._request("GET", "/api/v1/billing/plans", timeout=timeout)
        data: JsonDict = self._extract_data(payload)
        plans = self._coerce_plans(data)
        if plans:
            return plans[0]
        return BillingPlan.parse_obj(data)

    def get_plans(self, *, timeout: Optional[float] = None) -> List[BillingPlan]:
        """Return all billing plans visible to the account."""

        payload = self._request("GET", "/api/v1/billing/plans", timeout=timeout)
        data: JsonDict = self._extract_data(payload)
        return self._coerce_plans(data)

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
        data: JsonDict = self._extract_data(payload)
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
        data = self._extract_data(payload)
        if isinstance(data, list):
            return [TransactionRecord.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [TransactionRecord.parse_obj(data)]
        return []

    def _coerce_plans(self, data: Any) -> List[BillingPlan]:
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            items = data["items"]
        elif isinstance(data, dict):
            items = [data]
        else:
            items = []
        return [BillingPlan.parse_obj(item) for item in items]
