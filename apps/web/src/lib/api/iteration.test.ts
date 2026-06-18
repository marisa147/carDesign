import { describe, expect, it, vi } from "vitest";

import {
  getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl,
  getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl,
  getListExportsWorkspacesWorkspaceIdExportsGetUrl,
  getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl,
  getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl,
  type ExportResponse,
  type FeedbackResponse,
  type GenerationJobSubmissionResponse,
} from "@caragent/contracts";

import {
  buildIterationSubmissionPayload,
  createConceptExport,
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
