from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from caragent_worker.config import get_settings


@pytest.fixture(autouse=True)
def isolate_worker_settings_env_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[None]:
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
