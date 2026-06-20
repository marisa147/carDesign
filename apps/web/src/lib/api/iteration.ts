import {
  getCreatePreview3dScreenshotWorkspacesWorkspaceIdVersionsVersionIdPreview3dScreenshotsPostUrl,
  getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl,
  getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl,
  getListExportsWorkspacesWorkspaceIdExportsGetUrl,
  getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl,
  getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl,
  type ArtifactResponse,
  type ExportCreateRequest,
  type ExportResponse,
  type FeedbackCreateRequest,
  type FeedbackResponse,
  type GenerationIterationSubmissionRequest,
  type GenerationJobSubmissionResponse,
  type Preview3DScreenshotCreateRequest,
} from "@caragent/contracts";

import {
  buildProviderIntentPayload,
  buildReferenceUsagePayload,
  type ProviderIntentSelection,
  type ReferenceUsageDraft,
} from "@/lib/api/generation";
import { publicEnv } from "@/lib/config/public-env";

export interface IterationApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export interface ProductionReadinessPreflightReport {
  blockers: string[];
  checks: Array<{
    id: string;
    label: string;
    message: string;
    severity: "blocker" | "info" | "warning";
    status: "blocked" | "missing" | "ready" | "warning";
  }>;
  disclaimer: string;
  missing_evidence: string[];
  print_ready_allowed: boolean;
  status: "concept_only";
  version_id: string;
  workspace_id: string;
}

export interface ProductionReadinessPreflightResponse {
  export: ExportResponse;
  report: ProductionReadinessPreflightReport;
}

export async function submitChildIteration(
  workspaceId: string,
  versionId: string,
  payload: GenerationIterationSubmissionRequest,
  options: IterationApiOptions = {},
): Promise<GenerationJobSubmissionResponse> {
  return requestIterationJson<GenerationJobSubmissionResponse>(
    getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl(
      workspaceId,
      versionId,
    ),
    "POST",
    payload,
    options,
  );
}

export function buildIterationSubmissionPayload(
  basePayload: GenerationIterationSubmissionRequest,
  options: {
    providerSelection?: ProviderIntentSelection | null;
    referenceAssignments?: ReferenceUsageDraft[];
  } = {},
): GenerationIterationSubmissionRequest {
  const referenceOverrides =
    options.referenceAssignments && options.referenceAssignments.length > 0
      ? buildReferenceUsagePayload(options.referenceAssignments)
      : {};
  const parameterOverrides = {
    ...(basePayload.parameter_overrides ?? {}),
    ...referenceOverrides,
  };

  return {
    ...basePayload,
    ...(Object.keys(parameterOverrides).length > 0
      ? { parameter_overrides: parameterOverrides }
      : {}),
    ...buildProviderIntentPayload(options.providerSelection),
  };
}

export async function createVersionFeedback(
  workspaceId: string,
  versionId: string,
  payload: FeedbackCreateRequest,
  options: IterationApiOptions = {},
): Promise<FeedbackResponse> {
  return requestIterationJson<FeedbackResponse>(
    getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl(
      workspaceId,
      versionId,
    ),
    "POST",
    payload,
    options,
  );
}

export async function createConceptExport(
  workspaceId: string,
  versionId: string,
  payload: ExportCreateRequest,
  options: IterationApiOptions = {},
): Promise<ExportResponse> {
  return requestIterationJson<ExportResponse>(
    getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl(workspaceId, versionId),
    "POST",
    payload,
    options,
  );
}

export async function createProductionReadinessPreflight(
  workspaceId: string,
  versionId: string,
  options: IterationApiOptions = {},
): Promise<ProductionReadinessPreflightResponse> {
  return requestIterationJson<ProductionReadinessPreflightResponse>(
    `/workspaces/${workspaceId}/versions/${versionId}/production-readiness-preflight`,
    "POST",
    undefined,
    options,
  );
}

export async function createPreview3DScreenshot(
  workspaceId: string,
  versionId: string,
  payload: Preview3DScreenshotCreateRequest,
  options: IterationApiOptions = {},
): Promise<ArtifactResponse> {
  return requestIterationJson<ArtifactResponse>(
    getCreatePreview3dScreenshotWorkspacesWorkspaceIdVersionsVersionIdPreview3dScreenshotsPostUrl(
      workspaceId,
      versionId,
    ),
    "POST",
    payload,
    options,
  );
}

export async function listWorkspaceFeedback(
  workspaceId: string,
  options: IterationApiOptions = {},
): Promise<FeedbackResponse[]> {
  return requestIterationJson<FeedbackResponse[]>(
    getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function listWorkspaceExports(
  workspaceId: string,
  options: IterationApiOptions = {},
): Promise<ExportResponse[]> {
  return requestIterationJson<ExportResponse[]>(
    getListExportsWorkspacesWorkspaceIdExportsGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

async function requestIterationJson<T>(
  path: string,
  method: "GET" | "POST",
  body: unknown,
  options: IterationApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the iteration client.");
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
    throw new Error(`Iteration request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
