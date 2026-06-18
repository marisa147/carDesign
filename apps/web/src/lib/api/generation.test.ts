import { describe, expect, it, vi } from "vitest";

import {
  getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl,
  getGetJobJobsJobIdGetUrl,
  getListArtifactsWorkspacesWorkspaceIdArtifactsGetUrl,
  getListEventsJobsJobIdEventsGetUrl,
  getListExportsWorkspacesWorkspaceIdExportsGetUrl,
  getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl,
  getListVersionsWorkspacesWorkspaceIdVersionsGetUrl,
  getRetryGenerationJobJobsJobIdRetryPostUrl,
  getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl,
  getUpdateGenerationBriefRouteGenerationBriefsBriefIdPatchUrl,
  type ArtifactResponse,
  type DesignVersionResponse,
  type ExportResponse,
  type FeedbackResponse,
  type GenerationBriefResponse,
  type GenerationJobResponse,
  type GenerationJobRetryResponse,
  type GenerationJobSubmissionResponse,
  type JobEventResponse,
} from "@caragent/contracts";

import {
  createGenerationBrief,
  loadGenerationState,
  retryGenerationJob,
  submitGenerationJob,
  updateGenerationBrief,
} from "@/lib/api/generation";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const generatedAt = "2026-06-17T00:00:00Z";

const briefFixture: GenerationBriefResponse = {
  created_at: generatedAt,
  id: "brief-1",
  payload: {
    canvas_height: 768,
    canvas_width: 1536,
    character_theme: "Sakura heroine",
    coverage: "balanced side coverage",
    original_request: "White coupe with Sakura heroine and MOON DRIVE text.",
    palette: ["white", "teal"],
    reference_asset_ids: [],
    style: "itasha concept",
    text: ["MOON DRIVE"],
    vehicle_template_id: "generic-side-coupe",
    vehicle_template_label: "Generic side-view coupe",
    view: "side",
    warnings: [],
  },
  source_message_id: null,
  status: "draft",
  title: "Phase 3 brief",
  updated_at: generatedAt,
  workspace_id: "workspace-1",
};

const generationJobFixture: GenerationJobResponse = {
  actual_cost: null,
  brief_id: "brief-1",
  created_at: generatedAt,
  estimated_cost: null,
  id: "job-1",
  idempotency_key: "phase3-generation",
  latest_error: null,
  model: null,
  operation: "generate_2d_concept",
  provider: null,
  requested_by: "web-proof",
  status: "queued",
  updated_at: generatedAt,
  workspace_id: "workspace-1",
};

const submissionFixture: GenerationJobSubmissionResponse = {
  idempotent_reused: false,
  job: generationJobFixture,
  queued: {
    job_id: "job-1",
    task_id: null,
    task_name: "caragent_worker.generate_2d_concept_job",
  },
};

const retryFixture: GenerationJobRetryResponse = {
  ...submissionFixture,
  retry_of_job_id: "failed-job-1",
};

const eventFixture: JobEventResponse = {
  created_at: generatedAt,
  event_type: "created",
  id: "event-1",
  job_id: "job-1",
  message: "Job queued.",
  progress: null,
  sequence: 1,
  source: "api",
  status: "queued",
  updated_at: generatedAt,
};

const artifactFixture: ArtifactResponse = {
  asset_id: null,
  byte_size: 512,
  checksum_sha256: "a".repeat(64),
  content_type: "image/png",
  created_at: generatedAt,
  height: 768,
  id: "artifact-1",
  job_id: "job-1",
  kind: "generated_image",
  object_key: "workspaces/workspace-1/generated_image/artifact-1/concept.png",
  updated_at: generatedAt,
  version_id: "version-1",
  width: 1536,
  workspace_id: "workspace-1",
};

const versionFixture: DesignVersionResponse = {
  brief_id: "brief-1",
  created_at: generatedAt,
  id: "version-1",
  job_id: "job-1",
  lineage_depth: 0,
  parameters: { concept_label: "concept_preview" },
  parent_version_id: null,
  status: "generated",
  summary: "Generated 2D concept preview.",
  title: "Generated concept preview",
  updated_at: generatedAt,
  workspace_id: "workspace-1",
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
  manifest: { disclaimer: "Concept preview only, not print-ready." },
  requested_at: generatedAt,
  status: "requested",
  updated_at: generatedAt,
  version_id: "version-1",
  workspace_id: "workspace-1",
};

describe("generation API wrappers", () => {
  it("creates and updates structured briefs with generated route helpers", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(briefFixture, 201))
      .mockResolvedValueOnce(
        jsonResponse({
          ...briefFixture,
          payload: { ...briefFixture.payload, coverage: "full side coverage" },
        }),
      );

    await expect(
      createGenerationBrief(
        "workspace-1",
        {
          character_theme: "Sakura heroine",
          original_request: "White coupe with Sakura heroine and MOON DRIVE text.",
          palette: ["white", "teal"],
          text: ["MOON DRIVE"],
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(briefFixture);
    await expect(
      updateGenerationBrief(
        "brief-1",
        { coverage: "full side coverage" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toMatchObject({ payload: { coverage: "full side coverage" } });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl("workspace-1")}`,
      expect.objectContaining({
        method: "POST",
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getUpdateGenerationBriefRouteGenerationBriefsBriefIdPatchUrl("brief-1")}`,
      expect.objectContaining({
        body: JSON.stringify({ coverage: "full side coverage" }),
        method: "PATCH",
      }),
    );
  });

  it("submits and retries generation jobs without provider secrets", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(submissionFixture, 201))
      .mockResolvedValueOnce(jsonResponse(retryFixture, 201));

    await expect(
      submitGenerationJob(
        "workspace-1",
        {
          brief_id: "brief-1",
          idempotency_key: "phase3-generation",
          requested_by: "web-proof",
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(submissionFixture);
    await expect(
      retryGenerationJob(
        "failed-job-1",
        { idempotency_key: "retry-1", requested_by: "web-proof" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(retryFixture);

    const requestBodies = fetchMock.mock.calls
      .map(([, init]) => String((init as RequestInit).body ?? ""))
      .join("\n");
    expect(requestBodies).not.toMatch(/api[_-]?key|secret|provider/i);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl("workspace-1")}`,
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getRetryGenerationJobJobsJobIdRetryPostUrl("failed-job-1")}`,
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("loads durable job, event, artifact, version, feedback, and export state", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(generationJobFixture))
      .mockResolvedValueOnce(jsonResponse([eventFixture]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture]))
      .mockResolvedValueOnce(jsonResponse([feedbackFixture]))
      .mockResolvedValueOnce(jsonResponse([exportFixture]));

    await expect(
      loadGenerationState("workspace-1", "job-1", {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual({
      artifacts: [artifactFixture],
      events: [eventFixture],
      exports: [exportFixture],
      feedback: [feedbackFixture],
      job: generationJobFixture,
      versions: [versionFixture],
    });

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getGetJobJobsJobIdGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListEventsJobsJobIdEventsGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListArtifactsWorkspacesWorkspaceIdArtifactsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListVersionsWorkspacesWorkspaceIdVersionsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListExportsWorkspacesWorkspaceIdExportsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("reports failed requests with generation-specific errors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ detail: "nope" }, 500));

    await expect(
      submitGenerationJob(
        "workspace-1",
        { brief_id: "brief-1", idempotency_key: "phase3-generation" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).rejects.toThrow("Generation request failed with status 500");
  });
});
