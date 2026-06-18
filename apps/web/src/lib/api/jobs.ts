import {
  getCancelJobJobsJobIdCancelPostUrl,
  getCreateJobWorkspacesWorkspaceIdJobsPostUrl,
  getGetJobJobsJobIdGetUrl,
  getListEventsJobsJobIdEventsGetUrl,
  getListJobsWorkspacesWorkspaceIdJobsGetUrl,
  type GenerationJobCancelRequest,
  type GenerationJobCancelResponse,
  type GenerationJobResponse,
  type JobCreateRequest,
  type JobCreateResponse,
  type JobEventResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export interface JobApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export async function createWorkspaceJob(
  workspaceId: string,
  payload: JobCreateRequest,
  options: JobApiOptions = {},
): Promise<JobCreateResponse> {
  return requestJobJson<JobCreateResponse>(
    getCreateJobWorkspacesWorkspaceIdJobsPostUrl(workspaceId),
    "POST",
    payload,
    options,
  );
}

export async function listWorkspaceJobs(
  workspaceId: string,
  options: JobApiOptions = {},
): Promise<GenerationJobResponse[]> {
  return requestJobJson<GenerationJobResponse[]>(
    getListJobsWorkspacesWorkspaceIdJobsGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function getJob(
  jobId: string,
  options: JobApiOptions = {},
): Promise<GenerationJobResponse> {
  return requestJobJson<GenerationJobResponse>(
    getGetJobJobsJobIdGetUrl(jobId),
    "GET",
    undefined,
    options,
  );
}

export async function listJobEvents(
  jobId: string,
  options: JobApiOptions = {},
): Promise<JobEventResponse[]> {
  return requestJobJson<JobEventResponse[]>(
    getListEventsJobsJobIdEventsGetUrl(jobId),
    "GET",
    undefined,
    options,
  );
}

export async function cancelGenerationJob(
  jobId: string,
  payload: GenerationJobCancelRequest,
  options: JobApiOptions = {},
): Promise<GenerationJobCancelResponse> {
  return requestJobJson<GenerationJobCancelResponse>(
    getCancelJobJobsJobIdCancelPostUrl(jobId),
    "POST",
    payload,
    options,
  );
}

async function requestJobJson<T>(
  path: string,
  method: "GET" | "POST",
  body: unknown,
  options: JobApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the job client.");
  }

  const requestInit: RequestInit = { method };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }
  if (body !== undefined) {
    requestInit.headers = { "Content-Type": "application/json" };
    requestInit.body = JSON.stringify(body);
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Job request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
