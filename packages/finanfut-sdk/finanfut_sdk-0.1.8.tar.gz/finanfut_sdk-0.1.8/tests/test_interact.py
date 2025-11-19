"""Tests for interact client scaffolding."""

import pytest

from finanfut_sdk.interact import InteractClient


def test_interact_query_not_implemented():
    client = InteractClient()
    with pytest.raises(NotImplementedError):
        client.query({})
