from typing import Any

from .adapter import S3Adapter


def adapter(**kwargs: Any) -> S3Adapter:
    """Factory helper for creating a S3 adapter."""
    return S3Adapter(**kwargs)


__all__ = ["adapter", "S3Adapter"]
