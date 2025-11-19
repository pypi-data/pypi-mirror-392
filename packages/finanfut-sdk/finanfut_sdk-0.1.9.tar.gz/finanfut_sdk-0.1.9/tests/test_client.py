"""Tests for FinanFutClient scaffolding."""

from finanfut_sdk.client import FinanFutClient


def test_client_dataclass_fields():
    client = FinanFutClient(api_key="k", application_id="app", api_url="https://api")
    assert client.api_key == "k"
    assert client.application_id == "app"
    assert client.api_url == "https://api"
