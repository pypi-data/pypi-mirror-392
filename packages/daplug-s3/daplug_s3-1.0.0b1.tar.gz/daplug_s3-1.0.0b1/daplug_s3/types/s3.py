from __future__ import annotations

from datetime import datetime
from typing import BinaryIO, Mapping, Sequence, TypedDict, Union

JSONScalar = Union[str, int, float, bool, None]
JSONArray = Sequence["JSONValue"]
JSONObject = Mapping[str, "JSONValue"]
JSONValue = Union[JSONScalar, JSONArray, JSONObject]


class AdapterConfig(TypedDict, total=False):
    endpoint: str | None
    bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
    sns_arn: str
    sns_endpoint: str
    sns_attributes: Mapping[str, JSONScalar]


class PutKwargs(TypedDict, total=False):
    s3_path: str
    data: Union[JSONValue, bytes, str]
    public_read: bool
    json: bool
    encode: bool
    publish: bool


class StreamUploadKwargs(TypedDict, total=False):
    s3_path: str
    io: BinaryIO
    data: bytes
    threshold: int
    concurrency: int
    public_read: bool
    publish: bool


class GetKwargs(TypedDict, total=False):
    s3_path: str
    json: bool
    decode: bool


class DownloadKwargs(TypedDict, total=False):
    s3_path: str
    download_path: str


class MultipartUploadKwargs(TypedDict, total=False):
    s3_path: str
    chunks: Sequence[bytes]
    publish: bool


class PresignedReadKwargs(TypedDict, total=False):
    s3_path: str
    expiration: int


class PresignedPostKwargs(TypedDict, total=False):
    s3_path: str
    required_fields: Mapping[str, str]
    required_conditions: Sequence[Mapping[str, str]]
    expiration: int


class ListDirSubfoldersKwargs(TypedDict, total=False):
    dir_name: str


class ListDirFilesKwargs(TypedDict, total=False):
    dir_name: str
    date: datetime


class RenameKwargs(TypedDict, total=False):
    old_file_name: str
    new_file_name: str


class PublishMetadata(TypedDict):
    action: str
    presigned_url: str
