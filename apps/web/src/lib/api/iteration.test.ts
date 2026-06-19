import { describe, expect, it, vi } from "vitest";

import {
  getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl,
  getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl,
  getCreatePreview3dScreenshotWorkspacesWorkspaceIdVersionsVersionIdPreview3dScreenshotsPostUrl,
  getListExportsWorkspacesWorkspaceIdExportsGetUrl,
  getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl,
  getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl,
  type ArtifactResponse,
  type ExportResponse,
  type FeedbackResponse,
  type GenerationJobSubmissionResponse,
  type Preview3DScreenshotCreateRequest,
} from "@caragent/contracts";

import {
  buildIterationSubmissionPayload,
  createConceptExport,
  createPreview3DScreenshot,
  createVersionFeedback,
  listWorkspaceExports,
  listWorkspaceFeedback,
  submitChildIteration,
} from "@/lib/api/iteration";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const generatedAt = "2026-06-17T00:00:00Z";

const iterationSubmissionFixture: GenerationJobSubmissionResponse = {
  idempotent_reused: false,
  job: {
    actual_cost: null,
    brief_id: "brief-1",
    created_at: generatedAt,
    estimated_cost: null,
    id: "job-iteration-1",
    idempotency_key: "iterate-version-1",
    latest_error: null,
    model: null,
    operation: "generate_2d_concept",
    provider: null,
    requested_by: "web-proof",
    status: "queued",
    updated_at: generatedAt,
    workspace_id: "workspace-1",
  },
  queued: {
    job_id: "job-iteration-1",
    task_id: null,
    task_name: "caragent_worker.generate_2d_concept_job",
  },
};

const feedbackFixture: FeedbackResponse = {
  approval_state: "approved",
  comment: "Use this direction.",
  created_at: generatedAt,
  id: "feedback-1",
  rating: 5,
  updated_at: generatedAt,
  version_id: "version-1",
  workspace_id: "workspace-1",
};

const exportFixture: ExportResponse = {
  artifact_id: "artifact-1",
  completed_at: null,
  concept_label: "client-review",
  created_at: generatedAt,
  format: "png",
  id: "export-1",
  manifest: {
    disclaimer: "Concept preview only, not print-ready.",
    version_id: "version-1",
  },
  requested_at: generatedAt,
  status: "requested",
  updated_at: generatedAt,
  version_id: "version-1",
  workspace_id: "workspace-1",
};

const preview3dScreenshotRequestFixture: Preview3DScreenshotCreateRequest = {
  content_type: "image/png",
  filename: "preview-3d-screenshot.png",
  height: 360,
  image_base64: "iVBORw0KGgo=",
  preview_3d: {
    camera: {
      position: { x: 2.8, y: 1.4, z: 4.2 },
      preset_id: "front-left-default",
      target: { x: 0, y: 0.4, z: 0 },
      zoom: 1,
    },
    compatibility: {
      shell_id: "generic-side-coupe-lightweight-v1",
      status: "compatible",
    },
    materials: {
      decal_strategy: "preview_spec_projection",
      source_artifact_id: "artifact-1",
      source_kind: "preview_spec",
    },
    mode: "lightweight_shell",
    shell: {
      dimensions: { height: 1.4, length: 4.4, width: 1.8 },
      id: "generic-side-coupe-lightweight-v1",
      label: "Generic side coupe lightweight shell",
      material_slots: ["body", "side-decal-plane"],
      template_id: "generic-side-coupe",
    },
    source: {
      artifact_id: "artifact-1",
      artifact_object_key: "workspaces/workspace-1/generated/artifact-1/concept.png",
      preview_spec_template_id: "generic-side-coupe",
      preview_spec_view: "side",
      version_id: "version-1",
      workspace_id: "workspace-1",
    },
    warnings: [
      {
        id: "non_production_preview",
        message: "Concept only.",
        severity: "warning",
      },
      {
        id: "uv_not_verified",
        message: "UV not verified.",
        severity: "warning",
      },
    ],
  },
  width: 640,
};

const preview3dScreenshotArtifactFixture: ArtifactResponse = {
  asset_id: null,
  byte_size: 40,
  checksum_sha256: "a".repeat(64),
  content_type: "image/png",
  created_at: generatedAt,
  height: 360,
  id: "artifact-3d-1",
  job_id: "job-iteration-1",
  kind: "preview_3d_screenshot",
  metadata: {},
  object_key: "workspaces/workspace-1/preview_3d_screenshot/artifact-3d-1/preview.png",
  preview_3d_screenshot: null,
  updated_at: generatedAt,
  version_id: "version-1",
  width: 640,
  workspace_id: "workspace-1",
};

describe("iteration API wrappers", () => {
  it("builds child iteration payloads with current reference usage and provider intent", () => {
    const payload = buildIterationSubmissionPayload(
      {
        brief_id: "brief-1",
        change_request: "Make the door character larger.",
        idempotency_key: "iterate-version-1",
        parameter_overrides: { coverage: "door focus" },
        requested_by: "web-proof",
      },
      {
        providerSelection: {
          enabled: true,
          id: "bfl",
          model: "flux-2-pro-preview",
          providerParameters: { safety_tolerance: 2 },
        },
        referenceAssignments: [
          {
            assetId: "asset-2",
            enabled: true,
            role: "character",
          },
        ],
      },
    );

    expect(payload).toEqual({
      brief_id: "brief-1",
      change_request: "Make the door character larger.",
      idempotency_key: "iterate-version-1",
      model: "flux-2-pro-preview",
      parameter_overrides: {
        coverage: "door focus",
        reference_asset_ids: ["asset-2"],
        reference_usage: [
          {
            asset_id: "asset-2",
            enabled: true,
            role: "character",
          },
        ],
      },
      provider: "bfl",
      provider_parameters: { safety_tolerance: 2 },
      requested_by: "web-proof",
    });
    expect(JSON.stringify(payload).match(/reference_usage/g)).toHaveLength(1);
  });

  it("submits child iteration jobs with exact generated URLs and bodies", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(iterationSubmissionFixture, 201));

    await expect(
      submitChildIteration(
        "workspace-1",
        "version-1",
        {
          brief_id: "brief-1",
          change_request: "Make the door character larger.",
          idempotency_key: "iterate-version-1",
          parameter_overrides: { coverage: "door focus" },
          requested_by: "web-proof",
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(iterationSubmissionFixture);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl(
        "workspace-1",
        "version-1",
      )}`,
      expect.objectContaining({
        body: JSON.stringify({
          brief_id: "brief-1",
          change_request: "Make the door character larger.",
          idempotency_key: "iterate-version-1",
          parameter_overrides: { coverage: "door focus" },
          requested_by: "web-proof",
        }),
        method: "POST",
      }),
    );
  });

  it("creates feedback and concept exports with version-scoped URLs", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(feedbackFixture, 201))
      .mockResolvedValueOnce(jsonResponse(exportFixture, 201));

    await expect(
      createVersionFeedback(
        "workspace-1",
        "version-1",
        {
          approval_state: "approved",
          comment: "Use this direction.",
          metadata: { source: "web" },
          rating: 5,
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(feedbackFixture);
    await expect(
      createConceptExport(
        "workspace-1",
        "version-1",
        {
          artifact_id: "artifact-1",
          concept_label: "client-review",
          format: "png",
          manifest: { requested_by: "web-proof" },
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(exportFixture);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl(
        "workspace-1",
        "version-1",
      )}`,
      expect.objectContaining({
        body: JSON.stringify({
          approval_state: "approved",
          comment: "Use this direction.",
          metadata: { source: "web" },
          rating: 5,
        }),
        method: "POST",
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl(
        "workspace-1",
        "version-1",
      )}`,
      expect.objectContaining({
        body: JSON.stringify({
          artifact_id: "artifact-1",
          concept_label: "client-review",
          format: "png",
          manifest: { requested_by: "web-proof" },
        }),
        method: "POST",
      }),
    );
  });

  it("creates enhanced handoff package exports with safe manifest payloads", async () => {
    const enhancedExportFixture: ExportResponse = {
      ...exportFixture,
      artifact_id: "artifact-export-zip-1",
      completed_at: generatedAt,
      format: "enhanced_concept_handoff_zip",
      id: "export-zip-1",
      manifest: {
        disclaimer: "概念交接包，仅供评审",
        format: "enhanced_concept_handoff_zip",
        package_artifact: {
          content_type: "application/zip",
          object_key: "workspaces/workspace-1/export/package.zip",
        },
        schema_version: 1,
        version_id: "version-1",
      },
      status: "succeeded",
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(enhancedExportFixture, 201));
    const payload = {
      artifact_id: "artifact-1",
      concept_label: "client-review",
      format: "enhanced_concept_handoff_zip",
      manifest: {
        disclaimer: "概念交接包，仅供评审",
        included_reference_asset_ids: ["asset-2"],
        source: "web-workbench",
        source_artifact_object_key: "workspaces/workspace-1/generated/artifact-1/concept.png",
        version_id: "version-1",
      },
    };

    await expect(
      createConceptExport("workspace-1", "version-1", payload, {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual(enhancedExportFixture);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl(
        "workspace-1",
        "version-1",
      )}`,
      expect.objectContaining({
        body: JSON.stringify(payload),
        method: "POST",
      }),
    );
    expect(JSON.stringify(payload)).not.toMatch(/[A-Z]:\\|api[_-]?key|secret|image_base64/i);
  });

  it("creates preview 3D screenshots with version-scoped URLs and metadata payloads", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(preview3dScreenshotArtifactFixture, 201));

    await expect(
      createPreview3DScreenshot(
        "workspace-1",
        "version-1",
        preview3dScreenshotRequestFixture,
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(preview3dScreenshotArtifactFixture);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getCreatePreview3dScreenshotWorkspacesWorkspaceIdVersionsVersionIdPreview3dScreenshotsPostUrl(
        "workspace-1",
        "version-1",
      )}`,
      expect.objectContaining({
        body: JSON.stringify(preview3dScreenshotRequestFixture),
        method: "POST",
      }),
    );
  });

  it("lists feedback and exports without leaking provider configuration", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([feedbackFixture]))
      .mockResolvedValueOnce(jsonResponse([exportFixture]));

    await expect(
      listWorkspaceFeedback("workspace-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual([feedbackFixture]);
    await expect(
      listWorkspaceExports("workspace-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual([exportFixture]);

    const requestBodies = fetchMock.mock.calls
      .map(([, init]) => String((init as RequestInit).body ?? ""))
      .join("\n");
    expect(requestBodies).not.toMatch(/api[_-]?key|secret|provider/i);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getListExportsWorkspacesWorkspaceIdExportsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("reports failed requests with iteration-specific errors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ detail: "nope" }, 422));

    await expect(
      submitChildIteration(
        "workspace-1",
        "version-1",
        {
          brief_id: "brief-1",
          change_request: "Try another palette.",
          idempotency_key: "iterate-fail",
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).rejects.toThrow("Iteration request failed with status 422");
  });
});
