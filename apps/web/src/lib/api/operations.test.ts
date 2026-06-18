import { describe, expect, it, vi } from "vitest";

import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import { getProviderStatus } from "@/lib/api/operations";

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
    calls_enabled: false,
    default_provider: "disabled",
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
});
