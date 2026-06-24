import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type RecentFailureResponse,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export const LOCAL_PROVIDER_ID = "local-deterministic";
export const BFL_PROVIDER_ID = "bfl";
export const OPENAI_PROVIDER_ID = "openai";
const LOCAL_PROVIDER_MODEL = "local-concept-v1";
const BFL_DEFAULT_MODEL = "flux-2-pro-preview";
const OPENAI_DEFAULT_IMAGE_MODEL = "gpt-image-2";


export interface BflSettings {
  apiKeyConfigured: boolean;
  apiKeyMasked: string | null;
  baseUrl: string;
  callsEnabled: boolean;
  dailyCallLimit: number | null;
  defaultProvider: "bfl" | "disabled" | string;
  maxEstimatedCostPerJob: string | null;
  model: string;
  rateLimitPerMinute: number | null;
  restartRequired: boolean;
  resultPath: string;
  rolloutEnabled: boolean;
  submitPath: string;
  submitUrl: string;
}

export interface BflSettingsUpdate {
  apiKey?: string | null;
  baseUrl: string;
  callsEnabled: boolean;
  dailyCallLimit: number | null;
  defaultProvider: "bfl" | "disabled";
  maxEstimatedCostPerJob: string | null;
  model: string;
  rateLimitPerMinute: number | null;
  resultPath: string;
  rolloutEnabled: boolean;
  submitPath: string;
}

interface RawBflSettingsResponse {
  api_key_configured: boolean;
  api_key_masked: string | null;
  base_url: string;
  calls_enabled: boolean;
  daily_call_limit: number | null;
  default_provider: string;
  max_estimated_cost_per_job: string | null;
  model: string;
  rate_limit_per_minute: number | null;
  restart_required: boolean;
  result_path: string;
  rollout_enabled: boolean;
  submit_path: string;
  submit_url: string;
}
export interface OpenAISettings {
  apiKeyConfigured: boolean;
  apiKeyMasked: string | null;
  baseUrl: string;
  callsEnabled: boolean;
  dailyCallLimit: number | null;
  defaultProvider: "openai" | "disabled" | string;
  imageModel: string;
  imagePath: string;
  imageUrl: string;
  maxEstimatedCostPerJob: string | null;
  parserEnabled: boolean;
  rateLimitPerMinute: number | null;
  responsesPath: string;
  restartRequired: boolean;
  rolloutEnabled: boolean;
  textModel: string;
}

export interface OpenAISettingsUpdate {
  apiKey?: string | null;
  baseUrl: string;
  callsEnabled: boolean;
  dailyCallLimit: number | null;
  defaultProvider: "openai" | "disabled";
  imageModel: string;
  imagePath: string;
  maxEstimatedCostPerJob: string | null;
  parserEnabled: boolean;
  rateLimitPerMinute: number | null;
  responsesPath: string;
  rolloutEnabled: boolean;
  textModel: string;
}

interface RawOpenAISettingsResponse {
  api_key_configured: boolean;
  api_key_masked: string | null;
  base_url: string;
  calls_enabled: boolean;
  daily_call_limit: number | null;
  default_provider: string;
  image_model: string;
  image_path: string;
  image_url: string;
  max_estimated_cost_per_job: string | null;
  parser_enabled: boolean;
  rate_limit_per_minute: number | null;
  responses_path: string;
  restart_required: boolean;
  rollout_enabled: boolean;
  text_model: string;
}
export interface OperationsApiOptions {
  apiBaseUrl?: string;
  body?: BodyInit | null;
  fetch?: typeof fetch;
  headers?: HeadersInit;
  method?: string;
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
  referenceInput: WorkbenchReferenceInput;
  statusLabel: string;
}

export interface WorkbenchReferenceInput {
  accepted: boolean;
  blockedReason: string | null;
  promptGuidanceRoles: string[];
  supportLabel: string;
  supportedRoles: string[];
  unsupportedRoles: string[];
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


export async function getBflSettings(
  options: OperationsApiOptions = {},
): Promise<BflSettings> {
  const response = await requestOperationsJson<RawBflSettingsResponse>(
    "/operations/bfl-settings",
    options,
  );
  return normalizeBflSettings(response);
}

export async function updateBflSettings(
  input: BflSettingsUpdate,
  options: OperationsApiOptions = {},
): Promise<BflSettings> {
  const response = await requestOperationsJson<RawBflSettingsResponse>(
    "/operations/bfl-settings",
    {
      ...options,
      body: JSON.stringify({
        api_key: input.apiKey,
        base_url: input.baseUrl,
        calls_enabled: input.callsEnabled,
        daily_call_limit: input.dailyCallLimit,
        default_provider: input.defaultProvider,
        max_estimated_cost_per_job: input.maxEstimatedCostPerJob,
        model: input.model,
        rate_limit_per_minute: input.rateLimitPerMinute,
        result_path: input.resultPath,
        rollout_enabled: input.rolloutEnabled,
        submit_path: input.submitPath,
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    },
  );
  return normalizeBflSettings(response);
}

export async function getOpenAISettings(
  options: OperationsApiOptions = {},
): Promise<OpenAISettings> {
  const response = await requestOperationsJson<RawOpenAISettingsResponse>(
    "/operations/openai-settings",
    options,
  );
  return normalizeOpenAISettings(response);
}

export async function updateOpenAISettings(
  input: OpenAISettingsUpdate,
  options: OperationsApiOptions = {},
): Promise<OpenAISettings> {
  const response = await requestOperationsJson<RawOpenAISettingsResponse>(
    "/operations/openai-settings",
    {
      ...options,
      body: JSON.stringify({
        api_key: input.apiKey,
        base_url: input.baseUrl,
        calls_enabled: input.callsEnabled,
        daily_call_limit: input.dailyCallLimit,
        default_provider: input.defaultProvider,
        image_model: input.imageModel,
        image_path: input.imagePath,
        max_estimated_cost_per_job: input.maxEstimatedCostPerJob,
        parser_enabled: input.parserEnabled,
        rate_limit_per_minute: input.rateLimitPerMinute,
        responses_path: input.responsesPath,
        rollout_enabled: input.rolloutEnabled,
        text_model: input.textModel,
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    },
  );
  return normalizeOpenAISettings(response);
}export async function getProviderStatus(
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
  const openAIOption = buildOpenAIProviderOption({
    capability: capabilities.get(OPENAI_PROVIDER_ID),
    guardLabel,
    maxCostLabel,
    status,
  });
  const activeProviderId =
    provider?.active_mode === OPENAI_PROVIDER_ID && openAIOption.enabled
      ? OPENAI_PROVIDER_ID
      : provider?.active_mode === BFL_PROVIDER_ID && bflOption.enabled
        ? BFL_PROVIDER_ID
        : LOCAL_PROVIDER_ID;

  return {
    activeProviderId,
    guardLabel,
    maxCostLabel,
    options: [localOption, bflOption, openAIOption],
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

  const requestInit: RequestInit = {
    body: options.body,
    headers: options.headers,
    method: options.method ?? "GET",
  };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Operations request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}


function normalizeBflSettings(response: RawBflSettingsResponse): BflSettings {
  return {
    apiKeyConfigured: response.api_key_configured,
    apiKeyMasked: response.api_key_masked,
    baseUrl: response.base_url,
    callsEnabled: response.calls_enabled,
    dailyCallLimit: response.daily_call_limit,
    defaultProvider: response.default_provider,
    maxEstimatedCostPerJob: response.max_estimated_cost_per_job,
    model: response.model,
    rateLimitPerMinute: response.rate_limit_per_minute,
    restartRequired: response.restart_required,
    resultPath: response.result_path,
    rolloutEnabled: response.rollout_enabled,
    submitPath: response.submit_path,
    submitUrl: response.submit_url,
  };
}

function normalizeOpenAISettings(response: RawOpenAISettingsResponse): OpenAISettings {
  return {
    apiKeyConfigured: response.api_key_configured,
    apiKeyMasked: response.api_key_masked,
    baseUrl: response.base_url,
    callsEnabled: response.calls_enabled,
    dailyCallLimit: response.daily_call_limit,
    defaultProvider: response.default_provider,
    imageModel: response.image_model,
    imagePath: response.image_path,
    imageUrl: response.image_url,
    maxEstimatedCostPerJob: response.max_estimated_cost_per_job,
    parserEnabled: response.parser_enabled,
    rateLimitPerMinute: response.rate_limit_per_minute,
    responsesPath: response.responses_path,
    restartRequired: response.restart_required,
    rolloutEnabled: response.rollout_enabled,
    textModel: response.text_model,
  };
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
    referenceInput: normalizeReferenceInput(capability),
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
    referenceInput: normalizeReferenceInput(capability),
    statusLabel: status ? (enabled ? "可用" : "暂不可用") : "未刷新",
  };
}
function buildOpenAIProviderOption({
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
  const inferredBlockedReasons = inferOpenAIBlockedReasons(status);
  const blockedReasons = (
    rawBlockedReasons.length > 0 ? rawBlockedReasons : inferredBlockedReasons
  ).map(formatBlockedReason);
  const openAIKeyConfigured = Boolean(
    asRecord(provider)?.openai_key_configured,
  );
  const enabled =
    typeof capability?.enabled === "boolean"
      ? capability.enabled && blockedReasons.length === 0
      : Boolean(
          provider?.calls_enabled &&
            openAIKeyConfigured &&
            provider.hosted_provider_configured &&
            provider.hosted_quota_guard_enabled &&
            !provider.hosted_calls_blocked_reason,
        );
  const model = readString(capability, "default_model") || OPENAI_DEFAULT_IMAGE_MODEL;

  return {
    blockedReasons,
    conceptLabel: "GPT 概念预览",
    enabled,
    guardLabel,
    id: OPENAI_PROVIDER_ID,
    label: "GPT 托管",
    maxCostLabel,
    model,
    referenceInput: normalizeReferenceInput(capability),
    statusLabel: status ? (enabled ? "可用" : "暂不可用") : "未刷新",
  };
}

function normalizeReferenceInput(
  capability: Record<string, unknown> | undefined,
): WorkbenchReferenceInput {
  const referenceInput = asRecord(capability?.reference_input);
  const accepted = Boolean(referenceInput?.accepted);
  const promptGuidanceRoles = readStringArray(referenceInput, "prompt_guidance_roles");
  const supportedRoles = readStringArray(referenceInput, "supported_roles");
  const unsupportedRoles = readStringArray(referenceInput, "unsupported_roles");
  const blockedReason = readString(referenceInput, "blocked_reason") || null;
  const supportLabel = accepted
    ? "accepted"
    : promptGuidanceRoles.length > 0
      ? "prompt-only"
      : "unsupported";

  return {
    accepted,
    blockedReason,
    promptGuidanceRoles,
    supportLabel,
    supportedRoles,
    unsupportedRoles,
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
function inferOpenAIBlockedReasons(status: OperationsProviderStatusResponse | null): string[] {
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
  if (!asRecord(provider)?.openai_key_configured) {
    reasons.push("AI_PROVIDER_OPENAI_API_KEY is missing");
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
  if (
    reason.includes("AI_PROVIDER_OPENAI_API_KEY") ||
    reason.includes("OpenAI credential is missing")
  ) {
    return "OpenAI 凭据未配置";
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
