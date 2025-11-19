"""Tests for memory client scaffolding."""

import pytest

from finanfut_sdk.memory import MemoryClient


def test_memory_settings_accessor_not_implemented():
    client = MemoryClient()
    with pytest.raises(NotImplementedError):
        _ = client.settings
