import { describe, expect, it, vi } from "vitest";

import {
  getCancelJobJobsJobIdCancelPostUrl,
  getCreateJobWorkspacesWorkspaceIdJobsPostUrl,
  getGetJobJobsJobIdGetUrl,
  getListEventsJobsJobIdEventsGetUrl,
  getListJobsWorkspacesWorkspaceIdJobsGetUrl,
  type GenerationJobCancelResponse,
  type GenerationJobResponse,
  type JobCreateResponse,
  type JobEventResponse,
} from "@caragent/contracts";

import {
  cancelGenerationJob,
  createWorkspaceJob,
  getJob,
  listJobEvents,
  listWorkspaceJobs,
} from "@/lib/api/jobs";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const jobFixture: GenerationJobResponse = {
  actual_cost: null,
  brief_id: null,
  created_at: "2026-06-17T00:00:00Z",
  estimated_cost: null,
  id: "job-1",
  idempotency_key: "brief-001",
  latest_error: null,
  model: null,
  operation: "generate_concept",
  provider: null,
  requested_by: null,
  status: "queued",
  updated_at: "2026-06-17T00:00:00Z",
  workspace_id: "workspace-1",
};

const createdJobFixture: JobCreateResponse = {
  ...jobFixture,
  idempotent_reused: false,
};

const eventFixture: JobEventResponse = {
  created_at: "2026-06-17T00:00:00Z",
  event_type: "created",
  id: "event-1",
  job_id: "job-1",
  message: "Job queued.",
  progress: null,
  sequence: 1,
  source: "api",
  status: "queued",
  updated_at: "2026-06-17T00:00:00Z",
};

const cancelFixture: GenerationJobCancelResponse = {
  job: {
    ...jobFixture,
    metadata: {
      operations: {
        failure_category: "canceled",
        reason: "user_request",
        requested_by: "web-workbench",
      },
    },
    status: "canceled",
  },
  queue_revoke: {
    detail: null,
    status: "revoked",
    task_id: "task-1",
  },
};

describe("job API wrappers", () => {
  it("creates and lists jobs through generated contract helpers", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(createdJobFixture, 201))
      .mockResolvedValueOnce(jsonResponse([jobFixture]));

    await expect(
      createWorkspaceJob(
        "workspace-1",
        { idempotency_key: "brief-001", operation: "generate_concept" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(createdJobFixture);
    await expect(
      listWorkspaceJobs("workspace-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual([jobFixture]);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getCreateJobWorkspacesWorkspaceIdJobsPostUrl("workspace-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          idempotency_key: "brief-001",
          operation: "generate_concept",
        }),
        method: "POST",
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getListJobsWorkspacesWorkspaceIdJobsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("reads job status and events and reports failed requests", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(jobFixture))
      .mockResolvedValueOnce(jsonResponse([eventFixture]))
      .mockResolvedValueOnce(jsonResponse({ detail: "nope" }, 404));

    await expect(
      getJob("job-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual(jobFixture);
    await expect(
      listJobEvents("job-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual([eventFixture]);
    await expect(
      getJob("missing", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).rejects.toThrow("Job request failed with status 404");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getGetJobJobsJobIdGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getListEventsJobsJobIdEventsGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("cancels jobs through the generated cancel route helper", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(cancelFixture))
      .mockResolvedValueOnce(jsonResponse({ detail: "terminal" }, 422));

    await expect(
      cancelGenerationJob(
        "job-1",
        { reason: "user_request", requested_by: "web-workbench" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(cancelFixture);
    await expect(
      cancelGenerationJob(
        "job-done",
        { reason: "user_request" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).rejects.toThrow("Job request failed with status 422");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getCancelJobJobsJobIdCancelPostUrl("job-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          reason: "user_request",
          requested_by: "web-workbench",
        }),
        method: "POST",
      }),
    );
  });
});
