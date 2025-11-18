from __future__ import annotations

from typing import cast

from daplug_s3.types import (
    AdapterConfig,
    DownloadKwargs,
    GetKwargs,
    JSONArray,
    JSONObject,
    JSONScalar,
    JSONValue,
    ListDirFilesKwargs,
    ListDirSubfoldersKwargs,
    MultipartUploadKwargs,
    PresignedPostKwargs,
    PresignedReadKwargs,
    PublishMetadata,
    PutKwargs,
    RenameKwargs,
    StreamUploadKwargs,
)


def test_adapter_config_typeddict_defaults() -> None:
    config: AdapterConfig = {
        "bucket": "bucket",
        "aws_access_key_id": "key",
        "aws_secret_access_key": "secret",
        "region": "us-east-1",
    }
    assert config["bucket"] == "bucket"


def test_json_aliases_support_nested_structures() -> None:
    nested: JSONValue = cast(
        JSONObject,
        {
            "name": cast(JSONScalar, "example"),
            "tags": cast(JSONArray, ["a", "b"]),
        },
    )
    assert nested["name"] == "example"


def test_kwargs_typeddicts_accept_expected_keys() -> None:
    put_args: PutKwargs = {"s3_path": "key", "data": b"data"}
    stream_args: StreamUploadKwargs = {"s3_path": "key", "data": b"data"}
    get_args: GetKwargs = {"s3_path": "key", "decode": False}
    download_args: DownloadKwargs = {"s3_path": "key", "download_path": "/tmp/file"}
    multipart_args: MultipartUploadKwargs = {"s3_path": "key", "chunks": [b"chunk"]}
    presigned_read: PresignedReadKwargs = {"s3_path": "key"}
    presigned_post: PresignedPostKwargs = {"s3_path": "key"}
    list_dirs: ListDirSubfoldersKwargs = {"dir_name": "dir/"}
    list_files: ListDirFilesKwargs = {"dir_name": "dir/"}
    rename_args: RenameKwargs = {"old_file_name": "old", "new_file_name": "new"}
    publish_data: PublishMetadata = {"presigned_url": "https://example"}

    assert put_args["data"] == b"data"
    assert stream_args["s3_path"] == "key"
    assert get_args["decode"] is False
    assert download_args["download_path"].startswith("/tmp")
    assert multipart_args["chunks"] == [b"chunk"]
    assert presigned_read["s3_path"] == "key"
    assert presigned_post["s3_path"] == "key"
    assert list_dirs["dir_name"] == "dir/"
    assert list_files["dir_name"] == "dir/"
    assert rename_args["new_file_name"] == "new"
    assert publish_data["presigned_url"].startswith("https://")
