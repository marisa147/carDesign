import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type RecentFailureResponse,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export const LOCAL_PROVIDER_ID = "local-deterministic";
export const BFL_PROVIDER_ID = "bfl";
const LOCAL_PROVIDER_MODEL = "local-concept-v1";
const BFL_DEFAULT_MODEL = "flux-2-pro-preview";

export interface OperationsApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export interface WorkbenchProviderOption {
  blockedReasons: string[];
  conceptLabel: string;
  enabled: boolean;
  guardLabel: string;
  id: string;
  label: string;
  maxCostLabel: string;
  model: string;
  statusLabel: string;
}

export interface WorkbenchRecentFailure {
  failureCategory: string;
  failureKind: string | null;
  jobId: string;
  message: string | null;
  model: string | null;
  provider: string | null;
  providerStatus: string | null;
  stage: string | null;
  status: string;
}

export interface WorkbenchProviderStatus {
  activeProviderId: string;
  guardLabel: string;
  maxCostLabel: string;
  options: WorkbenchProviderOption[];
  recentFailures: WorkbenchRecentFailure[];
}

export async function getProviderStatus(
  options: OperationsApiOptions = {},
): Promise<OperationsProviderStatusResponse> {
  return requestOperationsJson<OperationsProviderStatusResponse>(
    getProviderStatusOperationsProviderStatusGetUrl(),
    options,
  );
}

export function normalizeProviderStatus(
  status: OperationsProviderStatusResponse | null,
): WorkbenchProviderStatus {
  const provider = status?.provider;
  const capabilities = new Map<string, Record<string, unknown>>();
  for (const item of provider?.capabilities ?? []) {
    const record = asRecord(item);
    if (!record) {
      continue;
    }
    const providerId = readString(record, "provider");
    if (providerId) {
      capabilities.set(providerId, record);
    }
  }

  const guardState = asRecord(provider?.guard_state);
  const guardLabel = formatLimitLabel(
    readNumber(guardState, "daily_call_limit") ?? provider?.hosted_daily_call_limit ?? null,
    readNumber(guardState, "rate_limit_per_minute") ??
      provider?.hosted_rate_limit_per_minute ??
      null,
  );
  const maxCostLabel = formatMaxCostLabel(
    readString(guardState, "max_estimated_cost_per_job") ||
      provider?.max_estimated_cost_per_job ||
      null,
  );

  const localOption = buildLocalProviderOption(capabilities.get(LOCAL_PROVIDER_ID));
  const bflOption = buildBflProviderOption({
    capability: capabilities.get(BFL_PROVIDER_ID),
    guardLabel,
    maxCostLabel,
    status,
  });
  const activeProviderId =
    provider?.active_mode === BFL_PROVIDER_ID && bflOption.enabled
      ? BFL_PROVIDER_ID
      : LOCAL_PROVIDER_ID;

  return {
    activeProviderId,
    guardLabel,
    maxCostLabel,
    options: [localOption, bflOption],
    recentFailures: (status?.recent_failures ?? []).map(normalizeRecentFailure),
  };
}

export function getProviderOption(
  status: WorkbenchProviderStatus,
  providerId: string,
): WorkbenchProviderOption | undefined {
  return status.options.find((option) => option.id === providerId);
}

async function requestOperationsJson<T>(
  path: string,
  options: OperationsApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the operations client.");
  }

  const requestInit: RequestInit = { method: "GET" };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Operations request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

function buildLocalProviderOption(
  capability: Record<string, unknown> | undefined,
): WorkbenchProviderOption {
  const model = readString(capability, "default_model") || LOCAL_PROVIDER_MODEL;
  return {
    blockedReasons: [],
    conceptLabel: "概念预览",
    enabled: true,
    guardLabel: "本地绕过",
    id: LOCAL_PROVIDER_ID,
    label: "本地概念",
    maxCostLabel: "0 cost",
    model,
    statusLabel: "可用",
  };
}

function buildBflProviderOption({
  capability,
  guardLabel,
  maxCostLabel,
  status,
}: {
  capability: Record<string, unknown> | undefined;
  guardLabel: string;
  maxCostLabel: string;
  status: OperationsProviderStatusResponse | null;
}): WorkbenchProviderOption {
  const provider = status?.provider;
  const rawBlockedReasons = readStringArray(capability, "blocked_reasons");
  const inferredBlockedReasons = inferBflBlockedReasons(status);
  const blockedReasons = (
    rawBlockedReasons.length > 0 ? rawBlockedReasons : inferredBlockedReasons
  ).map(formatBlockedReason);
  const enabled =
    typeof capability?.enabled === "boolean"
      ? capability.enabled && blockedReasons.length === 0
      : Boolean(
          provider?.calls_enabled &&
            provider.bfl_key_configured &&
            provider.hosted_provider_configured &&
            provider.hosted_quota_guard_enabled &&
            !provider.hosted_calls_blocked_reason,
        );
  const model = readString(capability, "default_model") || BFL_DEFAULT_MODEL;

  return {
    blockedReasons,
    conceptLabel: "概念预览",
    enabled,
    guardLabel,
    id: BFL_PROVIDER_ID,
    label: "BFL 托管",
    maxCostLabel,
    model,
    statusLabel: status ? (enabled ? "可用" : "暂不可用") : "未刷新",
  };
}

function inferBflBlockedReasons(status: OperationsProviderStatusResponse | null): string[] {
  const provider = status?.provider;
  if (!provider) {
    return ["Provider status has not been refreshed"];
  }

  const reasons: string[] = [];
  if (provider.hosted_calls_blocked_reason) {
    reasons.push(provider.hosted_calls_blocked_reason);
  }
  if (!provider.calls_enabled) {
    reasons.push("AI_PROVIDER_CALLS_ENABLED is disabled");
  }
  if (!provider.bfl_key_configured) {
    reasons.push("AI_PROVIDER_BFL_API_KEY is missing");
  }
  if (!provider.hosted_quota_guard_enabled) {
    reasons.push("Hosted quota/rate/cost guards are incomplete");
  }
  return reasons;
}

function normalizeRecentFailure(failure: RecentFailureResponse): WorkbenchRecentFailure {
  return {
    failureCategory: sanitizeDiagnosticText(failure.failure_category),
    failureKind: failure.provider_failure_kind
      ? sanitizeDiagnosticText(failure.provider_failure_kind)
      : null,
    jobId: sanitizeDiagnosticText(failure.job_id),
    message: failure.message ? sanitizeDiagnosticText(failure.message) : null,
    model: failure.model ? sanitizeDiagnosticText(failure.model) : null,
    provider: failure.provider ? sanitizeDiagnosticText(failure.provider) : null,
    providerStatus: failure.provider_status
      ? sanitizeDiagnosticText(failure.provider_status)
      : null,
    stage: failure.stage ? sanitizeDiagnosticText(failure.stage) : null,
    status: sanitizeDiagnosticText(failure.status),
  };
}

function formatLimitLabel(dailyLimit: number | null, rateLimit: number | null): string {
  if (dailyLimit === null || rateLimit === null) {
    return "托管护栏未完整";
  }

  return `${dailyLimit}/day · ${rateLimit}/min`;
}

function formatMaxCostLabel(maxCost: string | null): string {
  return maxCost ? `<= ${maxCost} / job` : "成本上限未配置";
}

function formatBlockedReason(reason: string): string {
  if (reason.includes("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED")) {
    return "托管灰度开关关闭";
  }
  if (reason.includes("AI_PROVIDER_CALLS_ENABLED")) {
    return "托管调用开关关闭";
  }
  if (reason.includes("AI_PROVIDER_BFL_API_KEY")) {
    return "BFL 凭据未配置";
  }
  if (reason.includes("Hosted quota/rate/cost guards are incomplete")) {
    return "配额/频率/成本护栏未完整配置";
  }
  if (reason.includes("Provider status has not been refreshed")) {
    return "运维状态未刷新";
  }

  return sanitizeDiagnosticText(reason);
}

function sanitizeDiagnosticText(value: string): string {
  return value
    .replace(/[A-Z]:\\[^\s]+/g, "[local path redacted]")
    .replace(/api[_-]?key[^\s]*/gi, "[api key redacted]")
    .replace(/secret[^\s]*/gi, "[secret redacted]")
    .replace(/bearer\s+[^\s]+/gi, "Bearer [token redacted]")
    .replace(/sk-[^\s]+/gi, "[token redacted]");
}

function readStringArray(
  record: Record<string, unknown> | undefined,
  key: string,
): string[] {
  const value = record?.[key];
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === "string");
}

function readString(record: Record<string, unknown> | undefined, key: string): string {
  const value = record?.[key];
  return typeof value === "string" ? value : "";
}

function readNumber(record: Record<string, unknown> | undefined, key: string): number | null {
  const value = record?.[key];
  return typeof value === "number" ? value : null;
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return undefined;
  }

  return value as Record<string, unknown>;
}
