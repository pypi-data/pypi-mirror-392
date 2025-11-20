"""Intents module implementation."""

from __future__ import annotations

from typing import Any, List, Optional

import requests

from ._base import BaseApiClient, HeaderProvider
from .utils.types import Intent


class IntentsClient(BaseApiClient):
    """Interact with available intents."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        super().__init__(api_url=api_url, session=session, header_provider=header_provider)

    def list(self, agent_id: str, *, timeout: Optional[float] = None) -> List[Intent]:
        """Return all intents registered for an agent."""

        path = f"/api/v1/agents/{agent_id}/intents"
        payload = self._request("GET", path, timeout=timeout)
        data = self._extract_data(payload)
        if isinstance(data, list):
            return [Intent.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [Intent.parse_obj(data)]
        return []
