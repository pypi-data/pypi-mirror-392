from __future__ import annotations

import json
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import pytest
from botocore.exceptions import ClientError


def test_put_serializes_json_and_publishes_presigned_url(s3_components, file_bytes):
    adapter = s3_components["adapter"]
    tracker = s3_components["publish_tracker"]
    payload = json.loads(file_bytes("sample.json").decode("utf-8"))

    adapter.put(s3_path="docs/doc.json", data=payload, json=True, public_read=True)
    saved = json.loads(adapter.client.get_object(Bucket=s3_components["bucket"], Key="docs/doc.json")["Body"].read())

    assert saved == payload
    assert "presigned_url" in tracker.last()["data"]


def test_create_uses_put_behavior(s3_components):
    adapter = s3_components["adapter"]

    adapter.create(s3_path="docs/create.txt", data="created", encode=True)
    result = adapter.client.get_object(Bucket=s3_components["bucket"], Key="docs/create.txt")["Body"].read().decode()

    assert result == "created"
    assert "presigned_url" in s3_components["publish_tracker"].last()["data"]


def test_upload_stream_handles_file_object(s3_components, file_bytes):
    adapter = s3_components["adapter"]
    data = file_bytes("sample.pdf")

    adapter.upload_stream(s3_path="docs/file.pdf", io=BytesIO(data))
    saved = adapter.client.get_object(Bucket=s3_components["bucket"], Key="docs/file.pdf")["Body"].read()

    assert saved == data
    assert s3_components["publish_tracker"].last() is not None


def test_upload_stream_accepts_raw_data(s3_components, file_bytes):
    adapter = s3_components["adapter"]
    data = file_bytes("sample.txt")

    adapter.upload_stream(s3_path="docs/file.txt", data=data)
    saved = adapter.client.get_object(Bucket=s3_components["bucket"], Key="docs/file.txt")["Body"].read()

    assert saved == data
    assert "presigned_url" in s3_components["publish_tracker"].last()["data"]


def test_get_returns_json_payload(s3_components, file_bytes):
    adapter = s3_components["adapter"]
    payload = json.loads(file_bytes("sample.json").decode())
    adapter.put(s3_path="docs/config.json", data=payload, json=True)

    result = adapter.get(s3_path="docs/config.json", json=True)

    assert result == payload


def test_get_without_decoding_returns_raw_response(s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="docs/raw.bin", Body=b"binary")

    response = adapter.get(s3_path="docs/raw.bin", decode=False)

    assert response["Body"].read() == b"binary"


def test_read_delegates_to_get(s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="docs/read.txt", Body=b"value")

    result = adapter.read(s3_path="docs/read.txt")

    assert result == "value"


def test_download_creates_nested_directories(tmp_path: Path, s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="files/report.txt", Body=b"report")
    destination = tmp_path / "nested" / "report.txt"

    path = adapter.download(s3_path="files/report.txt", download_path=str(destination))

    assert Path(path).read_text() == "report"
    assert destination.exists()


def test_multipart_upload_combines_chunks(s3_components, file_bytes):
    adapter = s3_components["adapter"]
    base = file_bytes("sample.csv")
    multiplier = (5 * 1024 * 1024) // len(base) + 1
    large_chunk = base * multiplier
    data = large_chunk * 2 + base
    chunks = [large_chunk, large_chunk, base]

    adapter.multipart_upload(s3_path="files/data.csv", chunks=chunks)
    saved = adapter.client.get_object(Bucket=s3_components["bucket"], Key="files/data.csv")["Body"].read()

    assert saved == data
    assert "presigned_url" in s3_components["publish_tracker"].last()["data"]


def test_create_public_url_includes_bucket(s3_components):
    adapter = s3_components["adapter"]

    url = adapter.create_public_url(s3_path="files/data.csv")

    assert s3_components["bucket"] in url


def test_create_presigned_read_url_contains_object_key(s3_components):
    adapter = s3_components["adapter"]

    url = adapter.create_presigned_read_url(s3_path="files/data.csv")

    assert "files/data.csv" in url


def test_create_presigned_post_url_returns_required_fields(s3_components):
    adapter = s3_components["adapter"]

    result = adapter.create_presigned_post_url(s3_path="uploads/item.txt", required_fields={"acl": "private"})

    assert "url" in result
    assert "fields" in result


def test_object_exist_handles_present_and_missing_keys(s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="files/exists.txt", Body=b"value")

    assert adapter.object_exist(s3_path="files/exists.txt") is True
    assert adapter.object_exist(s3_path="files/missing.txt") is False


def test_object_exist_propagates_unexpected_errors(s3_components, monkeypatch):
    adapter = s3_components["adapter"]

    def fake_object(_, __):
        class _Stub:
            def load(self):
                raise ClientError({"Error": {"Code": "500", "Message": "boom"}}, "HeadObject")

        return _Stub()

    monkeypatch.setattr(adapter.resource, "Object", fake_object)

    with pytest.raises(ClientError):
        adapter.object_exist(s3_path="files/error.txt")


def test_list_dir_subfolders_returns_prefixes(s3_components):
    adapter = s3_components["adapter"]
    client = adapter.client
    bucket = s3_components["bucket"]
    client.put_object(Bucket=bucket, Key="reports/2023/a.txt", Body=b"a")
    client.put_object(Bucket=bucket, Key="reports/2024/b.txt", Body=b"b")
    client.put_object(Bucket=bucket, Key="other/file.txt", Body=b"c")

    prefixes = adapter.list_dir_subfolders(dir_name="reports/")

    assert set(prefixes) == {"reports/2023/", "reports/2024/"}


def test_list_dir_files_supports_date_filter(s3_components):
    adapter = s3_components["adapter"]
    client = adapter.client
    bucket = s3_components["bucket"]
    client.put_object(Bucket=bucket, Key="reports/old.txt", Body=b"old")
    client.put_object(Bucket=bucket, Key="reports/new.txt", Body=b"new")
    cutoff = datetime.utcnow() + timedelta(days=1)

    keys = adapter.list_dir_files(dir_name="reports/", date=cutoff)

    assert keys == []


def test_list_dir_files_without_date_lists_all_objects(s3_components):
    adapter = s3_components["adapter"]
    client = adapter.client
    bucket = s3_components["bucket"]
    client.put_object(Bucket=bucket, Key="reports/one.txt", Body=b"1")
    client.put_object(Bucket=bucket, Key="reports/two.txt", Body=b"2")

    keys = adapter.list_dir_files(dir_name="reports/")

    assert set(keys) == {"reports/one.txt", "reports/two.txt"}


def test_rename_object_moves_content(s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="files/old.txt", Body=b"payload")

    adapter.rename_object(old_file_name="files/old.txt", new_file_name="files/new.txt")

    assert adapter.object_exist(s3_path="files/new.txt") is True
    assert adapter.object_exist(s3_path="files/old.txt") is False


def test_delete_removes_object(s3_components):
    adapter = s3_components["adapter"]
    adapter.client.put_object(Bucket=s3_components["bucket"], Key="files/delete.txt", Body=b"remove")

    adapter.delete(s3_path="files/delete.txt")

    assert adapter.object_exist(s3_path="files/delete.txt") is False
