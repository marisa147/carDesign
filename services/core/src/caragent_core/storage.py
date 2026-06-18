from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import UUID

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": {".jpeg", ".jpg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024


class ObjectStorage(Protocol):
    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        pass


@dataclass(frozen=True)
class StoredObject:
    content: bytes
    content_type: str


class InMemoryObjectStorage:
    def __init__(self) -> None:
        self.objects: dict[str, StoredObject] = {}

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = StoredObject(content=content, content_type=content_type)


class FileObjectStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        del content_type
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def build_object_key(
    *,
    workspace_id: UUID,
    kind: str,
    record_id: UUID,
    filename: str,
) -> str:
    return f"workspaces/{workspace_id}/{kind}/{record_id}/{sanitize_filename(filename)}"


def sanitize_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return f"{slug or 'file'}{suffix}"


def validate_upload(
    *,
    content_type: str,
    byte_size: int,
    filename: str,
    max_upload_bytes: int = MAX_UPLOAD_BYTES,
) -> None:
    if byte_size <= 0:
        raise ValueError("Upload content is required")

    if byte_size > max_upload_bytes:
        raise ValueError(f"Upload exceeds {max_upload_bytes} bytes")

    allowed_extensions = SUPPORTED_IMAGE_TYPES.get(content_type)
    if allowed_extensions is None:
        raise ValueError(f"Unsupported upload content type: {content_type}")

    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise ValueError(f"Unsupported upload extension for {content_type}: {suffix}")
