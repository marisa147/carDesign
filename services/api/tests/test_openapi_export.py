from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from caragent_api.scripts.export_openapi import export_openapi


API_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = API_ROOT / "src"


def test_openapi_export_module_writes_health_schema(tmp_path: Path) -> None:
    output_path = tmp_path / "contracts" / "openapi.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "caragent_api.scripts.export_openapi",
            "--out",
            str(output_path),
        ],
        cwd=API_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    schema = json.loads(output_path.read_text(encoding="utf-8"))
    assert schema["paths"]["/health"]["get"]["responses"]["200"]


def test_openapi_export_format_is_deterministic(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    export_openapi(first_path)
    export_openapi(second_path)

    first = first_path.read_text(encoding="utf-8")
    second = second_path.read_text(encoding="utf-8")

    assert first == second
    assert first.startswith('{\n  "components"')
    assert first.endswith("\n")
