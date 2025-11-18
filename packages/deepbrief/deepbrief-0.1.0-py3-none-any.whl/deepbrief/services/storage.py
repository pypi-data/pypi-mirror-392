import json
import os
from typing import Any

from dapr.clients import DaprClient

STORAGE_BINDING_NAME = os.getenv("STORAGE_BINDING_NAME", "bucketstore")


def _invoke_binding(
    operation: str,
    data: bytes = b"",
    metadata: dict[str, str] | None = None,
):
    if not STORAGE_BINDING_NAME:
        raise RuntimeError("STORAGE_BINDING_NAME is not configured")

    with DaprClient() as client:
        return client.invoke_binding(
            binding_name=STORAGE_BINDING_NAME,
            operation=operation,
            data=data,
            binding_metadata=metadata or {},
        )


def store_bytes(key: str, content: bytes, metadata: dict[str, str] | None = None):
    meta = {"key": key}
    if metadata:
        meta.update(metadata)
    _invoke_binding("create", data=content, metadata=meta)


def store_json(key: str, content: dict[str, Any], metadata: dict[str, str] | None = None):
    payload = json.dumps(content).encode("utf-8")
    store_bytes(key, payload, metadata)


def get_object(key: str) -> bytes:
    response = _invoke_binding("get", metadata={"key": key})
    return response.data


def delete_object(key: str):
    _invoke_binding("delete", metadata={"key": key})
