from __future__ import annotations

import json
from io import BytesIO
from urllib.request import urlopen

import pytest
from botocore.exceptions import ClientError


@pytest.mark.integration
def test_put_and_get_json_round_trip(integration_adapter, file_bytes):
    payload = json.loads(file_bytes("sample.json").decode())
    path = "integration/docs/config.json"

    integration_adapter.put(s3_path=path, data=payload, json=True)
    result = integration_adapter.get(s3_path=path, json=True)

    assert result["title"] == payload["title"]


@pytest.mark.integration
def test_upload_stream_and_download_preserves_binary(integration_adapter, file_bytes, tmp_path):
    data = file_bytes("sample.pdf")
    path = "integration/files/brochure.pdf"
    integration_adapter.upload_stream(s3_path=path, io=BytesIO(data))

    download_path = tmp_path / "brochure.pdf"
    integration_adapter.download(s3_path=path, download_path=str(download_path))

    assert download_path.read_bytes() == data


@pytest.mark.integration
def test_multipart_upload_then_delete(integration_adapter, file_bytes):
    base = file_bytes("sample.csv")
    multiplier = (5 * 1024 * 1024) // len(base) + 1
    large_chunk = base * multiplier
    data = large_chunk + base
    chunks = [large_chunk, base]
    path = "integration/uploads/data.csv"

    integration_adapter.multipart_upload(s3_path=path, chunks=chunks)
    retrieved = integration_adapter.get(s3_path=path)
    integration_adapter.delete(s3_path=path)

    assert retrieved.endswith("name\n1,Ada\n2,Bob\n3,Cam\n")


@pytest.mark.integration
def test_presigned_read_url_allows_direct_access(integration_adapter, file_bytes):
    path = "integration/files/sample.txt"
    data = file_bytes("sample.txt")
    integration_adapter.put(s3_path=path, data=data.decode(), encode=True)

    url = integration_adapter.create_presigned_read_url(s3_path=path, expiration=60)
    with urlopen(url) as response:
        body = response.read()

    assert body == data


@pytest.mark.integration
def test_get_missing_object_raises_client_error(integration_adapter):
    with pytest.raises(ClientError):
        integration_adapter.get(s3_path="integration/missing/file.txt")
