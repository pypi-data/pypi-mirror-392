from __future__ import annotations

import types

import daplug_s3
from daplug_s3 import adapter


def test_adapter_factory_instantiates_configured_class(monkeypatch):
    captured = {}

    class DummyAdapter:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(daplug_s3, "S3Adapter", DummyAdapter)

    instance = adapter(endpoint="http://example", bucket="demo")

    assert isinstance(instance, DummyAdapter)
    assert captured == {"endpoint": "http://example", "bucket": "demo"}


def test_module_exports_expected_symbols():
    exported = set(daplug_s3.__all__)

    assert {"adapter", "S3Adapter"}.issubset(exported)
