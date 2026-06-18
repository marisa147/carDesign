import {
  getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl,
  getCreateWorkspaceWorkspacesPostUrl,
  getGetWorkspaceWorkspacesWorkspaceIdGetUrl,
  getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl,
  getListMessagesWorkspacesWorkspaceIdMessagesGetUrl,
  type DesignBriefResponse,
  type MessageCreateRequest,
  type MessageResponse,
  type WorkspaceCreateRequest,
  type WorkspaceResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export interface WorkspaceApiOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

export async function createWorkspace(
  payload: WorkspaceCreateRequest,
  options: WorkspaceApiOptions = {},
): Promise<WorkspaceResponse> {
  return requestWorkspaceJson<WorkspaceResponse>(
    getCreateWorkspaceWorkspacesPostUrl(),
    "POST",
    payload,
    options,
  );
}

export async function resumeWorkspace(
  workspaceId: string,
  options: WorkspaceApiOptions = {},
): Promise<WorkspaceResponse> {
  return requestWorkspaceJson<WorkspaceResponse>(
    getGetWorkspaceWorkspacesWorkspaceIdGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function listWorkspaceMessages(
  workspaceId: string,
  options: WorkspaceApiOptions = {},
): Promise<MessageResponse[]> {
  return requestWorkspaceJson<MessageResponse[]>(
    getListMessagesWorkspacesWorkspaceIdMessagesGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function listWorkspaceDesignBriefs(
  workspaceId: string,
  options: WorkspaceApiOptions = {},
): Promise<DesignBriefResponse[]> {
  return requestWorkspaceJson<DesignBriefResponse[]>(
    getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl(workspaceId),
    "GET",
    undefined,
    options,
  );
}

export async function createWorkspaceMessage(
  workspaceId: string,
  payload: MessageCreateRequest,
  options: WorkspaceApiOptions = {},
): Promise<MessageResponse> {
  return requestWorkspaceJson<MessageResponse>(
    getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl(workspaceId),
    "POST",
    payload,
    options,
  );
}

async function requestWorkspaceJson<T>(
  path: string,
  method: "GET" | "POST",
  body: unknown,
  options: WorkspaceApiOptions,
): Promise<T> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const fetcher = options.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the workspace client.");
  }

  const requestInit: RequestInit = { method };
  if (options.signal !== undefined) {
    requestInit.signal = options.signal;
  }
  if (body !== undefined) {
    requestInit.headers = { "Content-Type": "application/json" };
    requestInit.body = JSON.stringify(body);
  }

  const response = await fetcher(`${apiBaseUrl}${path}`, requestInit);
  if (!response.ok) {
    throw new Error(`Workspace request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}
