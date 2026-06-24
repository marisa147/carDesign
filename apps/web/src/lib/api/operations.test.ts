import { describe, expect, it, vi } from "vitest";

import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import {
  BFL_PROVIDER_ID,
  LOCAL_PROVIDER_ID,
  getBflSettings,
  getOpenAISettings,
  getProviderOption,
  getProviderStatus,
  normalizeProviderStatus,
  updateBflSettings,
  updateOpenAISettings,
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
      expect.arrayContaining(["托管调用开关关闭", "BFL 凭据未配置"]),
    );
  });

  it("fetches and updates BFL settings without exposing the raw key", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: true,
          api_key_masked: "********cret",
          base_url: "https://api.bfl.ai",
          calls_enabled: true,
          daily_call_limit: 3,
          default_provider: "bfl",
          max_estimated_cost_per_job: "0.2500",
          model: "flux-2-pro-preview",
          rate_limit_per_minute: 1,
          restart_required: false,
          result_path: "/v1/get_result",
          rollout_enabled: true,
          submit_path: "/v1/flux-2-pro-preview",
          submit_url: "https://api.bfl.ai/v1/flux-2-pro-preview",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: true,
          api_key_masked: "********cret",
          base_url: "https://api.bfl.ai",
          calls_enabled: true,
          daily_call_limit: 5,
          default_provider: "bfl",
          max_estimated_cost_per_job: "0.2500",
          model: "flux-2-pro-preview",
          rate_limit_per_minute: 1,
          restart_required: true,
          result_path: "/v1/get_result",
          rollout_enabled: true,
          submit_path: "/v1/flux-2-pro-preview",
          submit_url: "https://api.bfl.ai/v1/flux-2-pro-preview",
        }),
      );

    await expect(
      getBflSettings({ apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toMatchObject({
      apiKeyConfigured: true,
      submitUrl: "https://api.bfl.ai/v1/flux-2-pro-preview",
    });
    await expect(
      updateBflSettings(
        {
          apiKey: "bfl-real-secret",
          baseUrl: "https://api.bfl.ai",
          callsEnabled: true,
          dailyCallLimit: 5,
          defaultProvider: "bfl",
          maxEstimatedCostPerJob: "0.2500",
          model: "flux-2-pro-preview",
          rateLimitPerMinute: 1,
          resultPath: "/v1/get_result",
          rolloutEnabled: true,
          submitPath: "/v1/flux-2-pro-preview",
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toMatchObject({ restartRequired: true });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://api.test/operations/bfl-settings",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://api.test/operations/bfl-settings",
      expect.objectContaining({
        body: expect.stringContaining("bfl-real-secret"),
        method: "POST",
      }),
    );
  });

  it("fetches and updates OpenAI GPT settings without exposing the raw key", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: true,
          api_key_masked: "********cret",
          base_url: "https://api.openai.com/v1",
          calls_enabled: true,
          daily_call_limit: 6,
          default_provider: "openai",
          image_model: "gpt-image-2",
          image_path: "/images/generations",
          image_url: "https://api.openai.com/v1/images/generations",
          max_estimated_cost_per_job: "0.9000",
          parser_enabled: true,
          rate_limit_per_minute: 2,
          responses_path: "/responses",
          restart_required: false,
          rollout_enabled: true,
          text_model: "gpt-5.5",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: true,
          api_key_masked: "********cret",
          base_url: "https://api.openai.com/v1",
          calls_enabled: true,
          daily_call_limit: 8,
          default_provider: "openai",
          image_model: "gpt-image-2",
          image_path: "/images/generations",
          image_url: "https://api.openai.com/v1/images/generations",
          max_estimated_cost_per_job: "0.9000",
          parser_enabled: true,
          rate_limit_per_minute: 2,
          responses_path: "/responses",
          restart_required: true,
          rollout_enabled: true,
          text_model: "gpt-5.5",
        }),
      );

    await expect(
      getOpenAISettings({ apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toMatchObject({
      apiKeyConfigured: true,
      imageUrl: "https://api.openai.com/v1/images/generations",
      parserEnabled: true,
    });
    await expect(
      updateOpenAISettings(
        {
          apiKey: "sk-openai-real-secret",
          baseUrl: "https://api.openai.com/v1",
          callsEnabled: true,
          dailyCallLimit: 8,
          defaultProvider: "openai",
          imageModel: "gpt-image-2",
          imagePath: "/images/generations",
          maxEstimatedCostPerJob: "0.9000",
          parserEnabled: true,
          rateLimitPerMinute: 2,
          responsesPath: "/responses",
          rolloutEnabled: true,
          textModel: "gpt-5.5",
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toMatchObject({ restartRequired: true });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://api.test/operations/openai-settings",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://api.test/operations/openai-settings",
      expect.objectContaining({
        body: expect.stringContaining("sk-openai-real-secret"),
        method: "POST",
      }),
    );
  });
});