import {
  getProviderStatusOperationsProviderStatusGetUrl,
  type OperationsProviderStatusResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export interface OperationsApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export async function getProviderStatus(
  options: OperationsApiOptions = {},
): Promise<OperationsProviderStatusResponse> {
  return requestOperationsJson<OperationsProviderStatusResponse>(
    getProviderStatusOperationsProviderStatusGetUrl(),
    options,
  );
}

async function requestOperationsJson<T>(
  path: string,
  options: OperationsApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the operations client.");
  }

  const requestInit: RequestInit = { method: "GET" };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Operations request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
