import { describe, expect, it, vi } from "vitest";

import {
  getGetAssetAssetsAssetIdGetUrl,
  getListAssetsWorkspacesWorkspaceIdAssetsGetUrl,
  getUpdateAssetRightsAssetsAssetIdRightsPatchUrl,
  getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl,
  type AssetResponse,
} from "@caragent/contracts";

import {
  getAsset,
  listWorkspaceAssets,
  updateAssetRights,
  uploadWorkspaceAsset,
} from "@/lib/api/assets";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const uploadedAt = "2026-06-17T00:00:00Z";

const assetFixture: AssetResponse = {
  byte_size: 128,
  checksum_sha256: "b".repeat(64),
  content_type: "image/png",
  created_at: uploadedAt,
  id: "asset-1",
  kind: "reference",
  object_key: "workspaces/workspace-1/uploads/asset-1/reference.png",
  original_filename: "reference.png",
  rights_confirmed_at: null,
  rights_notes: null,
  rights_status: "missing",
  source_label: null,
  source_url: null,
  thumbnail_object_key: null,
  updated_at: uploadedAt,
  workspace_id: "workspace-1",
};

describe("asset API wrappers", () => {
  it("uploads assets as multipart form data through generated route helpers", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(assetFixture, 201));
    const file = new File(["fake image"], "reference.png", { type: "image/png" });

    await expect(
      uploadWorkspaceAsset(
        "workspace-1",
        { file, kind: "logo" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(assetFixture);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl("workspace-1")}`,
      expect.objectContaining({
        method: "POST",
      }),
    );
    const request = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(request.headers).toBeUndefined();
    expect(request.body).toBeInstanceOf(FormData);
    const formData = request.body as FormData;
    expect(formData.get("file")).toBe(file);
    expect(formData.get("kind")).toBe("logo");
  });

  it("lists and reads assets with generated route helpers", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([assetFixture]))
      .mockResolvedValueOnce(jsonResponse(assetFixture));

    await expect(
      listWorkspaceAssets("workspace-1", {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual([assetFixture]);
    await expect(
      getAsset("asset-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual(assetFixture);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getListAssetsWorkspacesWorkspaceIdAssetsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getGetAssetAssetsAssetIdGetUrl("asset-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("updates asset rights and reports failed requests", async () => {
    const confirmedAsset = {
      ...assetFixture,
      rights_confirmed_at: uploadedAt,
      rights_notes: "User owns this logo.",
      rights_status: "confirmed",
      source_label: "Original upload",
    } satisfies AssetResponse;
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(confirmedAsset))
      .mockResolvedValueOnce(jsonResponse({ detail: "nope" }, 422));

    await expect(
      updateAssetRights(
        "asset-1",
        {
          rights_notes: "User owns this logo.",
          rights_status: "confirmed",
          source_label: "Original upload",
          source_url: null,
        },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(confirmedAsset);
    await expect(
      getAsset("missing", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).rejects.toThrow("Asset request failed with status 422");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getUpdateAssetRightsAssetsAssetIdRightsPatchUrl("asset-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          rights_notes: "User owns this logo.",
          rights_status: "confirmed",
          source_label: "Original upload",
          source_url: null,
        }),
        method: "PATCH",
      }),
    );
  });
});
