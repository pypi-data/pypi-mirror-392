"""Integration fixtures for exercising the S3 adapter against LocalStack."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable, Dict

import boto3
import pytest

from daplug_core.base_adapter import BaseAdapter
from daplug_s3.adapter import S3Adapter


AWS_REGION = "us-east-1"
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "test")


def _wait_for_s3(endpoint: str, attempts: int = 30, delay: float = 1.0) -> None:
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        region_name=AWS_REGION,
    )
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            client.list_buckets()
            return
        except Exception as exc:  # pragma: no cover - best-effort wait
            last_error = exc
            time.sleep(delay)
    raise RuntimeError("Timed out waiting for LocalStack S3") from last_error


@pytest.fixture(scope="session")
def integration_bucket() -> str:
    return "daplug-s3-integration"


@pytest.fixture(scope="session")
def integration_endpoint() -> str:
    return os.getenv("S3_ENDPOINT", "http://localhost:4566")


@pytest.fixture(autouse=True)
def _suppress_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    def _noop(self, db_data, **kwargs):
        return None

    monkeypatch.setattr(BaseAdapter, "publish", _noop, raising=False)


@pytest.fixture(scope="session")
def integration_adapter(integration_endpoint: str, integration_bucket: str) -> S3Adapter:
    _wait_for_s3(integration_endpoint)
    adapter = S3Adapter(
        endpoint=integration_endpoint,
        bucket=integration_bucket,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        region=AWS_REGION,
    )
    try:
        adapter.client.create_bucket(Bucket=integration_bucket)
    except adapter.client.exceptions.BucketAlreadyOwnedByYou:
        pass
    return adapter


@pytest.fixture(autouse=True)
def clear_bucket(integration_adapter: S3Adapter, integration_bucket: str) -> None:
    yield
    client = integration_adapter.client
    response = client.list_objects_v2(Bucket=integration_bucket)
    contents = response.get("Contents", [])
    if contents:
        client.delete_objects(
            Bucket=integration_bucket,
            Delete={"Objects": [{"Key": obj["Key"]} for obj in contents]},
        )


@pytest.fixture(scope="session")
def mocks_dir() -> Path:
    return Path(__file__).parent / "mocks"


@pytest.fixture
def file_bytes(mocks_dir: Path) -> Callable[[str], bytes]:
    def _reader(name: str) -> bytes:
        return (mocks_dir / name).read_bytes()

    return _reader
