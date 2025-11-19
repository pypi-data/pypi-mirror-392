"""Tests for contexts client scaffolding."""

import pytest

from finanfut_sdk.contexts import ContextsClient
from finanfut_sdk.utils.types import ContextDocument


def test_context_upload_not_implemented():
    client = ContextsClient()
    with pytest.raises(NotImplementedError):
        client.upload_document(ContextDocument(name="doc", content_type="text/plain"))
