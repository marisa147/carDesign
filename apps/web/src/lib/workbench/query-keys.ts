export const workbenchQueryKeys = {
  assets: (workspaceId: string) => ["assets", workspaceId] as const,
  briefs: (workspaceId: string) => ["briefs", workspaceId] as const,
  exports: (workspaceId: string) => ["exports", workspaceId] as const,
  feedback: (workspaceId: string) => ["feedback", workspaceId] as const,
  generationState: (workspaceId: string, jobId: string) =>
    ["generation-state", workspaceId, jobId] as const,
  iteration: (workspaceId: string, versionId: string) =>
    ["iteration", workspaceId, versionId] as const,
  jobs: (workspaceId: string) => ["jobs", workspaceId] as const,
  messages: (workspaceId: string) => ["messages", workspaceId] as const,
  templates: () => ["templates"] as const,
  workspace: (workspaceId: string) => ["workspace", workspaceId] as const,
};
