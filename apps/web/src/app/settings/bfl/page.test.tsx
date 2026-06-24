import "@/test/setup";

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import BflSettingsPage from "./page";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

describe("BflSettingsPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("saves BFL settings and tells the user to restart services", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: false,
          api_key_masked: null,
          base_url: "https://api.bfl.ai",
          calls_enabled: false,
          daily_call_limit: 3,
          default_provider: "disabled",
          max_estimated_cost_per_job: "0.2500",
          model: "flux-2-pro-preview",
          rate_limit_per_minute: 1,
          restart_required: false,
          result_path: "/v1/get_result",
          rollout_enabled: false,
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
    vi.stubGlobal("fetch", fetchMock);

    render(<BflSettingsPage />);

    expect(await screen.findByRole("heading", { name: "BFL 托管设置" })).toBeVisible();
    await user.type(screen.getByLabelText("BFL API Key"), "bfl-real-secret");
    await user.clear(screen.getByLabelText("每日调用上限"));
    await user.type(screen.getByLabelText("每日调用上限"), "5");
    await user.click(screen.getByRole("button", { name: "保存 BFL 设置" }));

    await waitFor(() => {
      expect(screen.getByText("设置已保存，重启 API 和 Worker 后生效。")).toBeVisible();
    });
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/operations/bfl-settings",
      expect.objectContaining({
        body: expect.stringContaining("bfl-real-secret"),
        method: "POST",
      }),
    );
    expect(screen.queryByText("bfl-real-secret")).not.toBeInTheDocument();
  });
});