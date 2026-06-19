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

    result = subprocess.run(  # noqa: S603
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


def test_openapi_export_includes_phase_2_product_routes_and_schemas(tmp_path: Path) -> None:
    output_path = tmp_path / "openapi.json"

    export_openapi(output_path)

    schema = json.loads(output_path.read_text(encoding="utf-8"))
    paths = schema["paths"]
    schemas = schema["components"]["schemas"]

    for path, method in {
        "/workspaces": "post",
        "/workspaces/{workspace_id}": "get",
        "/workspaces/{workspace_id}/messages": "get",
        "/workspaces/{workspace_id}/briefs": "get",
        "/workspaces/{workspace_id}/assets": "post",
        "/assets/{asset_id}": "get",
        "/assets/{asset_id}/rights": "patch",
        "/workspaces/{workspace_id}/jobs": "post",
        "/workspaces/{workspace_id}/generation/briefs": "post",
        "/generation/briefs/{brief_id}": "patch",
        "/workspaces/{workspace_id}/generation/jobs": "post",
        "/jobs/{job_id}": "get",
        "/jobs/{job_id}/cancel": "post",
        "/jobs/{job_id}/retry": "post",
        "/jobs/{job_id}/events": "get",
        "/operations/provider-status": "get",
        "/workspaces/{workspace_id}/versions": "get",
        "/workspaces/{workspace_id}/artifacts": "get",
        "/jobs/{job_id}/model-runs": "get",
        "/workspaces/{workspace_id}/feedback": "get",
        "/workspaces/{workspace_id}/exports": "get",
        "/workspaces/{workspace_id}/versions/{version_id}/exports": "post",
    }.items():
        assert paths[path][method]

    assert schemas["AssetResponse"]["properties"]["rights_status"]
    assert schemas["AssetRightsUpdateRequest"]["properties"]["rights_status"]
    assert schemas["GenerationJobResponse"]["properties"]["estimated_cost"]
    assert schemas["GenerationJobResponse"]["properties"]["actual_cost"]
    assert schemas["GenerationJobResponse"]["properties"]["metadata"]
    assert schemas["JobEventResponse"]["properties"]["metadata"]
    assert schemas["OperationsProviderStatusResponse"]["properties"]["provider"]
    assert schemas["ProviderOperationsSummary"]["properties"]["hosted_daily_call_limit"]
    assert schemas["ProviderOperationsSummary"]["properties"]["hosted_rate_limit_per_minute"]
    assert schemas["ProviderOperationsSummary"]["properties"]["max_estimated_cost_per_job"]
    assert schemas["ProviderOperationsSummary"]["properties"]["hosted_calls_blocked_reason"]
    assert schemas["JobCreateResponse"]["properties"]["idempotent_reused"]
    assert schemas["GenerationBriefCreateRequest"]["properties"]["original_request"]
    assert schemas["GenerationBriefResponse"]["properties"]["payload"]
    assert schemas["GenerationJobSubmissionRequest"]["properties"]["brief_id"]
    assert schemas["GenerationJobCancelResponse"]["properties"]["queue_revoke"]
    assert schemas["QueueRevokeResponse"]["properties"]["status"]
    assert schemas["GenerationJobRetryResponse"]["properties"]["retry_of_job_id"]
    assert schemas["ExportCreateRequest"]["properties"]["format"]
    assert schemas["ExportResponse"]["properties"]["manifest"]

    phase_6_fields = {
        "character_focus",
        "color_harmony",
        "overlay_logo_asset_ids",
        "racing_cues",
        "supporting_graphics",
        "typography_intent",
    }
    assert phase_6_fields.issubset(schemas["GenerationBriefCreateRequest"]["properties"])
    assert phase_6_fields.issubset(schemas["GenerationBriefUpdateRequest"]["properties"])
    assert phase_6_fields.issubset(schemas["GenerationBriefPayload"]["properties"])


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
