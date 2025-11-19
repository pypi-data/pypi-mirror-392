"""Tests for billing client scaffolding."""

import pytest

from finanfut_sdk.billing import BillingClient


def test_billing_plan_not_implemented():
    client = BillingClient()
    with pytest.raises(NotImplementedError):
        client.get_plan()
