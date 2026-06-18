import { describe, expect, it, vi } from "vitest";

import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import {
  BFL_PROVIDER_ID,
  LOCAL_PROVIDER_ID,
  getProviderOption,
  getProviderStatus,
  normalizeProviderStatus,
} from "@/lib/api/operations";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const providerStatusFixture: OperationsProviderStatusResponse = {
  api_version: "0.1.0",
  provider: {
    active_mode: "local-deterministic",
    bfl_key_configured: false,
    capabilities: [
      {
        blocked_reasons: [],
        credential_configured: true,
        credential_required: false,
        default_model: "local-concept-v1",
        display_name: "Local deterministic",
        enabled: true,
        estimated_cost: null,
        provider: "local-deterministic",
      },
      {
        blocked_reasons: [
          "AI_PROVIDER_CALLS_ENABLED is disabled",
          "AI_PROVIDER_BFL_API_KEY is missing",
        ],
        credential_configured: false,
        credential_required: true,
        default_model: "flux-2-pro-preview",
        display_name: "BFL",
        enabled: false,
        estimated_cost: { max_per_job: null },
        provider: "bfl",
      },
    ],
    calls_enabled: false,
    default_provider: "disabled",
    guard_state: {
      daily_call_limit: null,
      hosted_quota_guard_enabled: false,
      max_estimated_cost_per_job: null,
      rate_limit_per_minute: null,
    },
    hosted_calls_blocked_reason: null,
    hosted_daily_call_limit: null,
    hosted_provider_configured: false,
    hosted_quota_guard_enabled: false,
    hosted_rate_limit_per_minute: null,
    max_estimated_cost_per_job: null,
    supported_providers: ["local-deterministic", "bfl"],
  },
  queue: {
    active_tasks: 0,
    active_workers: 0,
    detail: "No worker replied.",
    generation_queue: "caragent.default",
    registered_tasks: [],
    reserved_tasks: 0,
    status: "unavailable",
  },
  recent_failures: [],
  runtime_mode: "local",
  worker: {
    active_workers: 0,
    detail: "No worker replied.",
    status: "unavailable",
    task_name: "caragent_worker.generate_2d_concept_job",
  },
};

const hostedProviderStatusFixture: OperationsProviderStatusResponse = {
  ...providerStatusFixture,
  provider: {
    ...providerStatusFixture.provider,
    active_mode: "bfl",
    bfl_key_configured: true,
    capabilities: [
      providerStatusFixture.provider.capabilities?.[0] ?? {},
      {
        blocked_reasons: [],
        credential_configured: true,
        credential_required: true,
        default_model: "flux-2-pro-preview",
        display_name: "BFL",
        enabled: true,
        estimated_cost: { max_per_job: "0.7500" },
        provider: "bfl",
      },
    ],
    calls_enabled: true,
    default_provider: "bfl",
    guard_state: {
      daily_call_limit: 25,
      hosted_quota_guard_enabled: true,
      max_estimated_cost_per_job: "0.7500",
      rate_limit_per_minute: 4,
    },
    hosted_daily_call_limit: 25,
    hosted_provider_configured: true,
    hosted_quota_guard_enabled: true,
    hosted_rate_limit_per_minute: 4,
    max_estimated_cost_per_job: "0.7500",
  },
  recent_failures: [
    {
      created_at: "2026-06-17T00:20:00Z",
      failure_category: "provider",
      job_id: "job-1",
      message: "api_key sk-test failed at C:\\tmp\\provider.txt",
      model: "flux-2-pro-preview",
      provider: "bfl",
      provider_failure_kind: "rate_limit",
      provider_status: "rate_limited",
      stage: "provider_generate",
      status: "failed",
    },
  ],
};

describe("operations API wrappers", () => {
  it("fetches provider status through the generated operations route helper", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(providerStatusFixture))
      .mockResolvedValueOnce(jsonResponse({ detail: "offline" }, 503));

    await expect(
      getProviderStatus({ apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual(providerStatusFixture);
    await expect(
      getProviderStatus({ apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).rejects.toThrow("Operations request failed with status 503");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getProviderStatusOperationsProviderStatusGetUrl()}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("normalizes provider status into browser-safe selector options", () => {
    const status = normalizeProviderStatus(hostedProviderStatusFixture);

    expect(status.activeProviderId).toBe(BFL_PROVIDER_ID);
    expect(status.guardLabel).toBe("25/day · 4/min");
    expect(status.maxCostLabel).toBe("<= 0.7500 / job");
    expect(status.recentFailures[0]?.message).not.toMatch(
      /api[_-]?key|sk-test|[A-Z]:\\/i,
    );

    const local = getProviderOption(status, LOCAL_PROVIDER_ID);
    const bfl = getProviderOption(status, BFL_PROVIDER_ID);
    expect(local).toMatchObject({
      enabled: true,
      id: "local-deterministic",
      label: "本地概念",
      model: "local-concept-v1",
    });
    expect(bfl).toMatchObject({
      enabled: true,
      id: "bfl",
      label: "BFL 托管",
      model: "flux-2-pro-preview",
    });
  });

  it("keeps local available and hosted blocked when status is missing or disabled", () => {
    const missingStatus = normalizeProviderStatus(null);
    expect(getProviderOption(missingStatus, LOCAL_PROVIDER_ID)?.enabled).toBe(true);
    expect(getProviderOption(missingStatus, BFL_PROVIDER_ID)).toMatchObject({
      enabled: false,
      statusLabel: "未刷新",
    });

    const disabledStatus = normalizeProviderStatus(providerStatusFixture);
    const disabledBfl = getProviderOption(disabledStatus, BFL_PROVIDER_ID);
    expect(disabledBfl?.enabled).toBe(false);
    expect(disabledBfl?.blockedReasons).toEqual(
      expect.arrayContaining([
        "托管调用开关关闭",
        "BFL 凭据未配置",
      ]),
    );
  });
});
