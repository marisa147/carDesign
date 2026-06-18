import {
  getGetAssetAssetsAssetIdGetUrl,
  getListAssetsWorkspacesWorkspaceIdAssetsGetUrl,
  getUpdateAssetRightsAssetsAssetIdRightsPatchUrl,
  getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl,
  type AssetResponse,
  type AssetRightsUpdateRequest,
  type BodyUploadAssetWorkspacesWorkspaceIdAssetsPost,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export interface AssetApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export interface ReferenceEligibility {
  canUseForGeneration: boolean;
  label: "可用于生成" | "需确认权利";
  warning: "引用素材需要权利确认" | null;
}

export function getReferenceEligibility(asset: AssetResponse): ReferenceEligibility {
  if (asset.rights_status === "confirmed") {
    return {
      canUseForGeneration: true,
      label: "可用于生成",
      warning: null,
    };
  }

  return {
    canUseForGeneration: false,
    label: "需确认权利",
    warning: "引用素材需要权利确认",
  };
}

export async function uploadWorkspaceAsset(
  workspaceId: string,
  payload: BodyUploadAssetWorkspacesWorkspaceIdAssetsPost,
  options: AssetApiOptions = {},
): Promise<AssetResponse> {
  const formData = new FormData();
  formData.append("file", payload.file);
  if (payload.kind !== undefined) {
    formData.append("kind", payload.kind);
  }

  return requestAssetJson<AssetResponse>(
    getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl(workspaceId),
    "POST",
    formData,
    options,
  );
}

export async function listWorkspaceAssets(
  workspaceId: string,
  options: AssetApiOptions = {},
): Promise<AssetResponse[]> {
  return requestAssetJson<AssetResponse[]>(
    getListAssetsWorkspacesWorkspaceIdAssetsGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function getAsset(
  assetId: string,
  options: AssetApiOptions = {},
): Promise<AssetResponse> {
  return requestAssetJson<AssetResponse>(
    getGetAssetAssetsAssetIdGetUrl(assetId),
    "GET",
    undefined,
    options,
  );
}

export async function updateAssetRights(
  assetId: string,
  payload: AssetRightsUpdateRequest,
  options: AssetApiOptions = {},
): Promise<AssetResponse> {
  return requestAssetJson<AssetResponse>(
    getUpdateAssetRightsAssetsAssetIdRightsPatchUrl(assetId),
    "PATCH",
    payload,
    options,
  );
}

async function requestAssetJson<T>(
  path: string,
  method: "GET" | "PATCH" | "POST",
  body: FormData | unknown,
  options: AssetApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the asset client.");
  }

  const requestInit: RequestInit = { method };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }
  if (body instanceof FormData) {
    requestInit.body = body;
  } else if (body !== undefined) {
    requestInit.headers = { "Content-Type": "application/json" };
    requestInit.body = JSON.stringify(body);
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Asset request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
