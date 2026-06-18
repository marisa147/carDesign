import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const openapiPath = resolve(repoRoot, "packages/contracts/openapi/openapi.json");
const clientPath = resolve(repoRoot, "packages/contracts/src/generated/client.ts");

const openapi = JSON.parse(readFileSync(openapiPath, "utf8"));
const client = readFileSync(clientPath, "utf8");
const failures = [];

const requiredRoutes = [
  ["GET /health", "/health", "get"],
  ["POST /workspaces", "/workspaces", "post"],
  ["GET /workspaces/{workspace_id}", "/workspaces/{workspace_id}", "get"],
  ["GET /workspaces/{workspace_id}/assets", "/workspaces/{workspace_id}/assets", "get"],
  ["POST /workspaces/{workspace_id}/assets", "/workspaces/{workspace_id}/assets", "post"],
  ["PATCH /assets/{asset_id}/rights", "/assets/{asset_id}/rights", "patch"],
  ["POST /workspaces/{workspace_id}/generation/briefs", "/workspaces/{workspace_id}/generation/briefs", "post"],
  ["PATCH /generation/briefs/{brief_id}", "/generation/briefs/{brief_id}", "patch"],
  ["POST /workspaces/{workspace_id}/generation/jobs", "/workspaces/{workspace_id}/generation/jobs", "post"],
  ["GET /jobs/{job_id}", "/jobs/{job_id}", "get"],
  ["GET /jobs/{job_id}/events", "/jobs/{job_id}/events", "get"],
  ["GET /jobs/{job_id}/model-runs", "/jobs/{job_id}/model-runs", "get"],
  ["POST /jobs/{job_id}/retry", "/jobs/{job_id}/retry", "post"],
  ["POST /jobs/{job_id}/cancel", "/jobs/{job_id}/cancel", "post"],
  ["GET /operations/provider-status", "/operations/provider-status", "get"],
  ["GET /workspaces/{workspace_id}/artifacts", "/workspaces/{workspace_id}/artifacts", "get"],
  ["GET /workspaces/{workspace_id}/versions", "/workspaces/{workspace_id}/versions", "get"],
  ["GET /workspaces/{workspace_id}/feedback", "/workspaces/{workspace_id}/feedback", "get"],
  ["POST /workspaces/{workspace_id}/versions/{version_id}/feedback", "/workspaces/{workspace_id}/versions/{version_id}/feedback", "post"],
  ["GET /workspaces/{workspace_id}/exports", "/workspaces/{workspace_id}/exports", "get"],
  ["POST /workspaces/{workspace_id}/versions/{version_id}/exports", "/workspaces/{workspace_id}/versions/{version_id}/exports", "post"],
  ["POST /workspaces/{workspace_id}/versions/{version_id}/iterations", "/workspaces/{workspace_id}/versions/{version_id}/iterations", "post"],
];

const requiredSchemas = {
  WorkspaceResponse: ["id", "title", "created_at", "updated_at"],
  GenerationBriefResponse: ["id", "workspace_id", "payload", "status"],
  GenerationJobResponse: ["id", "workspace_id", "operation", "status", "provider", "model"],
  JobEventResponse: ["id", "job_id", "event_type", "message", "created_at"],
  ArtifactResponse: ["id", "workspace_id", "job_id", "version_id", "object_key", "width", "height"],
  DesignVersionResponse: ["id", "workspace_id", "parent_version_id", "job_id", "parameters", "lineage_depth"],
  FeedbackResponse: ["id", "workspace_id", "version_id", "rating", "approval_state", "comment"],
  ExportResponse: ["id", "workspace_id", "version_id", "artifact_id", "manifest"],
  GenerationJobCancelResponse: ["job", "queue_revoke"],
  OperationsProviderStatusResponse: ["api_version", "runtime_mode", "provider", "worker", "queue", "recent_failures"],
};

const requiredClientTokens = [
  "export interface WorkspaceResponse",
  "export interface GenerationBriefResponse",
  "export interface GenerationJobResponse",
  "export interface ArtifactResponse",
  "export interface DesignVersionResponse",
  "export type DesignVersionResponseParameters = { [key: string]: unknown }",
  "export interface FeedbackResponse",
  "export interface ExportResponse",
  "export interface OperationsProviderStatusResponse",
  "getHealthHealthGetUrl",
  "getCreateWorkspaceWorkspacesPostUrl",
  "getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl",
  "getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl",
  "getGetJobJobsJobIdGetUrl",
  "getCancelJobJobsJobIdCancelPostUrl",
  "getProviderStatusOperationsProviderStatusGetUrl",
  "getListArtifactsWorkspacesWorkspaceIdArtifactsGetUrl",
  "getListVersionsWorkspacesWorkspaceIdVersionsGetUrl",
  "getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl",
  "getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl",
  "getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl",
];

for (const [label, path, method] of requiredRoutes) {
  if (!openapi.paths?.[path]?.[method]) {
    failures.push(`Missing OpenAPI route: ${label}`);
  }
}

for (const [schemaName, propertyNames] of Object.entries(requiredSchemas)) {
  const schema = openapi.components?.schemas?.[schemaName];
  if (!schema) {
    failures.push(`Missing OpenAPI schema: ${schemaName}`);
    continue;
  }

  for (const propertyName of propertyNames) {
    if (!schema.properties?.[propertyName]) {
      failures.push(`Missing OpenAPI schema property: ${schemaName}.${propertyName}`);
    }
  }
}

const designVersionParameters =
  openapi.components?.schemas?.DesignVersionResponse?.properties?.parameters;
if (designVersionParameters?.type !== "object" || designVersionParameters?.additionalProperties !== true) {
  failures.push(
    "DesignVersionResponse.parameters must remain an open object so PreviewSpec metadata stays readable.",
  );
}

for (const token of requiredClientTokens) {
  if (!client.includes(token)) {
    failures.push(`Missing generated client surface: ${token}`);
  }
}

if (failures.length > 0) {
  console.error("V1 compatibility check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  console.error("\nRun `pnpm contracts:check` after reviewing intentional contract changes.");
  process.exit(1);
}

console.log(
  `V1 compatibility check passed: ${requiredRoutes.length} routes, ${Object.keys(requiredSchemas).length} schemas, and ${requiredClientTokens.length} client surfaces verified.`,
);
