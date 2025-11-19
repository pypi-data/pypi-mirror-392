"""Memory module implementation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Union

import requests

from .utils.errors import map_api_error
from .utils.types import MemoryRecord, MemorySettings

HeaderProvider = Callable[[Optional[Dict[str, str]]], Dict[str, str]]
Payload = Dict[str, Any]


class MemorySettingsClient:
    """Manage application-level memory settings."""

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

    def get(self, application_id: str, *, timeout: Optional[float] = None) -> MemorySettings:
        path = f"/api/v1/applications/{application_id}/memory"
        payload = self._request("GET", path, timeout=timeout)
        data: Payload = payload.get("data") or payload
        return MemorySettings.parse_obj(data)

    def update(
        self,
        application_id: str,
        settings: Union[MemorySettings, Mapping[str, Any]],
        *,
        timeout: Optional[float] = None,
    ) -> MemorySettings:
        path = f"/api/v1/applications/{application_id}/memory"
        body = self._coerce_payload(settings)
        payload = self._request("POST", path, json=body, timeout=timeout)
        data: Payload = payload.get("data") or payload
        return MemorySettings.parse_obj(data)

    def _coerce_payload(
        self, settings: Union[MemorySettings, Mapping[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(settings, MemorySettings):
            return settings.dict(exclude_none=True)
        return {k: v for k, v in dict(settings).items() if v is not None}

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        json: Optional[Payload] = None,
    ) -> Payload:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._header_provider(),
                json=json,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
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


class MemoryRecordsClient:
    """Manage memory records for each application agent."""

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

    def list(
        self,
        application_id: str,
        application_agent_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> List[MemoryRecord]:
        path = self._records_path(application_id, application_agent_id)
        payload = self._request("GET", path, timeout=timeout)
        data = payload.get("data")
        records_payload = data.get("records") if isinstance(data, dict) else data
        if isinstance(records_payload, list):
            return [MemoryRecord.parse_obj(item) for item in records_payload]
        if isinstance(records_payload, dict):
            return [MemoryRecord.parse_obj(records_payload)]
        return []

    def query(
        self,
        application_id: str,
        application_agent_id: str,
        query: str,
        *,
        timeout: Optional[float] = None,
    ) -> List[MemoryRecord]:
        path = f"{self._records_path(application_id, application_agent_id)}/query"
        payload = self._request("POST", path, json={"query": query}, timeout=timeout)
        data = payload.get("data")
        if isinstance(data, list):
            return [MemoryRecord.parse_obj(item) for item in data]
        if isinstance(data, dict):
            return [MemoryRecord.parse_obj(data)]
        return []

    def create(
        self,
        application_id: str,
        application_agent_id: str,
        record: Union[MemoryRecord, Mapping[str, Any]],
        *,
        timeout: Optional[float] = None,
    ) -> MemoryRecord:
        path = self._records_path(application_id, application_agent_id)
        body = self._coerce_payload(record)
        payload = self._request("POST", path, json=body, timeout=timeout)
        data: Payload = payload.get("data") or payload
        return MemoryRecord.parse_obj(data)

    def delete(
        self,
        application_id: str,
        application_agent_id: str,
        record_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> None:
        path = f"{self._records_path(application_id, application_agent_id)}/{record_id}"
        self._request("DELETE", path, timeout=timeout)

    def _records_path(self, application_id: str, application_agent_id: str) -> str:
        return f"/api/v1/applications/{application_id}/agents/{application_agent_id}/memory"

    def _coerce_payload(
        self, record: Union[MemoryRecord, Mapping[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(record, MemoryRecord):
            return record.dict(exclude_none=True)
        return {k: v for k, v in dict(record).items() if v is not None}

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        json: Optional[Payload] = None,
    ) -> Payload:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._header_provider(),
                json=json,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
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


class MemoryClient:
    """Entry point for memory operations."""

    def __init__(
        self,
        *,
        api_url: str,
        session: Optional[requests.Session] = None,
        header_provider: HeaderProvider,
    ) -> None:
        self._settings = MemorySettingsClient(
            api_url=api_url, session=session, header_provider=header_provider
        )
        self._records = MemoryRecordsClient(
            api_url=api_url, session=session, header_provider=header_provider
        )

    @property
    def settings(self) -> MemorySettingsClient:
        return self._settings

    @property
    def records(self) -> MemoryRecordsClient:
        return self._records
