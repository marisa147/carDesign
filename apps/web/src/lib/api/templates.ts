import {
  getGetTemplateTemplatesTemplateIdGetUrl,
  getGetTemplateThumbnailTemplatesTemplateIdThumbnailPngGetUrl,
  getListTemplatesTemplatesGetUrl,
  type ListTemplatesTemplatesGetParams,
  type TemplateCatalogItemResponse,
  type TemplateDetailResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export interface TemplateApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export async function listTemplates(
  params: ListTemplatesTemplatesGetParams = {},
  options: TemplateApiOptions = {},
): Promise<TemplateCatalogItemResponse[]> {
  return requestTemplateJson<TemplateCatalogItemResponse[]>(
    getListTemplatesTemplatesGetUrl(params),
    options,
  );
}

export async function getTemplate(
  templateId: string,
  options: TemplateApiOptions = {},
): Promise<TemplateDetailResponse> {
  return requestTemplateJson<TemplateDetailResponse>(
    getGetTemplateTemplatesTemplateIdGetUrl(templateId),
    options,
  );
}

export function templateThumbnailUrl(
  thumbnailPath: string,
  apiBaseUrl = publicEnv.apiBaseUrl,
): string {
  return `${apiBaseUrl}${thumbnailPath}`;
}

export function templateThumbnailPath(templateId: string): string {
  return getGetTemplateThumbnailTemplatesTemplateIdThumbnailPngGetUrl(templateId);
}

async function requestTemplateJson<T>(
  path: string,
  options: TemplateApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the template client.");
  }

  const requestInit: RequestInit = { method: "GET" };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Template request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
