from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from caragent_worker.app import celery_app
from caragent_worker.tasks.health import worker_health


def test_celery_app_imports_with_expected_name() -> None:
    assert celery_app.main == "caragent_worker"
    assert celery_app.conf.broker_url == "redis://localhost:6379/0"


def test_worker_health_returns_static_status_payload() -> None:
    payload = worker_health.run()

    assert payload == {
        "status": "ok",
        "runtime_mode": "local",
        "queue": "redis",
        "external_calls": False,
    }


def test_worker_source_does_not_import_api_or_provider_modules() -> None:
    forbidden = (
        re.compile(r"\bimport\s+caragent_api\b"),
        re.compile(r"\bfrom\s+caragent_api\b"),
        re.compile(r"\bimport\s+fastapi\b", re.IGNORECASE),
        re.compile(r"\bfrom\s+fastapi\b", re.IGNORECASE),
        re.compile(r"\bopenai\s+import\b"),
        re.compile(r"\bfrom\s+openai\b"),
        re.compile(r"\bimport\s+openai\b"),
        re.compile(r"\bfal_client\b"),
        re.compile(r"\bbfl\b", re.IGNORECASE),
        re.compile(r"\bfrom\s+(fal|bfl)[\w.-]*\b", re.IGNORECASE),
        re.compile(r"\bimport\s+(fal|bfl)[\w.-]*\b", re.IGNORECASE),
    )

    violations = [
        f"{source_file}: {pattern.pattern}"
        for source_file in iter_worker_source_files()
        for pattern in forbidden
        if pattern.search(source_file.read_text(encoding="utf-8"))
    ]

    assert violations == []


def iter_worker_source_files() -> Iterable[Path]:
    return Path("src/caragent_worker").rglob("*.py")
