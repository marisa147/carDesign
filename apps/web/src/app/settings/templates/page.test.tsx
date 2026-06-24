import "@/test/setup";

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import TemplateSettingsPage from "./page";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const catalogItem = {
  aliases: [],
  canvas_height: 900,
  canvas_width: 1600,
  id: "toyota_gr86_brz_v1",
  label: "Toyota GR86 / Subaru BRZ construction template",
  readiness: {
    blocking_reasons: [],
    catalog_eligible: true,
    missing_asset_slots: [],
    required_asset_slots: ["base", "thumbnail"],
    reusable_asset_allowed: true,
    warnings: [],
  },
  safe_zone_summary: [],
  source: {
    audit_timestamp: "2026-06-23T00:00:00Z",
    distribution_allowed: true,
    license_status: "approved",
    source_type: "internal_original",
  },
  supported_views: ["side", "front", "rear", "top"],
  thumbnail_url: "/templates/toyota_gr86_brz_v1/thumbnail.png",
  view: "side",
};

const detail = {
  ...catalogItem,
  asset_slots: { thumbnail: "thumbnail.png" },
  authorization: {
    authorization_file: "authorization/internal-gr86.md",
    commercial_use: true,
    expires_at: null,
    reviewer: "carAgent maintainers",
    scope: "concept preview and construction export",
    source: "internal_generated",
    version_history: [{ version: "1.0.0" }],
  },
  dimensions: { overall_length: 4265, overall_width: 1775 },
  export_config: { formats: ["svg", "pdf", "png"] },
  forbidden_zones: [{ id: "windshield" }],
  safe_zones: [{ id: "door" }],
  scale: { side: 2.66, unit: "mm_per_canvas_px" },
  sections: [{ id: "door-left" }, { id: "hood" }],
  view_assets: { side: { base: "side.png" } },
};

describe("TemplateSettingsPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows installed templates, authorization metadata, and validation results", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([catalogItem]))
      .mockResolvedValueOnce(jsonResponse(detail))
      .mockResolvedValueOnce(
        jsonResponse({
          accepted: false,
          authorization: null,
          files_checked: ["template.json"],
          issues: [
            {
              code: "missing_authorization_field",
              message: "Missing authorization field: reviewer.",
              path: "template.json",
              severity: "error",
            },
          ],
          label: "User GR86 demo",
          source_class: "user_provided",
          template_id: "user_gr86_demo_v1",
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<TemplateSettingsPage />);

    expect(await screen.findByRole("heading", { name: "模板管理" })).toBeVisible();
    expect(await screen.findByText("Toyota GR86 / Subaru BRZ construction template")).toBeVisible();
    expect(await screen.findByText("authorization/internal-gr86.md")).toBeVisible();
    expect(screen.getByText("2 条记录")).toBeVisible();

    const file = new File(["zip-bytes"], "template.zip", { type: "application/zip" });
    await user.upload(screen.getByLabelText(/选择模板 zip 包/), file);
    await user.click(screen.getByRole("button", { name: "校验模板包" }));

    await waitFor(() => {
      expect(screen.getByText("missing_authorization_field")).toBeVisible();
    });
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/templates/validate-package",
      expect.objectContaining({ body: expect.any(FormData), method: "POST" }),
    );
  });
});
