import { describe, expect, it, vi } from "vitest";

import {
  getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl,
  getCreateWorkspaceWorkspacesPostUrl,
  getGetWorkspaceWorkspacesWorkspaceIdGetUrl,
  getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl,
  getListMessagesWorkspacesWorkspaceIdMessagesGetUrl,
  type DesignBriefResponse,
  type MessageResponse,
  type WorkspaceResponse,
} from "@caragent/contracts";

import {
  createWorkspace,
  createWorkspaceMessage,
  listWorkspaceDesignBriefs,
  listWorkspaceMessages,
  resumeWorkspace,
} from "@/lib/api/workspaces";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const workspaceFixture: WorkspaceResponse = {
  created_at: "2026-06-17T00:00:00Z",
  id: "workspace-1",
  owner_id: null,
  status: "active",
  title: "Sakura GT86",
  updated_at: "2026-06-17T00:00:00Z",
};

const messageFixture: MessageResponse = {
  content: "Make a pink itasha.",
  created_at: "2026-06-17T00:00:00Z",
  id: "message-1",
  role: "user",
  sequence: 1,
  updated_at: "2026-06-17T00:00:00Z",
  workspace_id: "workspace-1",
};

const designBriefFixture: DesignBriefResponse = {
  created_at: "2026-06-17T00:00:00Z",
  id: "brief-1",
  payload: {
    original_request: "Make a pink itasha.",
    style: "itasha concept",
  },
  source_message_id: "message-1",
  status: "draft",
  title: "Phase 4 brief",
  updated_at: "2026-06-17T00:00:00Z",
  workspace_id: "workspace-1",
};

describe("workspace API wrappers", () => {
  it("creates a workspace through the generated URL helper", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(workspaceFixture, 201));

    const result = await createWorkspace(
      { title: "Sakura GT86" },
      { apiBaseUrl: "http://api.test", fetch: fetchMock },
    );

    expect(result).toEqual(workspaceFixture);
    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getCreateWorkspaceWorkspacesPostUrl()}`,
      expect.objectContaining({
        body: JSON.stringify({ title: "Sakura GT86" }),
        method: "POST",
      }),
    );
  });

  it("resumes a workspace and lists messages using generated route helpers", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]));

    await expect(
      resumeWorkspace("workspace-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).resolves.toEqual(workspaceFixture);
    await expect(
      listWorkspaceMessages("workspace-1", {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual([messageFixture]);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getGetWorkspaceWorkspacesWorkspaceIdGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://api.test${getListMessagesWorkspacesWorkspaceIdMessagesGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("creates a message and throws useful errors on non-2xx responses", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(messageFixture, 201))
      .mockResolvedValueOnce(jsonResponse({ detail: "nope" }, 500));

    await expect(
      createWorkspaceMessage(
        "workspace-1",
        { content: "Make a pink itasha.", role: "user" },
        { apiBaseUrl: "http://api.test", fetch: fetchMock },
      ),
    ).resolves.toEqual(messageFixture);
    await expect(
      resumeWorkspace("workspace-1", { apiBaseUrl: "http://api.test", fetch: fetchMock }),
    ).rejects.toThrow("Workspace request failed with status 500");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://api.test${getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl("workspace-1")}`,
      expect.objectContaining({
        body: JSON.stringify({ content: "Make a pink itasha.", role: "user" }),
        method: "POST",
      }),
    );
  });

  it("lists durable design briefs for workspace resume", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([designBriefFixture]));

    await expect(
      listWorkspaceDesignBriefs("workspace-1", {
        apiBaseUrl: "http://api.test",
        fetch: fetchMock,
      }),
    ).resolves.toEqual([designBriefFixture]);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://api.test${getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });
});
