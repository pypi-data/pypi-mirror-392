"""Shared fixtures for unit tests."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterator

import pytest
from moto import mock_aws

from daplug_s3.adapter import BaseAdapter, S3Adapter
from tests.unit.mocks.base_adapter import PublishTracker


@pytest.fixture(scope="session")
def mocks_dir() -> Path:
    return Path(__file__).parent / "mocks"


@pytest.fixture
def file_bytes(mocks_dir: Path) -> Callable[[str], bytes]:
    def _reader(name: str) -> bytes:
        return (mocks_dir / name).read_bytes()

    return _reader


@pytest.fixture
def publish_tracker(monkeypatch: pytest.MonkeyPatch) -> PublishTracker:
    tracker = PublishTracker()
    monkeypatch.setattr(BaseAdapter, "publish", tracker)
    return tracker


@pytest.fixture
def s3_components(publish_tracker: PublishTracker) -> Iterator[Dict[str, object]]:
    with mock_aws():
        settings = {
            "endpoint": None,
            "bucket": "unit-bucket",
            "aws_access_key_id": "mock",
            "aws_secret_access_key": "mock",
            "region": "us-east-1",
        }
        adapter = S3Adapter(**settings)
        adapter.client.create_bucket(Bucket=settings["bucket"])
        yield {
            "adapter": adapter,
            "client": adapter.client,
            "resource": adapter.resource,
            "bucket": settings["bucket"],
            "publish_tracker": publish_tracker,
        }
