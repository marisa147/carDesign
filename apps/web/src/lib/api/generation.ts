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
  type GenerationBriefCreateRequest,
  type GenerationBriefResponse,
  type GenerationBriefUpdateRequest,
  type GenerationJobResponse,
  type GenerationJobRetryRequest,
  type GenerationJobRetryResponse,
  type GenerationJobSubmissionRequest,
  type GenerationJobSubmissionResponse,
  type JobEventResponse,
  type ReferenceAssignment,
  type ReferenceRole,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";
import { LOCAL_PROVIDER_ID } from "@/lib/api/operations";

export interface GenerationApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export interface GenerationState {
  artifacts: ArtifactResponse[];
  events: JobEventResponse[];
  exports: ExportResponse[];
  feedback: FeedbackResponse[];
  job: GenerationJobResponse;
  versions: DesignVersionResponse[];
}

export interface ProviderIntentSelection {
  enabled: boolean;
  id: string;
  model?: string | null;
  providerParameters?: Record<string, unknown>;
}

export const REFERENCE_ROLE_OPTIONS: {
  label: string;
  value: ReferenceRole;
}[] = [
  { label: "角色", value: "character" },
  { label: "风格", value: "style" },
  { label: "车辆", value: "vehicle" },
  { label: "Logo", value: "logo" },
  { label: "配色", value: "palette" },
  { label: "仅灵感", value: "inspiration" },
];

export const DEFAULT_REFERENCE_ROLE: ReferenceRole = "inspiration";

export interface ReferenceUsageDraft {
  assetId: string;
  enabled: boolean;
  role: ReferenceRole;
}

export function buildReferenceUsagePayload(
  assignments: ReferenceUsageDraft[],
): Pick<GenerationBriefUpdateRequest, "reference_asset_ids" | "reference_usage"> {
  const referenceUsage: ReferenceAssignment[] = assignments.map((assignment) => ({
    asset_id: assignment.assetId,
    enabled: assignment.enabled,
    role: assignment.role,
  }));

  return {
    reference_asset_ids: referenceUsage
      .filter((assignment) => assignment.enabled !== false)
      .map((assignment) => assignment.asset_id),
    reference_usage: referenceUsage,
  };
}

export async function createGenerationBrief(
  workspaceId: string,
  payload: GenerationBriefCreateRequest,
  options: GenerationApiOptions = {},
): Promise<GenerationBriefResponse> {
  return requestGenerationJson<GenerationBriefResponse>(
    getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl(workspaceId),
    "POST",
    payload,
    options,
  );
}

export async function updateGenerationBrief(
  briefId: string,
  payload: GenerationBriefUpdateRequest,
  options: GenerationApiOptions = {},
): Promise<GenerationBriefResponse> {
  return requestGenerationJson<GenerationBriefResponse>(
    getUpdateGenerationBriefRouteGenerationBriefsBriefIdPatchUrl(briefId),
    "PATCH",
    payload,
    options,
  );
}

export async function submitGenerationJob(
  workspaceId: string,
  payload: GenerationJobSubmissionRequest,
  options: GenerationApiOptions = {},
): Promise<GenerationJobSubmissionResponse> {
  return requestGenerationJson<GenerationJobSubmissionResponse>(
    getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl(workspaceId),
    "POST",
    payload,
    options,
  );
}

export function buildGenerationSubmissionPayload(
  basePayload: GenerationJobSubmissionRequest,
  providerSelection?: ProviderIntentSelection | null,
): GenerationJobSubmissionRequest {
  return {
    ...basePayload,
    ...buildProviderIntentPayload(providerSelection),
  };
}

export function buildProviderIntentPayload(
  providerSelection?: ProviderIntentSelection | null,
): Pick<GenerationJobSubmissionRequest, "model" | "provider" | "provider_parameters"> {
  if (
    !providerSelection ||
    !providerSelection.enabled ||
    providerSelection.id === LOCAL_PROVIDER_ID
  ) {
    return {};
  }

  const payload: Pick<
    GenerationJobSubmissionRequest,
    "model" | "provider" | "provider_parameters"
  > = {
    provider: providerSelection.id,
  };
  if (providerSelection.model) {
    payload.model = providerSelection.model;
  }
  if (
    providerSelection.providerParameters &&
    Object.keys(providerSelection.providerParameters).length > 0
  ) {
    payload.provider_parameters = providerSelection.providerParameters;
  }

  return payload;
}

export async function retryGenerationJob(
  jobId: string,
  payload: GenerationJobRetryRequest,
  options: GenerationApiOptions = {},
): Promise<GenerationJobRetryResponse> {
  return requestGenerationJson<GenerationJobRetryResponse>(
    getRetryGenerationJobJobsJobIdRetryPostUrl(jobId),
    "POST",
    payload,
    options,
  );
}

export async function loadGenerationState(
  workspaceId: string,
  jobId: string,
  options: GenerationApiOptions = {},
): Promise<GenerationState> {
  const [job, events, artifacts, versions, feedback, exports] = await Promise.all([
    requestGenerationJson<GenerationJobResponse>(
      getGetJobJobsJobIdGetUrl(jobId),
      "GET",
      undefined,
      options,
    ),
    requestGenerationJson<JobEventResponse[]>(
      getListEventsJobsJobIdEventsGetUrl(jobId),
      "GET",
      undefined,
      options,
    ),
    requestGenerationJson<ArtifactResponse[]>(
      getListArtifactsWorkspacesWorkspaceIdArtifactsGetUrl(workspaceId),
      "GET",
      undefined,
      options,
    ),
    requestGenerationJson<DesignVersionResponse[]>(
      getListVersionsWorkspacesWorkspaceIdVersionsGetUrl(workspaceId),
      "GET",
      undefined,
      options,
    ),
    requestGenerationJson<FeedbackResponse[]>(
      getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl(workspaceId),
      "GET",
      undefined,
      options,
    ),
    requestGenerationJson<ExportResponse[]>(
      getListExportsWorkspacesWorkspaceIdExportsGetUrl(workspaceId),
      "GET",
      undefined,
      options,
    ),
  ]);

  return { artifacts, events, exports, feedback, job, versions };
}

async function requestGenerationJson<T>(
  path: string,
  method: "GET" | "PATCH" | "POST",
  body: unknown,
  options: GenerationApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the generation client.");
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
    throw new Error(`Generation request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
