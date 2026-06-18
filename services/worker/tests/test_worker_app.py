from __future__ import annotations

import importlib
import re
from collections.abc import Iterable
from pathlib import Path

import pytest

from caragent_worker.app import celery_app
from caragent_worker.config import get_settings
from caragent_worker.tasks.health import worker_health
from caragent_worker.tasks.jobs import generate_2d_concept_job


def test_celery_app_imports_with_expected_name() -> None:
    assert celery_app.main == "caragent_worker"
    assert celery_app.conf.broker_url == "redis://localhost:6379/0"
    assert celery_app.conf.include == [
        "caragent_worker.tasks.health",
        "caragent_worker.tasks.jobs",
    ]


def test_worker_health_returns_static_status_payload() -> None:
    payload = worker_health.run()

    assert payload == {
        "hosted_provider_configured": False,
        "provider_calls_enabled": False,
        "provider_default": "disabled",
        "provider_model": "local-concept-v1",
        "recommended_pool": "solo",
        "status": "ok",
        "runtime_mode": "local",
        "queue": "caragent.default",
        "task_name": "caragent_worker.generate_2d_concept_job",
        "worker_version": "0.1.0",
    }


def test_worker_health_reports_hosted_provider_presence_without_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "bfl")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "worker-bfl-secret")
    get_settings.cache_clear()

    try:
        payload = worker_health.run()
    finally:
        get_settings.cache_clear()

    assert payload["provider_default"] == "bfl"
    assert payload["provider_calls_enabled"] is True
    assert payload["hosted_provider_configured"] is True
    assert "worker-bfl-secret" not in str(payload)


def test_generation_task_is_registered_with_celery_app() -> None:
    assert "caragent_worker.tasks.jobs" in celery_app.conf.include
    assert generate_2d_concept_job.name == "caragent_worker.generate_2d_concept_job"


def test_postgres_async_driver_is_available_for_generation_tasks() -> None:
    assert importlib.import_module("asyncpg") is not None


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
        re.compile(r"^\s*from\s+(fal|bfl)[\w.-]*\b", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*import\s+(fal|bfl)[\w.-]*\b", re.IGNORECASE | re.MULTILINE),
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
