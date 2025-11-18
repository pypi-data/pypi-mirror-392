# 🪣 daplug-s3 (da•plug)

> **Schema-Driven S3 Normalization & Event Publishing for Python**

[![CircleCI](https://circleci.com/gh/dual/daplug-s3.svg?style=shield)](https://circleci.com/gh/dual/daplug-s3)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dual_daplug-s3&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dual_daplug-s3)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=dual_daplug-s3&metric=coverage)](https://sonarcloud.io/summary/new_code?id=dual_daplug-s3)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![PyPI package](https://img.shields.io/pypi/v/daplug-s3?color=blue&label=pypi%20package)](https://pypi.org/project/daplug-s3/)
[![License](https://img.shields.io/badge/license-apache%202.0-blue)](LICENSE)
[![Contributions](https://img.shields.io/badge/contributions-welcome-blue)](https://github.com/paulcruse3/daplug-s3/issues)

`daplug-s3` is an adapter that wraps `boto3` S3 primitives with schema-friendly helpers, SNS publishing, and convenience utilities for streaming, multipart uploads, and presigned URL generation.

Need deeper operational context? See [`.agents/.AGENTS.md`](.agents/.AGENTS.md) for the full consumer guide and [`.agents/CODEX.md`](.agents/CODEX.md) for contributor workflow expectations.

---

## ✨ Highlights

- **Schema-aware writes** – Convert Python dictionaries into JSON payloads automatically.
- **Event-driven** – Every write publishes presigned URLs via the `daplug_core` publisher so downstream services can react in real time.
- **Complete S3 toolkit** – Simple helpers for CRUD, streaming uploads, multipart chunking, directory listings, and rename/delete patterns.
- **Local-first** – Works seamlessly with LocalStack using the `endpoint` parameter.

---

## 📦 Installation

```bash
pip install daplug-s3
# or with Pipenv
pipenv install daplug-s3
```

The library targets Python **3.9+**.

---

## 🚀 Quick Start

```python
from daplug_s3 import adapter

s3 = adapter(
    endpoint="https://s3.us-east-1.amazonaws.com",  # optional override
    bucket="my-team-bucket",
    aws_access_key_id="AKIA...",
    aws_secret_access_key="secret",
    region="us-east-1",
    sns_arn="arn:aws:sns:us-east-1:123456789012:my-topic",
    sns_endpoint="https://sns.us-east-1.amazonaws.com",
)
```

### Adapter Configuration Arguments

| Kwarg                   | Type                       | Required | Description                                                  |
|-------------------------|----------------------------|----------|--------------------------------------------------------------|
| `endpoint`              | `str,None`                 | No       | Custom S3/LocalStack endpoint. Leave `None` for AWS default. |
| `bucket`                | `str`                      | Yes      | Default bucket applied to every request.                     |
| `aws_access_key_id`     | `str`                      | Yes      | IAM access key.                                              |
| `aws_secret_access_key` | `str`                      | Yes      | IAM secret key.                                              |
| `region`                | `str`                      | Yes      | AWS region name.                                             |
| `sns_arn`               | `str`                      | No       | SNS topic ARN used by `BaseAdapter.publish`.                 |
| `sns_endpoint`          | `str`                      | No       | SNS endpoint override (LocalStack).                          |
| `sns_attributes`        | `dict[str,int,float,bool]` | No       | Default SNS message attributes.                              |

All public methods below accept keyword arguments only.

---

## 🧰 API Reference & Examples

### `put(**kwargs)` (alias: `create`)

Store data in S3 with optional JSON encoding.

```python
payload = {"type": "invoice", "id": 256}
s3.put(s3_path="docs/invoice-256.json", data=payload, json=True)
```

| Kwarg         | Type                   | Required | Default | Description                     |
|---------------|------------------------|----------|---------|---------------------------------|
| `s3_path`     | `str`                  | Yes      | —       | Object key.                     |
| `data`        | `bytes \| str \| dict` | Yes      | —       | Content to write.               |
| `json`        | `bool`                 | No       | `False` | Encode via `jsonpickle`.        |
| `encode`      | `bool`                 | No       | `True`  | Convert strings to UTF-8 bytes. |
| `public_read` | `bool`                 | No       | `False` | Applies `public-read` ACL.      |

Always triggers `BaseAdapter.publish` with a presigned URL payload.

---

### `upload_stream(**kwargs)`

Upload streamed or buffered data.

```python
from pathlib import Path
with Path("brochure.pdf").open("rb") as fh:
    s3.upload_stream(s3_path="docs/brochure.pdf", io=fh, public_read=True)
```

| Kwarg | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `s3_path` | `str` | Yes | — | Object key. |
| `io` | binary file object | One of | — | File-like object to stream from. |
| `data` | `bytes` | One of | — | Raw bytes used when `io` missing. |
| `threshold` | `int` | No | `10000` | Multipart threshold for uploads. |
| `concurrency` | `int` | No | `4` | Parallel worker count. |
| `public_read` | `bool` | No | `False` | Public ACL toggle. |

Either `io` or `data` must be supplied.

---

### `get(**kwargs)` (alias: `read`)

Retrieve and optionally decode objects.

```python
config = s3.get(s3_path="docs/invoice-256.json", json=True)
```

| Kwarg | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `s3_path` | `str` | Yes | — | Object key. |
| `json` | `bool` | No | `False` | Decode JSON via `jsonpickle`. |
| `decode` | `bool` | No | `True` | When `False`, returns raw boto3 response. |

`read` simply calls `get`.

---

### `download(**kwargs)`

Save S3 content locally.

```python
target = s3.download(s3_path="reports/weekly.csv", download_path="/tmp/weekly.csv")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Remote key. |
| `download_path` | `str` | Yes | Destination path; directories are created automatically. |

Returns the `download_path` string.

---

### `multipart_upload(**kwargs)`

Manual chunk uploads.

```python
chunks = [b"chunk-1", b"chunk-2", b"chunk-3"]
s3.multipart_upload(s3_path="large/data.bin", chunks=chunks)
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Target key. |
| `chunks` | `list[bytes]` | Yes | Ordered byte chunks uploaded sequentially. |

Publishes a presigned URL when complete.

---

### `create_public_url(**kwargs)`

Generate unsigned URLs for public objects.

```python
public_url = s3.create_public_url(s3_path="docs/brochure.pdf")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Object key. |

Only works for objects uploaded with `public_read=True`.

---

### `create_presigned_read_url(**kwargs)`

Time-limited access.

```python
signed_url = s3.create_presigned_read_url(s3_path="docs/invoice-256.json", expiration=900)
```

| Kwarg | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `s3_path` | `str` | Yes | — | Object key. |
| `expiration` | `int` | No | `3600` | Seconds before URL expires. |

---

### `create_presigned_post_url(**kwargs)`

Generate POST policies for browser uploads.

```python
post_config = s3.create_presigned_post_url(
    s3_path="uploads/raw.txt",
    required_fields={"acl": "private"},
    required_conditions=[["content-length-range", 0, 1048576]],
    expiration=600,
)
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Destination key. |
| `required_fields` | `dict[str, str]` | No | Pre-populated form fields. |
| `required_conditions` | `list[list[str]]` | No | Additional policy conditions. |
| `expiration` | `int` | No (`3600`) | Policy lifetime (seconds). |

---

### `object_exist(**kwargs)`

Check for object existence.

```python
if not s3.object_exist(s3_path="docs/invoice-999.json"):
    raise LookupError("missing doc")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Object key. |

Returns `True` when the object exists, `False` on 404, otherwise raises `ClientError`.

---

### `list_dir_subfolders(**kwargs)`

```python
folders = s3.list_dir_subfolders(dir_name="reports/")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `dir_name` | `str` | Yes | Prefix ending with `/`. |

Returns prefixes for child folders.

---

### `list_dir_files(**kwargs)`

```python
recent = s3.list_dir_files(dir_name="reports/", date=datetime.utcnow())
```

| Kwarg | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `dir_name` | `str` | Yes | — | Prefix to list. |
| `date` | `datetime` | No | `None` | Only return objects newer than this timestamp. |

Outputs a list of object keys.

---

### `rename_object(**kwargs)`

Copy + delete convenience.

```python
s3.rename_object(old_file_name="logs/old.txt", new_file_name="logs/new.txt")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `old_file_name` | `str` | Yes | Existing key. |
| `new_file_name` | `str` | Yes | New key. |

---

### `delete(**kwargs)`

Remove an object.

```python
s3.delete(s3_path="archives/data.bin")
```

| Kwarg | Type | Required | Description |
| --- | --- | --- | --- |
| `s3_path` | `str` | Yes | Key to delete. |

Returns the boto3 `delete_object` response.

---

## 🧪 Local Development & Testing

```bash
pipenv install --dev

# lint & type check
pipenv run lint
pipenv run type-check

# unit tests (moto-backed)
pipenv run test

# integration tests (LocalStack S3 via docker-compose)
pipenv run integrations
```

Set `S3_ENDPOINT=http://localhost:4566` plus fake AWS credentials when using LocalStack manually.

---

## 📚 Additional Resources

- Consumer-facing playbook: [`.agents/.AGENTS.md`](.agents/.AGENTS.md)
- Contributor guide & automation notes: [`.agents/CODEX.md`](.agents/CODEX.md)

---

## 🤝 Contributing

Issues and pull requests are welcome! Please run the full quality gate before opening a PR:

```bash
pipenv run lint
pipenv run type-check
pipenv run test
pipenv run integrations
```

---

## 📄 License

Apache License 2.0 – see [LICENSE](LICENSE) for details.

---

> Built to keep S3 integrations predictable, event-driven, and schema-friendly. EOF
