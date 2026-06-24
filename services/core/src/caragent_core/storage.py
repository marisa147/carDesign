from __future__ import annotations

import asyncio
import importlib
import json
import re
import struct
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, cast, runtime_checkable
from uuid import UUID

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": {".jpeg", ".jpg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_UPLOAD_PIXELS = 24_000_000
LOCAL_STORAGE_MODES = {"local", "development", "test"}


@runtime_checkable
class SecretValue(Protocol):
    def get_secret_value(self) -> str:
        pass


@runtime_checkable
class ReadableBody(Protocol):
    def read(self) -> bytes:
        pass


class S3Client(Protocol):
    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str) -> object:
        pass

    def get_object(self, *, Bucket: str, Key: str) -> Mapping[str, object]:
        pass

    def head_object(self, *, Bucket: str, Key: str) -> Mapping[str, object]:
        pass

    def delete_object(self, *, Bucket: str, Key: str) -> object:
        pass


class ObjectStorage(Protocol):
    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        pass

    async def get_object(self, key: str) -> StoredObject:
        pass

    async def head_object(self, key: str) -> StoredObjectMetadata:
        pass

    async def delete_object(self, key: str) -> None:
        pass


@dataclass(frozen=True)
class StoredObject:
    content: bytes
    content_type: str


@dataclass(frozen=True)
class StoredObjectMetadata:
    byte_size: int
    content_type: str


@dataclass(frozen=True, slots=True)
class StorageSettings:
    backend: Literal["file", "s3"] | None = None
    local_root: Path = Path(".runtime/object-storage")
    runtime_mode: str = "local"
    s3_access_key_id: str | None = None
    s3_bucket: str | None = None
    s3_endpoint_url: str | None = None
    s3_secret_access_key: str | None = None

    @classmethod
    def from_object(cls, settings: object) -> StorageSettings:
        local_root = Path(
            str(
                getattr(
                    settings,
                    "object_storage_local_root",
                    getattr(settings, "storage_local_root", ".runtime/object-storage"),
                ),
            ),
        )
        secret_value = getattr(settings, "s3_secret_access_key", None)
        if isinstance(secret_value, SecretValue):
            secret: str | None = secret_value.get_secret_value()
        elif secret_value is None:
            secret = None
        else:
            secret = str(secret_value)
        return cls(
            backend=getattr(settings, "object_storage_backend", None),
            local_root=local_root,
            runtime_mode=str(getattr(settings, "runtime_mode", "local")),
            s3_access_key_id=getattr(settings, "s3_access_key_id", None),
            s3_bucket=getattr(settings, "s3_bucket", None),
            s3_endpoint_url=getattr(settings, "s3_endpoint_url", None),
            s3_secret_access_key=secret,
        )


class S3ObjectStorage:
    def __init__(self, *, bucket: str, client: S3Client) -> None:
        self.bucket = bucket
        self.client = client

    @classmethod
    def from_settings(
        cls,
        settings: StorageSettings,
        *,
        client: S3Client | None = None,
    ) -> S3ObjectStorage:
        if not settings.s3_bucket:
            raise ValueError("S3_BUCKET is required for S3 object storage")
        if client is not None:
            return cls(bucket=settings.s3_bucket, client=client)

        try:
            boto3 = importlib.import_module("boto3")
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "boto3 is required for S3 object storage; install it in the runtime environment.",
            ) from error

        client_factory = cast(Callable[..., object], getattr(boto3, "client"))  # noqa: B009
        created_client = client_factory(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )
        return cls(bucket=settings.s3_bucket, client=cast(S3Client, created_client))

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )

    async def get_object(self, key: str) -> StoredObject:
        response = await asyncio.to_thread(
            self.client.get_object,
            Bucket=self.bucket,
            Key=key,
        )
        body = response.get("Body")
        if not isinstance(body, ReadableBody):
            raise RuntimeError("S3 get_object response missing readable Body")
        return StoredObject(
            content=body.read(),
            content_type=self._content_type_from_response(response),
        )

    async def head_object(self, key: str) -> StoredObjectMetadata:
        response = await asyncio.to_thread(
            self.client.head_object,
            Bucket=self.bucket,
            Key=key,
        )
        byte_size = response.get("ContentLength")
        return StoredObjectMetadata(
            byte_size=byte_size if isinstance(byte_size, int) else 0,
            content_type=self._content_type_from_response(response),
        )

    async def delete_object(self, key: str) -> None:
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket,
            Key=key,
        )

    @staticmethod
    def _content_type_from_response(response: Mapping[str, object]) -> str:
        content_type = response.get("ContentType")
        return content_type if isinstance(content_type, str) else "application/octet-stream"


class ObjectStorageFactory:
    @staticmethod
    def from_settings(
        settings: StorageSettings | object,
        *,
        s3_client: S3Client | None = None,
    ) -> ObjectStorage:
        storage_settings = (
            settings
            if isinstance(settings, StorageSettings)
            else StorageSettings.from_object(settings)
        )
        backend = storage_settings.backend
        if backend is None:
            backend = "file" if storage_settings.runtime_mode in LOCAL_STORAGE_MODES else "s3"

        if backend == "file":
            return FileObjectStorage(storage_settings.local_root)
        if backend == "s3":
            return S3ObjectStorage.from_settings(storage_settings, client=s3_client)
        raise ValueError(f"Unsupported object storage backend: {backend}")


class InMemoryObjectStorage:
    def __init__(self) -> None:
        self.objects: dict[str, StoredObject] = {}

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = StoredObject(content=content, content_type=content_type)

    async def get_object(self, key: str) -> StoredObject:
        try:
            return self.objects[key]
        except KeyError as error:
            raise FileNotFoundError(key) from error

    async def head_object(self, key: str) -> StoredObjectMetadata:
        stored = await self.get_object(key)
        return StoredObjectMetadata(
            byte_size=len(stored.content),
            content_type=stored.content_type,
        )

    async def delete_object(self, key: str) -> None:
        try:
            del self.objects[key]
        except KeyError as error:
            raise FileNotFoundError(key) from error


class FileObjectStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        target = self._target_for_key(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        self._metadata_target(target).write_text(
            json.dumps(
                {
                    "byte_size": len(content),
                    "content_type": content_type,
                },
                ensure_ascii=True,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    async def get_object(self, key: str) -> StoredObject:
        target = self._target_for_key(key)
        if not target.is_file():
            raise FileNotFoundError(key)
        metadata = await self.head_object(key)
        return StoredObject(
            content=target.read_bytes(),
            content_type=metadata.content_type,
        )

    async def head_object(self, key: str) -> StoredObjectMetadata:
        target = self._target_for_key(key)
        if not target.is_file():
            raise FileNotFoundError(key)
        content_type = "application/octet-stream"
        metadata_target = self._metadata_target(target)
        if metadata_target.is_file():
            try:
                metadata = json.loads(metadata_target.read_text(encoding="utf-8"))
                if isinstance(metadata.get("content_type"), str):
                    content_type = metadata["content_type"]
            except (OSError, ValueError, TypeError):
                content_type = "application/octet-stream"
        return StoredObjectMetadata(
            byte_size=target.stat().st_size,
            content_type=content_type,
        )

    async def delete_object(self, key: str) -> None:
        target = self._target_for_key(key)
        if not target.is_file():
            raise FileNotFoundError(key)
        target.unlink()
        metadata_target = self._metadata_target(target)
        if metadata_target.exists():
            metadata_target.unlink()

    def _target_for_key(self, key: str) -> Path:
        target = self.root / key
        root = self.root.resolve()
        resolved = target.resolve()
        if root != resolved and root not in resolved.parents:
            raise ValueError("Object key escapes storage root")
        return resolved

    @staticmethod
    def _metadata_target(target: Path) -> Path:
        return target.with_name(f"{target.name}.metadata.json")


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
    content: bytes | None = None,
    max_image_pixels: int = MAX_UPLOAD_PIXELS,
) -> None:
    normalized_content_type = _normalize_content_type(content_type)
    if byte_size <= 0:
        raise ValueError("Upload content is required")

    if byte_size > max_upload_bytes:
        raise ValueError(f"Upload exceeds {max_upload_bytes} bytes")

    allowed_extensions = SUPPORTED_IMAGE_TYPES.get(normalized_content_type)
    if allowed_extensions is None:
        raise ValueError(f"Unsupported upload content type: {content_type}")

    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise ValueError(f"Unsupported upload extension for {normalized_content_type}: {suffix}")

    if content is None:
        return
    if len(content) != byte_size:
        raise ValueError("Upload byte size does not match content")

    detected_type, width, height = _detect_image_upload(content)
    if detected_type != normalized_content_type:
        raise ValueError(
            "Upload bytes do not match declared content type: "
            f"{normalized_content_type}",
        )
    if width <= 0 or height <= 0:
        raise ValueError("Upload image dimensions are required")
    if width * height > max_image_pixels:
        raise ValueError(f"Upload image exceeds {max_image_pixels} pixels")


def _normalize_content_type(content_type: str) -> str:
    return content_type.split(";", 1)[0].strip().lower()


def _detect_image_upload(content: bytes) -> tuple[str, int, int]:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        width, height = _read_png_dimensions(content)
        return "image/png", width, height
    if content.startswith(b"\xff\xd8"):
        width, height = _read_jpeg_dimensions(content)
        return "image/jpeg", width, height
    if len(content) >= 16 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        width, height = _read_webp_dimensions(content)
        return "image/webp", width, height
    raise ValueError("Upload bytes do not match supported image magic")


def _read_png_dimensions(content: bytes) -> tuple[int, int]:
    if len(content) < 24 or content[12:16] != b"IHDR":
        raise ValueError("Upload PNG is missing a valid IHDR chunk")
    width, height = struct.unpack("!II", content[16:24])
    return width, height


def _read_jpeg_dimensions(content: bytes) -> tuple[int, int]:
    sof_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    index = 2
    while index < len(content) - 1:
        if content[index] != 0xFF:
            index += 1
            continue
        while index < len(content) and content[index] == 0xFF:
            index += 1
        if index >= len(content):
            break
        marker = content[index]
        index += 1
        if marker in {0x01, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9}:
            continue
        if index + 2 > len(content):
            break
        segment_length = int.from_bytes(content[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(content):
            break
        segment_start = index + 2
        if marker in sof_markers:
            if segment_start + 5 > len(content):
                break
            height = int.from_bytes(content[segment_start + 1 : segment_start + 3], "big")
            width = int.from_bytes(content[segment_start + 3 : segment_start + 5], "big")
            return width, height
        index += segment_length
    raise ValueError("Upload JPEG is missing image dimensions")


def _read_webp_dimensions(content: bytes) -> tuple[int, int]:
    chunk_type = content[12:16]
    if chunk_type == b"VP8X" and len(content) >= 30:
        width = int.from_bytes(content[24:27], "little") + 1
        height = int.from_bytes(content[27:30], "little") + 1
        return width, height
    if chunk_type == b"VP8L" and len(content) >= 25 and content[20] == 0x2F:
        bits = int.from_bytes(content[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return width, height
    if chunk_type == b"VP8 " and len(content) >= 30 and content[23:26] == b"\x9d\x01\x2a":
        width = int.from_bytes(content[26:28], "little") & 0x3FFF
        height = int.from_bytes(content[28:30], "little") & 0x3FFF
        return width, height
    raise ValueError("Upload WebP is missing image dimensions")
