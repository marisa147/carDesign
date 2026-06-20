"use client";

import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type {
  ArtifactResponse,
  AssetResponse,
  AssetRightsUpdateRequest,
  DesignVersionResponse,
  DesignBriefResponse,
  EditIntent,
  ExportResponse,
  FeedbackResponse,
  GenerationBriefResponse,
  GenerationBriefUpdateRequest,
  GenerationJobResponse,
  MessageResponse,
  OperationsProviderStatusResponse,
  ReferenceRole,
  TemplateCatalogItemResponse,
  WorkspaceResponse,
} from "@caragent/contracts";

import { Button } from "@/components/ui/button";
import { AssetPanel } from "@/components/workbench/asset-panel";
import { ChatPanel, type WorkbenchBrief } from "@/components/workbench/chat-panel";
import { ComparisonPanel } from "@/components/workbench/comparison-panel";
import {
  ExportPanel,
  handoffPackageDisclaimer,
  manifestDisclaimer,
  type ConceptExportFormat,
} from "@/components/workbench/export-panel";
import {
  FeedbackPanel,
  type FeedbackApprovalState,
} from "@/components/workbench/feedback-panel";
import { FutureGates } from "@/components/workbench/future-gates";
import { IterationPanel } from "@/components/workbench/iteration-panel";
import { ParameterPanel } from "@/components/workbench/parameter-panel";
import { PreviewPanel } from "@/components/workbench/preview-panel";
import { ProgressPanel } from "@/components/workbench/progress-panel";
import { WorkbenchShell } from "@/components/workbench/workbench-shell";
import {
  listWorkspaceAssets,
  updateAssetRights,
  uploadWorkspaceAsset,
} from "@/lib/api/assets";
import {
  DEFAULT_REFERENCE_ROLE,
  createGenerationBrief,
  loadGenerationState,
  retryGenerationJob,
  updateGenerationBrief,
  type GenerationState,
  type ReferenceUsageDraft,
} from "@/lib/api/generation";
import {
  createConceptExport,
  createProductionReadinessPreflight,
  createVersionFeedback,
  buildIterationSubmissionPayload,
  submitChildIteration,
  type ProductionReadinessPreflightReport,
} from "@/lib/api/iteration";
import { cancelGenerationJob, listWorkspaceJobs } from "@/lib/api/jobs";
import { listTemplates } from "@/lib/api/templates";
import { isV2EnhancedHandoffPackageEnabled } from "@/lib/config/public-env";
import {
  LOCAL_PROVIDER_ID,
  getProviderOption,
  getProviderStatus,
  normalizeProviderStatus,
} from "@/lib/api/operations";
import {
  createWorkspace,
  createWorkspaceMessage,
  listWorkspaceDesignBriefs,
  listWorkspaceMessages,
  resumeWorkspace,
} from "@/lib/api/workspaces";
import { workbenchQueryKeys } from "@/lib/workbench/query-keys";
import {
  DEFAULT_WORKBENCH_TEMPLATE_ID,
  useWorkbenchStore,
  type TargetedEditTarget,
} from "@/lib/workbench/store";

const WORKBENCH_WORKSPACE_ID_KEY = "caragent.workbench.workspaceId";
const WORKBENCH_BRIEF_ID_KEY = "caragent.workbench.briefId";

export function WorkbenchApp() {
  const queryClient = useQueryClient();
  const selectedVersionId = useWorkbenchStore((state) => state.selectedVersionId);
  const clearTargetedEditDraft = useWorkbenchStore((state) => state.clearTargetedEditDraft);
  const editPromptDelta = useWorkbenchStore((state) => state.editPromptDelta);
  const editRoutePreference = useWorkbenchStore((state) => state.editRoutePreference);
  const isTargetedEditMode = useWorkbenchStore((state) => state.isTargetedEditMode);
  const selectedEditTarget = useWorkbenchStore((state) => state.selectedEditTarget);
  const selectedTemplateId = useWorkbenchStore((state) => state.selectedTemplateId);
  const setEditPromptDelta = useWorkbenchStore((state) => state.setEditPromptDelta);
  const setSelectedTemplateId = useWorkbenchStore((state) => state.setSelectedTemplateId);
  const [draft, setDraft] = useState("");
  const [workspace, setWorkspace] = useState<WorkspaceResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [currentBrief, setCurrentBrief] = useState<WorkbenchBrief | null>(null);
  const [assets, setAssets] = useState<AssetResponse[]>([]);
  const [jobs, setJobs] = useState<GenerationJobResponse[]>([]);
  const [templates, setTemplates] = useState<TemplateCatalogItemResponse[]>([]);
  const [generationState, setGenerationState] = useState<GenerationState | null>(null);
  const [operationsStatus, setOperationsStatus] =
    useState<OperationsProviderStatusResponse | null>(null);
  const [selectedProviderId, setSelectedProviderId] = useState(LOCAL_PROVIDER_ID);
  const [referenceAssignments, setReferenceAssignments] = useState<ReferenceUsageDraft[]>([]);
  const [isCancelingGeneration, setIsCancelingGeneration] = useState(false);
  const [isLoadingGeneration, setIsLoadingGeneration] = useState(false);
  const [isRetryingGeneration, setIsRetryingGeneration] = useState(false);
  const [isLoadingSession, setIsLoadingSession] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [iterationDraft, setIterationDraft] = useState("");
  const [iterationError, setIterationError] = useState<string | null>(null);
  const [iterationNotice, setIterationNotice] = useState<string | null>(null);
  const [isSubmittingIteration, setIsSubmittingIteration] = useState(false);
  const [feedbackApprovalState, setFeedbackApprovalState] =
    useState<FeedbackApprovalState>("none");
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [feedbackNotice, setFeedbackNotice] = useState<string | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportFormat, setExportFormat] = useState<ConceptExportFormat>("png");
  const [exportNotice, setExportNotice] = useState<string | null>(null);
  const [preflightError, setPreflightError] = useState<string | null>(null);
  const [preflightNotice, setPreflightNotice] = useState<string | null>(null);
  const [preflightReport, setPreflightReport] =
    useState<ProductionReadinessPreflightReport | null>(null);
  const [isSubmittingExport, setIsSubmittingExport] = useState(false);
  const [isSubmittingPreflight, setIsSubmittingPreflight] = useState(false);

  const versions = generationState?.versions ?? [];
  const feedback = generationState?.feedback ?? [];
  const exports = generationState?.exports ?? [];
  const artifacts = generationState?.artifacts ?? [];
  const selectedVersion = selectSelectedVersion(versions, selectedVersionId);
  const selectedArtifact = selectArtifactForVersion(artifacts, selectedVersion);
  const providerStatus = normalizeProviderStatus(operationsStatus);
  const requestedProviderOption = getProviderOption(providerStatus, selectedProviderId);
  const effectiveProviderId =
    requestedProviderOption?.enabled === false ? LOCAL_PROVIDER_ID : selectedProviderId;
  const selectedProviderOption =
    getProviderOption(providerStatus, effectiveProviderId) ??
    getProviderOption(providerStatus, LOCAL_PROVIDER_ID) ??
    providerStatus.options[0];
  const selectedReferenceAssetIds = referenceAssignments
    .filter((assignment) => assignment.enabled)
    .map((assignment) => assignment.assetId);

  useEffect(() => {
    const storedWorkspaceId = readStoredId(WORKBENCH_WORKSPACE_ID_KEY);
    if (!storedWorkspaceId) {
      return;
    }

    let isCancelled = false;

    queueMicrotask(() => {
      if (!isCancelled) {
        setIsLoadingSession(true);
        setChatError(null);
      }
    });

    Promise.all([
      resumeWorkspace(storedWorkspaceId),
      listWorkspaceMessages(storedWorkspaceId),
      listWorkspaceDesignBriefs(storedWorkspaceId),
      listWorkspaceAssets(storedWorkspaceId),
      listWorkspaceJobs(storedWorkspaceId),
    ])
      .then(async ([nextWorkspace, nextMessages, nextBriefs, nextAssets, nextJobs]) => {
        const latestJob = selectLatestJob(nextJobs);
        const nextGenerationState = latestJob
          ? await loadGenerationState(nextWorkspace.id, latestJob.id)
          : null;

        if (isCancelled) {
          return;
        }

        const nextBrief = selectResumeBrief(
          nextBriefs,
          readStoredId(WORKBENCH_BRIEF_ID_KEY),
        );
        setWorkspace(nextWorkspace);
        setMessages(nextMessages);
        setCurrentBrief(nextBrief);
        setAssets(nextAssets);
        setJobs(nextJobs);
        setGenerationState(nextGenerationState);
        setReferenceAssignments(readBriefReferenceAssignments(nextBrief));
        setSelectedTemplateId(
          readBriefTemplateId(nextBrief) ?? DEFAULT_WORKBENCH_TEMPLATE_ID,
        );
        queryClient.setQueryData(
          workbenchQueryKeys.workspace(nextWorkspace.id),
          nextWorkspace,
        );
        queryClient.setQueryData(
          workbenchQueryKeys.messages(nextWorkspace.id),
          nextMessages,
        );
        queryClient.setQueryData(
          workbenchQueryKeys.briefs(nextWorkspace.id),
          nextBriefs,
        );
        queryClient.setQueryData(
          workbenchQueryKeys.assets(nextWorkspace.id),
          nextAssets,
        );
        queryClient.setQueryData(workbenchQueryKeys.jobs(nextWorkspace.id), nextJobs);
        if (nextGenerationState) {
          queryClient.setQueryData(
            workbenchQueryKeys.generationState(nextWorkspace.id, nextGenerationState.job.id),
            nextGenerationState,
          );
        }
        writeStoredId(WORKBENCH_WORKSPACE_ID_KEY, nextWorkspace.id);
        writeStoredId(WORKBENCH_BRIEF_ID_KEY, nextBrief?.id ?? null);
      })
      .catch(() => {
        if (!isCancelled) {
          setChatError("无法恢复工作台记录，请稍后重试。");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoadingSession(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [queryClient, setSelectedTemplateId]);

  useEffect(() => {
    let isCancelled = false;

    listTemplates({ catalog_eligible: true })
      .then((nextTemplates) => {
        if (isCancelled) {
          return;
        }
        setTemplates(nextTemplates);
        queryClient.setQueryData(workbenchQueryKeys.templates(), nextTemplates);
      })
      .catch(() => {
        if (!isCancelled) {
          setTemplates([]);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [queryClient]);

  const handleChatSubmit = async () => {
    const prompt = draft.trim();
    if (prompt.length === 0 || isSubmitting || isLoadingSession) {
      return;
    }

    setIsSubmitting(true);
    setChatError(null);

    try {
      const activeWorkspace =
        workspace ?? (await createWorkspace({ title: "痛车设计工作台" }));
      setWorkspace(activeWorkspace);
      writeStoredId(WORKBENCH_WORKSPACE_ID_KEY, activeWorkspace.id);
      queryClient.setQueryData(
        workbenchQueryKeys.workspace(activeWorkspace.id),
        activeWorkspace,
      );

      const userMessage = await createWorkspaceMessage(activeWorkspace.id, {
        content: prompt,
        role: "user",
      });
      const nextMessages = [...messages, userMessage];
      setMessages(nextMessages);
      queryClient.setQueryData(
        workbenchQueryKeys.messages(activeWorkspace.id),
        nextMessages,
      );

      const nextBrief = await createGenerationBrief(activeWorkspace.id, {
        original_request: userMessage.content,
        source_message_id: userMessage.id,
        title: "Workbench brief",
        vehicle_template_id: selectedTemplateId,
        view: "side",
      });
      setCurrentBrief(nextBrief);
      setSelectedTemplateId(readBriefTemplateId(nextBrief) ?? selectedTemplateId);
      setReferenceAssignments(readBriefReferenceAssignments(nextBrief));
      writeStoredId(WORKBENCH_BRIEF_ID_KEY, nextBrief.id);
      queryClient.setQueryData<WorkbenchBrief[]>(
        workbenchQueryKeys.briefs(activeWorkspace.id),
        (existing = []) => upsertBrief(existing, nextBrief),
      );
      setDraft("");
    } catch {
      setChatError("需求保存失败，请检查本地 API 后重试。");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleParameterSave = async (payload: GenerationBriefUpdateRequest) => {
    if (!currentBrief) {
      throw new Error("No active generation brief is available.");
    }

    const nextBrief = await updateGenerationBrief(currentBrief.id, payload);
    setCurrentBrief(nextBrief);
    setSelectedTemplateId(readBriefTemplateId(nextBrief) ?? selectedTemplateId);
    setReferenceAssignments(readBriefReferenceAssignments(nextBrief));
    writeStoredId(WORKBENCH_BRIEF_ID_KEY, nextBrief.id);
    queryClient.setQueryData<WorkbenchBrief[]>(
      workbenchQueryKeys.briefs(nextBrief.workspace_id),
      (existing = []) => upsertBrief(existing, nextBrief),
    );

    return nextBrief;
  };

  const handleTemplateChange = async (templateId: string) => {
    setSelectedTemplateId(templateId);
    if (!currentBrief) {
      return;
    }

    const nextBrief = await updateGenerationBrief(currentBrief.id, {
      vehicle_template_id: templateId,
      view: "side",
    });
    setCurrentBrief(nextBrief);
    setSelectedTemplateId(readBriefTemplateId(nextBrief) ?? templateId);
    setReferenceAssignments(readBriefReferenceAssignments(nextBrief));
    writeStoredId(WORKBENCH_BRIEF_ID_KEY, nextBrief.id);
    queryClient.setQueryData<WorkbenchBrief[]>(
      workbenchQueryKeys.briefs(nextBrief.workspace_id),
      (existing = []) => upsertBrief(existing, nextBrief),
    );
  };

  const handleAssetUpload = async ({ file, kind }: { file: File; kind: string }) => {
    if (!workspace) {
      throw new Error("No active workspace is available.");
    }

    const nextAsset = await uploadWorkspaceAsset(workspace.id, { file, kind });
    setAssets((existing) => {
      const nextAssets = upsertAsset(existing, nextAsset);
      queryClient.setQueryData(workbenchQueryKeys.assets(workspace.id), nextAssets);
      return nextAssets;
    });

    return nextAsset;
  };

  const refreshGenerationState = async () => {
    if (!workspace) {
      return;
    }

    setIsLoadingGeneration(true);
    try {
      const nextJobs = await listWorkspaceJobs(workspace.id);
      const latestJob = selectLatestJob(nextJobs);
      const nextGenerationState = latestJob
        ? await loadGenerationState(workspace.id, latestJob.id)
        : null;
      const nextOperationsStatus = await getProviderStatus().catch(() => null);
      setJobs(nextJobs);
      setGenerationState(nextGenerationState);
      setOperationsStatus(nextOperationsStatus);
      setSelectedProviderId(normalizeProviderStatus(nextOperationsStatus).activeProviderId);
      queryClient.setQueryData(workbenchQueryKeys.jobs(workspace.id), nextJobs);
      if (nextGenerationState) {
        queryClient.setQueryData(
          workbenchQueryKeys.generationState(workspace.id, nextGenerationState.job.id),
          nextGenerationState,
        );
      }
    } finally {
      setIsLoadingGeneration(false);
    }
  };

  const cancelCurrentGeneration = async () => {
    if (!generationState) {
      return;
    }

    setIsCancelingGeneration(true);
    try {
      const cancelResult = await cancelGenerationJob(generationState.job.id, {
        reason: "user_request",
        requested_by: "web-workbench",
      });
      setJobs((existing) => upsertJob(existing, cancelResult.job));
      setGenerationState((existing) =>
        existing ? { ...existing, job: cancelResult.job } : existing,
      );
    } finally {
      setIsCancelingGeneration(false);
    }
  };

  const retryCurrentGeneration = async () => {
    if (!generationState) {
      return;
    }

    setIsRetryingGeneration(true);
    try {
      const retryResult = await retryGenerationJob(generationState.job.id, {
        idempotency_key: `retry-${generationState.job.id}`,
        requested_by: "web-workbench",
      });
      setJobs((existing) => upsertJob(existing, retryResult.job));
      setGenerationState((existing) =>
        existing ? { ...existing, job: retryResult.job } : existing,
      );
    } finally {
      setIsRetryingGeneration(false);
    }
  };

  const submitSelectedIteration = async () => {
    const changeRequest = iterationDraft.trim();
    if (!workspace || !currentBrief || !selectedVersion || changeRequest.length === 0) {
      return;
    }

    const targetedEditResult = isTargetedEditMode
      ? buildTargetedEditIntent({
          artifact: selectedArtifact,
          promptDelta: editPromptDelta.trim() || changeRequest,
          routePreference: editRoutePreference,
          target: selectedEditTarget,
          version: selectedVersion,
        })
      : { editIntent: null, error: null };

    if (targetedEditResult.error) {
      setIterationError(targetedEditResult.error);
      setIterationNotice(null);
      return;
    }

    setIsSubmittingIteration(true);
    setIterationError(null);
    setIterationNotice(null);
    try {
      const result = await submitChildIteration(workspace.id, selectedVersion.id, {
        ...buildIterationSubmissionPayload(
          {
            brief_id: currentBrief.id,
            change_request: changeRequest,
            idempotency_key: `iteration-${selectedVersion.id}-${Date.now()}`,
            ...(targetedEditResult.editIntent
              ? { edit_intent: targetedEditResult.editIntent }
              : {}),
            parameter_overrides: {},
            requested_by: "web-workbench",
          },
          {
            providerSelection: selectedProviderOption,
            referenceAssignments,
          },
        ),
      });

      setJobs((existing) => {
        const nextJobs = upsertJob(existing, result.job);
        queryClient.setQueryData(workbenchQueryKeys.jobs(workspace.id), nextJobs);
        return nextJobs;
      });
      setGenerationState((existing) =>
        existing ? { ...existing, events: [], job: result.job } : existing,
      );
      queryClient.setQueryData(
        workbenchQueryKeys.iteration(workspace.id, selectedVersion.id),
        result,
      );
      setIterationDraft("");
      clearTargetedEditDraft();
      setIterationNotice("子迭代已提交，父版本仍保留。");
      await refreshGenerationState();
    } catch {
      setIterationError("子迭代提交失败，请稍后重试。");
    } finally {
      setIsSubmittingIteration(false);
    }
  };

  const submitSelectedFeedback = async () => {
    if (!workspace || !selectedVersion) {
      return;
    }

    setIsSubmittingFeedback(true);
    setFeedbackError(null);
    setFeedbackNotice(null);
    try {
      const savedFeedback = await createVersionFeedback(workspace.id, selectedVersion.id, {
        approval_state: feedbackApprovalState,
        comment: feedbackComment.trim() || null,
        metadata: { source: "web-workbench" },
        rating: feedbackRating,
      });
      setGenerationState((existing) =>
        existing
          ? {
              ...existing,
              feedback: upsertFeedback(existing.feedback, savedFeedback),
            }
          : existing,
      );
      queryClient.setQueryData<FeedbackResponse[]>(
        workbenchQueryKeys.feedback(workspace.id),
        (existing = []) => upsertFeedback(existing, savedFeedback),
      );
      setFeedbackApprovalState("none");
      setFeedbackComment("");
      setFeedbackRating(null);
      setFeedbackNotice("反馈已保存。");
    } catch {
      setFeedbackError("反馈保存失败，请稍后重试。");
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const submitSelectedExport = async () => {
    if (!workspace || !selectedVersion || !selectedArtifact) {
      return;
    }

    const isHandoffPackage = exportFormat === "enhanced_concept_handoff_zip";
    setIsSubmittingExport(true);
    setExportError(null);
    setExportNotice(null);
    try {
      const savedExport = await createConceptExport(workspace.id, selectedVersion.id, {
        artifact_id: selectedArtifact.id,
        concept_label: "client-review",
        format: exportFormat,
        manifest: {
          disclaimer: isHandoffPackage ? handoffPackageDisclaimer : manifestDisclaimer,
          ...referenceTraceManifest(selectedVersion.parameters),
          ...(isHandoffPackage
            ? handoffPackageRequestManifest({
                artifacts,
                selectedArtifact,
                selectedVersion,
              })
            : {}),
          ...templateTraceManifest(selectedVersion.parameters),
          source: "web-workbench",
          source_artifact_object_key: selectedArtifact.object_key,
          version_id: selectedVersion.id,
        },
      });
      setGenerationState((existing) =>
        existing
          ? {
              ...existing,
              exports: upsertExport(existing.exports, savedExport),
            }
          : existing,
      );
      queryClient.setQueryData<ExportResponse[]>(
        workbenchQueryKeys.exports(workspace.id),
        (existing = []) => upsertExport(existing, savedExport),
      );
      setExportNotice(isHandoffPackage ? "交接包导出已记录。" : "概念导出已记录。");
    } catch {
      setExportError("概念导出创建失败，请稍后重试。");
    } finally {
      setIsSubmittingExport(false);
    }
  };

  const runProductionPreflight = async () => {
    if (!workspace || !selectedVersion) {
      return;
    }

    setIsSubmittingPreflight(true);
    setPreflightError(null);
    setPreflightNotice(null);
    try {
      const result = await createProductionReadinessPreflight(
        workspace.id,
        selectedVersion.id,
      );
      setPreflightReport(result.report);
      setGenerationState((existing) =>
        existing
          ? {
              ...existing,
              exports: upsertExport(existing.exports, result.export),
            }
          : existing,
      );
      queryClient.setQueryData<ExportResponse[]>(
        workbenchQueryKeys.exports(workspace.id),
        (existing = []) => upsertExport(existing, result.export),
      );
      setPreflightNotice("生产预检已记录。");
    } catch {
      setPreflightError("生产预检失败，请稍后重试。");
    } finally {
      setIsSubmittingPreflight(false);
    }
  };

  const handleAssetRightsUpdate = async (
    assetId: string,
    payload: AssetRightsUpdateRequest,
  ) => {
    const nextAsset = await updateAssetRights(assetId, payload);
    setAssets((existing) => {
      const nextAssets = upsertAsset(existing, nextAsset);
      queryClient.setQueryData(workbenchQueryKeys.assets(nextAsset.workspace_id), nextAssets);
      return nextAssets;
    });

    return nextAsset;
  };

  const handleReferenceAssignmentChange = (
    assetId: string,
    changes: { enabled?: boolean; role?: ReferenceRole },
  ) => {
    setReferenceAssignments((existing) => {
      const current = existing.find((assignment) => assignment.assetId === assetId);
      const nextAssignment: ReferenceUsageDraft = {
        assetId,
        enabled: changes.enabled ?? current?.enabled ?? false,
        role: changes.role ?? current?.role ?? DEFAULT_REFERENCE_ROLE,
      };

      return [
        nextAssignment,
        ...existing.filter((assignment) => assignment.assetId !== assetId),
      ];
    });
  };

  return (
    <WorkbenchShell
      assets={
        <AssetPanel
          assets={assets}
          isLoading={isLoadingSession}
          onReferenceAssignmentChange={handleReferenceAssignmentChange}
          onRightsUpdate={handleAssetRightsUpdate}
          onUpload={handleAssetUpload}
          referenceAssignments={referenceAssignments}
          unsupportedReferenceRoles={
            selectedProviderOption?.referenceInput.unsupportedRoles ?? []
          }
          workspaceId={workspace?.id ?? null}
        />
      }
      chat={
        <ChatPanel
          currentBrief={currentBrief}
          draft={draft}
          error={chatError}
          isLoading={isLoadingSession}
          isSubmitting={isSubmitting}
          messages={messages}
          onDraftChange={setDraft}
          onSubmit={handleChatSubmit}
        />
      }
      futureGates={<FutureGates />}
      history={
        <div className="grid gap-4">
          <ComparisonPanel versions={versions} />
          <IterationPanel
            changeRequest={iterationDraft}
            error={iterationError}
            isSubmitting={isSubmittingIteration}
            notice={iterationNotice}
            onChangeRequestChange={(value) => {
              setIterationDraft(value);
              setEditPromptDelta(value);
              setIterationNotice(null);
              setIterationError(null);
            }}
            onSubmit={() => {
              void submitSelectedIteration();
            }}
            selectedVersion={selectedVersion}
            workspaceReady={workspace !== null && currentBrief !== null}
          />
          <FeedbackPanel
            approvalState={feedbackApprovalState}
            comment={feedbackComment}
            error={feedbackError}
            feedback={feedback}
            isSubmitting={isSubmittingFeedback}
            notice={feedbackNotice}
            onApprovalStateChange={(value) => {
              setFeedbackApprovalState(value);
              setFeedbackNotice(null);
              setFeedbackError(null);
            }}
            onCommentChange={(value) => {
              setFeedbackComment(value);
              setFeedbackNotice(null);
              setFeedbackError(null);
            }}
            onRatingChange={(value) => {
              setFeedbackRating(value);
              setFeedbackNotice(null);
              setFeedbackError(null);
            }}
            onSubmit={() => {
              void submitSelectedFeedback();
            }}
            rating={feedbackRating}
            selectedVersion={selectedVersion}
          />
          <ExportPanel
            artifact={selectedArtifact}
            artifacts={artifacts}
            enhancedHandoffEnabled={isV2EnhancedHandoffPackageEnabled()}
            error={exportError}
            exports={exports}
            format={exportFormat}
            isSubmitting={isSubmittingExport}
            isSubmittingPreflight={isSubmittingPreflight}
            notice={exportNotice}
            onFormatChange={(value) => {
              setExportFormat(value);
              setExportNotice(null);
              setExportError(null);
            }}
            onRunPreflight={() => {
              void runProductionPreflight();
            }}
            onSubmit={() => {
              void submitSelectedExport();
            }}
            preflightError={preflightError}
            preflightNotice={preflightNotice}
            preflightReport={preflightReport}
            selectedVersion={selectedVersion}
          />
        </div>
      }
      parameters={
        <ParameterPanel
          assets={assets}
          currentBrief={currentBrief}
          isLoading={isLoadingSession}
          key={`${currentBrief?.id ?? "empty-brief"}:${referenceAssignmentSignature(
            referenceAssignments,
          )}`}
          onSave={handleParameterSave}
          onTemplateChange={handleTemplateChange}
          onProviderChange={setSelectedProviderId}
          providerStatus={providerStatus}
          referenceAssignments={referenceAssignments}
          selectedReferenceAssetIds={selectedReferenceAssetIds}
          selectedTemplateId={readBriefTemplateId(currentBrief) ?? selectedTemplateId}
          selectedProviderId={selectedProviderOption?.id ?? LOCAL_PROVIDER_ID}
          templates={templates}
        />
      }
      preview={
        <PreviewPanel
          artifacts={generationState?.artifacts ?? []}
          isLoading={isLoadingGeneration || isLoadingSession}
          versions={versions}
        />
      }
      progress={
        <ProgressPanel
          events={generationState?.events ?? []}
          isCanceling={isCancelingGeneration}
          isLoading={isLoadingGeneration}
          isRetrying={isRetryingGeneration}
          job={generationState?.job ?? selectLatestJob(jobs)}
          operationsStatus={operationsStatus}
          onCancel={() => {
            void cancelCurrentGeneration();
          }}
          onRefresh={() => {
            void refreshGenerationState();
          }}
          onRetry={() => {
            void retryCurrentGeneration();
          }}
        />
      }
    />
  );
}

function readStoredId(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(key);
}

function writeStoredId(key: string, value: string | null) {
  if (typeof window === "undefined") {
    return;
  }

  if (value) {
    window.localStorage.setItem(key, value);
    return;
  }

  window.localStorage.removeItem(key);
}

function selectResumeBrief(
  briefs: DesignBriefResponse[],
  storedBriefId: string | null,
): WorkbenchBrief | null {
  if (briefs.length === 0) {
    return null;
  }

  return (
    briefs.find((brief) => brief.id === storedBriefId) ??
    [...briefs].sort((left, right) => right.updated_at.localeCompare(left.updated_at))[0] ??
    null
  );
}

function upsertBrief(
  existing: WorkbenchBrief[],
  nextBrief: GenerationBriefResponse,
): WorkbenchBrief[] {
  return [nextBrief, ...existing.filter((brief) => brief.id !== nextBrief.id)];
}

function upsertAsset(existing: AssetResponse[], nextAsset: AssetResponse): AssetResponse[] {
  return [nextAsset, ...existing.filter((asset) => asset.id !== nextAsset.id)];
}

function upsertJob(
  existing: GenerationJobResponse[],
  nextJob: GenerationJobResponse,
): GenerationJobResponse[] {
  return [nextJob, ...existing.filter((job) => job.id !== nextJob.id)];
}

function upsertFeedback(
  existing: FeedbackResponse[],
  nextFeedback: FeedbackResponse,
): FeedbackResponse[] {
  return [
    nextFeedback,
    ...existing.filter((feedback) => feedback.id !== nextFeedback.id),
  ];
}

function upsertExport(existing: ExportResponse[], nextExport: ExportResponse): ExportResponse[] {
  return [nextExport, ...existing.filter((entry) => entry.id !== nextExport.id)];
}

function selectLatestJob(jobs: GenerationJobResponse[]): GenerationJobResponse | null {
  if (jobs.length === 0) {
    return null;
  }

  return [...jobs].sort((left, right) => right.updated_at.localeCompare(left.updated_at))[0];
}

function selectSelectedVersion(
  versions: DesignVersionResponse[],
  selectedVersionId: string | null,
): DesignVersionResponse | null {
  return versions.find((version) => version.id === selectedVersionId) ?? versions[0] ?? null;
}

function selectArtifactForVersion(
  artifacts: ArtifactResponse[],
  selectedVersion: DesignVersionResponse | null,
): ArtifactResponse | null {
  if (!selectedVersion) {
    return null;
  }

  return (
    artifacts.find(
      (artifact) =>
        artifact.version_id === selectedVersion.id && artifact.kind === "generated_image",
    ) ?? null
  );
}

type TargetedEditIntentBuildResult =
  | { editIntent: EditIntent; error: null }
  | { editIntent: null; error: string | null };

function buildTargetedEditIntent({
  artifact,
  promptDelta,
  routePreference,
  target,
  version,
}: {
  artifact: ArtifactResponse | null;
  promptDelta: string;
  routePreference: EditIntent["route_preference"];
  target: TargetedEditTarget | null;
  version: DesignVersionResponse;
}): TargetedEditIntentBuildResult {
  if (!target) {
    return { editIntent: null, error: "请选择局部编辑目标。" };
  }

  if (
    !artifact ||
    !artifact.content_type ||
    !artifact.width ||
    !artifact.height ||
    artifact.width <= 0 ||
    artifact.height <= 0
  ) {
    return { editIntent: null, error: "无法创建编辑遮罩，请先选择有效预览图。" };
  }

  return {
    editIntent: {
      mask: {
        artifact_id: artifact.id,
        content_type: artifact.content_type,
        height: artifact.height,
        width: artifact.width,
      },
      mode: "targeted_edit",
      parent_version_id: version.id,
      prompt_delta: {
        instructions: [promptDelta],
        summary: promptDelta,
      },
      region: target.region,
      route_preference: routePreference,
      schema_version: 1,
      target: {
        id: target.id,
        type: target.type,
      },
    },
    error: null,
  };
}

function readBriefReferenceAssignments(brief: WorkbenchBrief | null): ReferenceUsageDraft[] {
  const usage = brief?.payload.reference_usage;
  if (Array.isArray(usage) && usage.length > 0) {
    return usage
      .filter(
        (item): item is { asset_id: string; enabled?: boolean; role: ReferenceRole } =>
          typeof item?.asset_id === "string" && typeof item?.role === "string",
      )
      .map((item) => ({
        assetId: item.asset_id,
        enabled: item.enabled !== false,
        role: item.role,
      }));
  }

  const value = brief?.payload.reference_asset_ids;
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === "string").map((assetId) => ({
    assetId,
    enabled: true,
    role: DEFAULT_REFERENCE_ROLE,
  }));
}

function readBriefTemplateId(brief: WorkbenchBrief | null): string | null {
  const value = brief?.payload.vehicle_template_id;
  return typeof value === "string" && value.trim().length > 0 ? value : null;
}

function referenceAssignmentSignature(assignments: ReferenceUsageDraft[]): string {
  return assignments
    .map((assignment) => `${assignment.assetId}:${assignment.role}:${assignment.enabled}`)
    .sort()
    .join(",");
}

const referenceTraceKeys = [
  "included_reference_asset_ids",
  "omitted_reference_asset_ids",
  "reference_roles",
  "reference_usage",
  "reference_warning_count",
  "rights_snapshot",
  "unsupported_reference_roles",
] as const;

function referenceTraceManifest(parameters: Record<string, unknown>): Record<string, unknown> {
  const trace: Record<string, unknown> = {};
  for (const key of referenceTraceKeys) {
    if (key in parameters) {
      trace[key] = parameters[key];
    }
  }
  return trace;
}

function templateTraceManifest(parameters: Record<string, unknown>): Record<string, unknown> {
  const previewSpec = parameters.preview_spec;
  if (!isRecord(previewSpec) || !isRecord(previewSpec.template)) {
    return {};
  }

  const template = previewSpec.template;
  return {
    preview_spec_template_id:
      typeof template.id === "string" ? template.id : null,
    preview_spec_template_view:
      typeof template.view === "string" ? template.view : null,
    vehicle_template: template,
  };
}

function handoffPackageRequestManifest({
  artifacts,
  selectedArtifact,
  selectedVersion,
}: {
  artifacts: ArtifactResponse[];
  selectedArtifact: ArtifactResponse;
  selectedVersion: DesignVersionResponse;
}): Record<string, unknown> {
  const preview3dScreenshotArtifactIds = artifacts
    .filter(
      (artifact) =>
        artifact.version_id === selectedVersion.id && artifact.kind === "preview_3d_screenshot",
    )
    .map((artifact) => artifact.id);

  return {
    package_type: "enhanced_concept_handoff",
    preview_3d_screenshot_artifact_ids: preview3dScreenshotArtifactIds,
    requested_files: [
      "manifest.json",
      "handoff-notes.md",
      "warnings.md",
      "production-readiness-preflight.json",
      "template-validation.json",
      "prompt-trace.md",
      "references.json",
      "images/concept.png",
    ],
    source_artifact_content_type: selectedArtifact.content_type,
    source_artifact_id: selectedArtifact.id,
    source_artifact_object_key: selectedArtifact.object_key,
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
