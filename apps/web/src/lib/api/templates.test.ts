import { describe, expect, it, vi } from "vitest";
import {
  getGetTemplateTemplatesTemplateIdGetUrl,
  getListTemplatesTemplatesGetUrl,
  type TemplateCatalogItemResponse,
  type TemplateDetailResponse,
} from "@caragent/contracts";

import {
  getTemplate,
  listTemplates,
  templateThumbnailPath,
  templateThumbnailUrl,
} from "@/lib/api/templates";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const templateFixture: TemplateCatalogItemResponse = {
  aliases: ["generic-side-coupe"],
  canvas_height: 768,
  canvas_width: 1536,
  id: "generic_coupe_side_v1",
  label: "Generic coupe side-view",
  readiness: {
    blocking_reasons: [],
    catalog_eligible: true,
    missing_asset_slots: [],
    required_asset_slots: ["base", "thumbnail"],
    reusable_asset_allowed: true,
    warnings: [],
  },
  safe_zone_summary: [
    {
      height: 0.24,
      id: "door-main",
      kind: "body",
      label: "Door / main side panel",
      width: 0.32,
      x: 0.33,
      y: 0.45,
    },
  ],
  source: {
    allowed_usage_scope: "mvp_concept_preview",
    audit_timestamp: "2026-06-19T14:40:00Z",
    distribution_allowed: true,
    license_evidence: "internal-mvp-generic-template-pack-v1",
    license_status: "approved",
    rights_notes: "Internal generic template.",
    source_type: "internal_original",
  },
  supported_views: ["side"],
  thumbnail_url: "/templates/generic_coupe_side_v1/thumbnail.png",
  view: "side",
};

describe("template API wrappers", () => {
  it("lists and fetches template metadata with generated route helpers", async () => {
    const detailFixture: TemplateDetailResponse = {
      ...templateFixture,
      asset_slots: { base: "base.png", thumbnail: "thumbnail.png" },
      safe_zones: [{ id: "door-main" }],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([templateFixture]))
      .mockResolvedValueOnce(jsonResponse(detailFixture));

    await expect(
      listTemplates(
        { catalog_eligible: true, view: "side" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual([templateFixture]);
    await expect(
      getTemplate("generic-side-coupe", {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual(detailFixture);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getListTemplatesTemplatesGetUrl({
        catalog_eligible: true,
        view: "side",
      })}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getGetTemplateTemplatesTemplateIdGetUrl("generic-side-coupe")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("builds thumbnail URLs without fetching binary content", () => {
    expect(templateThumbnailPath("generic_van_side_v1")).toBe(
      "/templates/generic_van_side_v1/thumbnail.png",
    );
    expect(
      templateThumbnailUrl("/templates/generic_van_side_v1/thumbnail.png", "http://api.test"),
    ).toBe("http://api.test/templates/generic_van_side_v1/thumbnail.png");
  });
});
