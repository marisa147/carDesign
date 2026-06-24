import "@/test/setup";

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import GptSettingsPage from "./page";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

describe("GptSettingsPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("saves GPT API settings and tells the user to restart services", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: false,
          api_key_masked: null,
          base_url: "https://api.openai.com/v1",
          calls_enabled: false,
          daily_call_limit: 6,
          default_provider: "disabled",
          image_model: "gpt-image-2",
          image_path: "/images/generations",
          image_url: "https://api.openai.com/v1/images/generations",
          max_estimated_cost_per_job: "0.9000",
          parser_enabled: false,
          rate_limit_per_minute: 2,
          responses_path: "/responses",
          restart_required: false,
          rollout_enabled: false,
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
    vi.stubGlobal("fetch", fetchMock);

    render(<GptSettingsPage />);

    expect(await screen.findByRole("heading", { name: "GPT 设置" })).toBeVisible();
    await user.type(screen.getByLabelText("OpenAI API Key"), "sk-openai-real-secret");
    await user.clear(screen.getByLabelText("每日调用上限"));
    await user.type(screen.getByLabelText("每日调用上限"), "8");
    await user.click(screen.getByRole("button", { name: "保存 GPT 设置" }));

    await waitFor(() => {
      expect(screen.getByText("设置已保存，重启 API 和 Worker 后生效。")).toBeVisible();
    });
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/operations/openai-settings",
      expect.objectContaining({
        body: expect.stringContaining("sk-openai-real-secret"),
        method: "POST",
      }),
    );
    expect(screen.queryByText("sk-openai-real-secret")).not.toBeInTheDocument();
  });

  it("separates GPT default provider from rollout state", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          api_key_configured: true,
          api_key_masked: "********cret",
          base_url: "https://api.openai.com/v1",
          calls_enabled: true,
          daily_call_limit: 6,
          default_provider: "disabled",
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
          daily_call_limit: 6,
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
    vi.stubGlobal("fetch", fetchMock);

    render(<GptSettingsPage />);

    const providerToggle = await screen.findByLabelText("GPT 默认托管");
    expect(providerToggle).not.toBeChecked();

    await user.click(providerToggle);
    await user.click(screen.getByRole("button", { name: "保存 GPT 设置" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenLastCalledWith(
        "http://localhost:8000/operations/openai-settings",
        expect.objectContaining({
          body: expect.stringContaining('"default_provider":"openai"'),
          method: "POST",
        }),
      );
    });
  });});

