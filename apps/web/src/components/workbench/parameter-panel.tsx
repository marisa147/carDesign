"use client";

import type {
  AssetResponse,
  GenerationBriefPayload,
  GenerationBriefResponse,
  GenerationBriefUpdateRequest,
  ReferenceAssignment,
  ReferenceRole,
  TemplateCatalogItemResponse,
  TemplateDetailResponse,
} from "@caragent/contracts";
import {
  AlertTriangle,
  Archive,
  CheckCircle2,
  Cloud,
  Cpu,
  Loader2,
  Plus,
  Save,
  ShieldAlert,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { WorkbenchBrief } from "@/components/workbench/chat-panel";
import { getReferenceEligibility } from "@/lib/api/assets";
import {
  REFERENCE_ROLE_OPTIONS,
  buildReferenceUsagePayload,
  type ReferenceUsageDraft,
} from "@/lib/api/generation";
import {
  BFL_PROVIDER_ID,
  LOCAL_PROVIDER_ID,
  type WorkbenchProviderOption,
  type WorkbenchProviderStatus,
} from "@/lib/api/operations";
import { templateThumbnailUrl } from "@/lib/api/templates";

interface ParameterPanelProps {
  assets: AssetResponse[];
  currentBrief: WorkbenchBrief | null;
  generationError: string | null;
  isGenerating: boolean;
  isLoading: boolean;
  onArchive: () => Promise<void>;
  onGenerate: () => Promise<void>;
  onNewConcept: () => void;
  onSave: (payload: GenerationBriefUpdateRequest) => Promise<GenerationBriefResponse>;
  onTemplateChange: (templateId: string) => Promise<void>;
  onProviderChange: (providerId: string) => void;
  onSectionSelect: (section: TemplateSectionSelection) => void;
  providerStatus: WorkbenchProviderStatus;
  referenceAssignments: ReferenceUsageDraft[];
  selectedReferenceAssetIds: string[];
  selectedTemplateId: string;
  selectedProviderId: string;
  templateDetail: TemplateDetailResponse | null;
  templates: TemplateCatalogItemResponse[];
}

interface TemplateSectionSelection {
  bounds: {
    height: number;
    width: number;
    x: number;
    y: number;
  };
  id: string;
  label: string;
  realSizeLabel: string;
  view: "front" | "rear" | "side" | "top";
  views: string[];
}

interface TemplateSectionRecord {
  bounds?: {
    height?: unknown;
    width?: unknown;
    x?: unknown;
    y?: unknown;
  };
  id?: unknown;
  label?: unknown;
  real_size_mm?: {
    height?: unknown;
    width?: unknown;
  };
  views?: unknown;
}

interface ParameterDraft {
  characterFocus: string;
  characterTheme: string;
  colorHarmony: string;
  coverage: string;
  overlayLogoAssetIdsText: string;
  paletteText: string;
  racingCuesText: string;
  referenceAssetIdsText: string;
  style: string;
  supportingGraphicsText: string;
  textText: string;
  typographyIntent: string;
}

type SaveState = "idle" | "saving" | "saved" | "error";
type StringUpdateKey =
  | "character_focus"
  | "character_theme"
  | "color_harmony"
  | "coverage"
  | "style"
  | "typography_intent";

type ArrayUpdateKey =
  | "overlay_logo_asset_ids"
  | "palette"
  | "racing_cues"
  | "reference_asset_ids"
  | "supporting_graphics"
  | "text";

export function ParameterPanel({
  assets,
  currentBrief,
  generationError,
  isGenerating,
  isLoading,
  onArchive,
  onGenerate,
  onNewConcept,
  onSave,
  onTemplateChange,
  onProviderChange,
  onSectionSelect,
  providerStatus,
  referenceAssignments,
  selectedReferenceAssetIds,
  selectedTemplateId,
  selectedProviderId,
  templateDetail,
  templates,
}: ParameterPanelProps) {
  const [draft, setDraft] = useState(() =>
    createDraft(currentBrief, selectedReferenceAssetIds),
  );
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [archiveState, setArchiveState] = useState<SaveState>("idle");
  const [referenceAssetIdsTextTouched, setReferenceAssetIdsTextTouched] = useState(false);
  const effectiveReferenceAssetIdsText = referenceAssetIdsTextTouched
    ? draft.referenceAssetIdsText
    : selectedReferenceAssetIds.join("\n");
  const effectiveDraft = {
    ...draft,
    referenceAssetIdsText: effectiveReferenceAssetIdsText,
  };
  const payload = currentBrief ? readPayload(currentBrief) : {};
  const templateSections = readTemplateSections(templateDetail);
  const activeTemplateId = readString(payload, "vehicle_template_id") || selectedTemplateId;
  const handleTemplateSelect = async (templateId: string) => {
    setSaveState("saving");
    try {
      await onTemplateChange(templateId);
      setSaveState("saved");
    } catch {
      setSaveState("error");
    }
  };

  if (!currentBrief) {
    return (
      <div className="grid gap-3 text-sm">
        <TemplateCatalogSelector
          activeTemplateId={activeTemplateId}
          isLoading={isLoading}
          onTemplateSelect={handleTemplateSelect}
          templates={templates}
        />
        <InfoRow label="视角" value="side" />
        <InfoRow label="风格" value="等待 brief" />
        <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
          先发送设计需求以生成结构化 brief。
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <Button disabled type="button" variant="outline">
            <SlidersHorizontal aria-hidden="true" className="h-4 w-4" />
            保存参数
          </Button>
          <Button disabled type="button">
            <Sparkles aria-hidden="true" className="h-4 w-4" />
            生成概念
          </Button>
        </div>
      </div>
    );
  }

  const updatePayload = buildUpdatePayload(payload, effectiveDraft, referenceAssignments);
  const isDirty = Object.keys(updatePayload).length > 0;
  const isArchived = currentBrief.status === "archived";
  const canSave = isDirty && saveState !== "saving" && !isLoading;
  const canGenerate = saveState !== "saving" && !isLoading && !isGenerating;
  const canArchive = !isArchived && archiveState !== "saving" && saveState !== "saving" && !isLoading && !isGenerating;

  const handleSave = async () => {
    if (!canSave) {
      return;
    }

    setSaveState("saving");
    try {
      const updatedBrief = await onSave(updatePayload);
      setDraft(createDraft(updatedBrief));
      setReferenceAssetIdsTextTouched(false);
      setSaveState("saved");
    } catch {
      setSaveState("error");
    }
  };

  const handleGenerate = async () => {
    if (!canGenerate) {
      return;
    }

    setSaveState("saving");
    try {
      if (isDirty) {
        const updatedBrief = await onSave(updatePayload);
        setDraft(createDraft(updatedBrief));
        setReferenceAssetIdsTextTouched(false);
      }
      setSaveState("saved");
      await onGenerate();
    } catch {
      setSaveState("error");
    }
  };

  const handleNewConcept = () => {
    setSaveState("idle");
    setArchiveState("idle");
    setReferenceAssetIdsTextTouched(false);
    onNewConcept();
  };

  const handleArchive = async () => {
    if (!canArchive) {
      return;
    }

    setArchiveState("saving");
    try {
      await onArchive();
      setArchiveState("saved");
    } catch {
      setArchiveState("error");
    }
  };

  return (
    <div className="grid gap-3 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <InfoRow label="车型模板" value={readString(payload, "vehicle_template_label") || "-"} />
        <InfoRow label="视角" value={readString(payload, "view") || "-"} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <InfoRow label="概念状态" value={formatBriefStatus(currentBrief.status)} />
        <InfoRow label="画布" value={formatCanvas(payload)} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button disabled={archiveState === "saving" || saveState === "saving" || isLoading} onClick={handleNewConcept} type="button" variant="outline">
          <Plus aria-hidden="true" className="h-4 w-4" />
          新建概念
        </Button>
        <Button disabled={!canArchive} onClick={handleArchive} type="button" variant="outline">
          {archiveState === "saving" ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <Archive aria-hidden="true" className="h-4 w-4" />
          )}
          作废当前
        </Button>
        {archiveState === "error" ? (
          <span className="inline-flex items-center gap-1 text-sm font-medium text-destructive" role="alert">
            <AlertTriangle aria-hidden="true" className="h-4 w-4" />
            作废失败
          </span>
        ) : null}
      </div>
      <TemplateCatalogSelector
        activeTemplateId={activeTemplateId}
        isLoading={isLoading || saveState === "saving"}
        onTemplateSelect={handleTemplateSelect}
        templates={templates}
      />
      <ProviderSelector
        onProviderChange={onProviderChange}
        providerStatus={providerStatus}
        selectedProviderId={selectedProviderId}
      />
      <ReferenceSummary
        assets={assets}
        referenceAssignments={referenceAssignments}
        selectedProvider={
          providerStatus.options.find((option) => option.id === selectedProviderId) ??
          providerStatus.options.find((option) => option.id === LOCAL_PROVIDER_ID) ??
          providerStatus.options[0]
        }
      />
      <ConstructionBriefSummary payload={payload} />
      <SectionWorkspace
        onSectionSelect={onSectionSelect}
        sections={templateSections}
        templateId={activeTemplateId}
      />

      <TextInput
        id="parameter-character-theme"
        label="角色主题"
        onChange={(value) => {
          setDraft((current) => ({ ...current, characterTheme: value }));
          setSaveState("idle");
        }}
        value={draft.characterTheme}
      />
      <section className="grid gap-3 rounded-md border border-border bg-card p-3">
        <div>
          <h3 className="text-sm font-semibold">痛车设计控制</h3>
        </div>
        <TextInput
          id="parameter-character-focus"
          label="角色焦点"
          onChange={(value) => {
            setDraft((current) => ({ ...current, characterFocus: value }));
            setSaveState("idle");
          }}
          value={draft.characterFocus}
        />
        <TextArea
          id="parameter-supporting-graphics"
          label="辅助图形"
          onChange={(value) => {
            setDraft((current) => ({ ...current, supportingGraphicsText: value }));
            setSaveState("idle");
          }}
          value={draft.supportingGraphicsText}
        />
        <TextArea
          id="parameter-racing-cues"
          label="赛车/JDM 元素"
          onChange={(value) => {
            setDraft((current) => ({ ...current, racingCuesText: value }));
            setSaveState("idle");
          }}
          value={draft.racingCuesText}
        />
        <TextInput
          id="parameter-typography-intent"
          label="字体意图"
          onChange={(value) => {
            setDraft((current) => ({ ...current, typographyIntent: value }));
            setSaveState("idle");
          }}
          value={draft.typographyIntent}
        />
        <TextInput
          id="parameter-color-harmony"
          label="配色协调"
          onChange={(value) => {
            setDraft((current) => ({ ...current, colorHarmony: value }));
            setSaveState("idle");
          }}
          value={draft.colorHarmony}
        />
        <TextArea
          id="parameter-overlay-logo-asset-ids"
          label="文字/Logo 素材 ID"
          onChange={(value) => {
            setDraft((current) => ({ ...current, overlayLogoAssetIdsText: value }));
            setSaveState("idle");
          }}
          value={draft.overlayLogoAssetIdsText}
        />
      </section>
      <TextInput
        id="parameter-style"
        label="风格"
        onChange={(value) => {
          setDraft((current) => ({ ...current, style: value }));
          setSaveState("idle");
        }}
        value={draft.style}
      />
      <TextInput
        id="parameter-coverage"
        label="覆盖范围"
        onChange={(value) => {
          setDraft((current) => ({ ...current, coverage: value }));
          setSaveState("idle");
        }}
        value={draft.coverage}
      />
      <TextArea
        id="parameter-palette"
        label="配色"
        onChange={(value) => {
          setDraft((current) => ({ ...current, paletteText: value }));
          setSaveState("idle");
        }}
        value={draft.paletteText}
      />
      <TextArea
        id="parameter-text"
        label="文案"
        onChange={(value) => {
          setDraft((current) => ({ ...current, textText: value }));
          setSaveState("idle");
        }}
        value={draft.textText}
      />
      <TextArea
        id="parameter-reference-asset-ids"
        label="引用素材 ID"
        onChange={(value) => {
          setReferenceAssetIdsTextTouched(true);
          setDraft((current) => ({ ...current, referenceAssetIdsText: value }));
          setSaveState("idle");
        }}
        value={effectiveReferenceAssetIdsText}
      />

      <div className="flex flex-wrap items-center gap-2">
        <Button disabled={!canSave} onClick={handleSave} type="button" variant="outline">
          {saveState === "saving" ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <Save aria-hidden="true" className="h-4 w-4" />
          )}
          保存参数
        </Button>
        <Button disabled={!canGenerate} onClick={handleGenerate} type="button">
          {isGenerating ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles aria-hidden="true" className="h-4 w-4" />
          )}
          生成概念
        </Button>
        <SaveStatus isDirty={isDirty} saveState={saveState} />
      </div>
      {generationError ? (
        <p className="text-xs font-medium text-destructive" role="alert">
          {generationError}
        </p>
      ) : null}

      <Warnings warnings={readStringArray(payload, "warnings")} />
    </div>
  );
}



function SectionWorkspace({
  onSectionSelect,
  sections,
  templateId,
}: {
  onSectionSelect: (section: TemplateSectionSelection) => void;
  sections: TemplateSectionSelection[];
  templateId: string;
}) {
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
  const selectedSection =
    sections.find((section) => section.id === selectedSectionId) ?? sections[0] ?? null;

  const handleSelect = (section: TemplateSectionSelection) => {
    setSelectedSectionId(section.id);
    onSectionSelect(section);
  };

  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">分区工作台</h3>
        <Badge variant={sections.length > 0 ? "primary" : "warning"}>
          {sections.length > 0 ? `${sections.length} 个分区` : "模板未分区"}
        </Badge>
      </div>
      {sections.length > 0 ? (
        <>
          <div aria-label="车身分区" className="grid grid-cols-2 gap-2" role="group">
            {sections.map((section) => (
              <button
                aria-pressed={selectedSection?.id === section.id}
                className={`min-h-10 rounded-md border px-3 py-2 text-left text-sm font-medium ${
                  selectedSection?.id === section.id
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background hover:bg-muted"
                }`}
                key={section.id}
                onClick={() => handleSelect(section)}
                type="button"
              >
                <span className="block truncate">{section.label}</span>
                <span className="block truncate text-xs opacity-80">{section.views.join(" / ")}</span>
              </button>
            ))}
          </div>
          {selectedSection ? <SectionDetail section={selectedSection} /> : null}
        </>
      ) : (
        <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-sm text-secondary-foreground">
          当前模板 {templateId} 未提供 sections，局部编辑会继续使用 PreviewSpec 安全区。
        </p>
      )}
    </section>
  );
}

function SectionDetail({ section }: { section: TemplateSectionSelection }) {
  return (
    <div className="grid grid-cols-2 gap-2 max-[720px]:grid-cols-1">
      <InfoRow label="当前分区" value={`${section.label} (${section.id})`} />
      <InfoRow label="相关视图" value={section.views.join(" / ")} />
      <InfoRow label="平面尺寸" value={section.realSizeLabel} />
      <InfoRow
        label="归一化位置"
        value={`${section.bounds.x}, ${section.bounds.y}, ${section.bounds.width} x ${section.bounds.height}`}
      />
    </div>
  );
}

function ConstructionBriefSummary({ payload }: { payload: Record<string, unknown> }) {
  const materialCount =
    readStringArray(payload, "reference_asset_ids").length +
    readStringArray(payload, "overlay_logo_asset_ids").length;
  const warnings = buildConstructionWarnings(payload);

  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">施工单摘要</h3>
        <Badge variant={warnings.length > 0 ? "warning" : "primary"}>
          {warnings.length > 0 ? `${warnings.length} 项提醒` : "核心齐全"}
        </Badge>
      </div>
      <div className="grid grid-cols-2 gap-2 max-[720px]:grid-cols-1">
        <InfoRow label="车型" value={readString(payload, "vehicle_template_label") || "待补充"} />
        <InfoRow label="范围" value={readString(payload, "coverage") || "待补充"} />
        <InfoRow label="设计" value={formatDesignIntent(payload)} />
        <InfoRow label="素材" value={materialCount > 0 ? `${materialCount} 个素材引用` : "待补充"} />
        <InfoRow label="导出" value={formatExportIntent(payload)} />
        <InfoRow label="风险" value={warnings.length > 0 ? warnings.slice(0, 2).join("；") : "无阻塞提醒"} />
      </div>
    </section>
  );
}

function formatDesignIntent(payload: Record<string, unknown>): string {
  const theme = readString(payload, "character_theme");
  const palette = readStringArray(payload, "palette").join("、");
  const text = readStringArray(payload, "text").join("、");
  const parts = [theme, palette, text].filter(Boolean);
  return parts.length > 0 ? parts.join(" / ") : "待补充";
}

function formatExportIntent(payload: Record<string, unknown>): string {
  const template = readString(payload, "vehicle_template_id");
  const view = readString(payload, "view");
  if (!template) {
    return "待选择模板";
  }
  return `${template}${view ? ` · ${view}` : ""} · SVG/PDF/PNG 准施工包`;
}

function buildConstructionWarnings(payload: Record<string, unknown>): string[] {
  const warnings = [...readStringArray(payload, "warnings")];
  if (readStringArray(payload, "palette").length === 0) {
    warnings.push("主色未填写");
  }
  if (!readString(payload, "coverage")) {
    warnings.push("包覆范围未填写");
  }
  if (
    readStringArray(payload, "text").length === 0 &&
    readStringArray(payload, "overlay_logo_asset_ids").length === 0
  ) {
    warnings.push("文字/Logo 未填写");
  }
  if (readStringArray(payload, "reference_asset_ids").length === 0) {
    warnings.push("参考素材未绑定");
  }
  return [...new Set(warnings)];
}

function ProviderSelector({
  onProviderChange,
  providerStatus,
  selectedProviderId,
}: {
  onProviderChange: (providerId: string) => void;
  providerStatus: WorkbenchProviderStatus;
  selectedProviderId: string;
}) {
  const selectedOption =
    providerStatus.options.find((option) => option.id === selectedProviderId) ??
    providerStatus.options.find((option) => option.id === LOCAL_PROVIDER_ID) ??
    providerStatus.options[0];
  const bflOption = providerStatus.options.find((option) => option.id === BFL_PROVIDER_ID);
  const blockedBflOption = providerStatus.options.find(
    (option) => option.id === BFL_PROVIDER_ID && option.blockedReasons.length > 0,
  );

  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">生成模式</h3>
        {selectedOption ? <Badge variant="muted">{selectedOption.conceptLabel}</Badge> : null}
      </div>
      <div aria-label="生成模式" className="grid grid-cols-2 gap-2" role="group">
        {providerStatus.options.map((option) => (
          <ProviderButton
            key={option.id}
            onSelect={onProviderChange}
            option={option}
            selected={option.id === selectedProviderId}
          />
        ))}
      </div>
      {selectedOption ? (
        <div className="grid grid-cols-2 gap-2">
          <InfoRow label="护栏" value={selectedOption.guardLabel} />
          <InfoRow label="成本" value={selectedOption.maxCostLabel} />
        </div>
      ) : null}
      {bflOption?.enabled && selectedOption?.id !== BFL_PROVIDER_ID ? (
        <div className="grid grid-cols-2 gap-2">
          <InfoRow label="BFL 配额" value={bflOption.guardLabel} />
          <InfoRow label="BFL 成本" value={bflOption.maxCostLabel} />
        </div>
      ) : null}
      {blockedBflOption ? (
        <div className="grid gap-1 rounded-md border border-warning/30 bg-warning/10 p-2 text-xs text-warning">
          <div className="flex items-center gap-1 font-medium">
            <ShieldAlert aria-hidden="true" className="h-4 w-4" />
            托管调用已阻断
          </div>
          {blockedBflOption.blockedReasons.map((reason) => (
            <span key={reason}>{reason}</span>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function TemplateCatalogSelector({
  activeTemplateId,
  isLoading,
  onTemplateSelect,
  templates,
}: {
  activeTemplateId: string;
  isLoading: boolean;
  onTemplateSelect: (templateId: string) => Promise<void>;
  templates: TemplateCatalogItemResponse[];
}) {
  const [filterText, setFilterText] = useState("");
  const normalizedFilter = filterText.trim().toLowerCase();
  const visibleTemplates = templates.filter((template) => {
    if (!normalizedFilter) {
      return true;
    }
    return `${template.id} ${template.label}`.toLowerCase().includes(normalizedFilter);
  });
  const selectedTemplate =
    findTemplate(templates, activeTemplateId) ?? templates.find((template) => template.id);
  const selectedMessages = selectedTemplate
    ? [
        ...(selectedTemplate.readiness.blocking_reasons ?? []),
        ...(selectedTemplate.readiness.warnings ?? []),
      ]
    : [];

  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">模板目录</h3>
        <Badge variant={selectedTemplate?.readiness.catalog_eligible ? "primary" : "warning"}>
          {selectedTemplate?.readiness.catalog_eligible ? "可用" : "受限"}
        </Badge>
      </div>
      <input
        aria-label="模板筛选"
        className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
        onChange={(event) => {
          setFilterText(event.target.value);
        }}
        placeholder="coupe / sedan / suv"
        value={filterText}
      />
      <div className="grid gap-2">
        {visibleTemplates.map((template) => {
          const isSelected = template.id === selectedTemplate?.id;
          const isDisabled = isLoading || !template.readiness.catalog_eligible;
          return (
            <button
              aria-label={`选择模板 ${template.label}`}
              aria-pressed={isSelected}
              className={[
                "grid min-h-20 grid-cols-[96px_1fr] items-center gap-3 rounded-md border p-2 text-left transition-colors",
                isSelected ? "border-primary bg-primary/10" : "border-border bg-background",
                isDisabled ? "cursor-not-allowed opacity-70" : "hover:border-primary",
              ].join(" ")}
              disabled={isDisabled}
              key={template.id}
              onClick={() => {
                void onTemplateSelect(template.id);
              }}
              type="button"
            >
              {/* eslint-disable-next-line @next/next/no-img-element -- Template thumbnails are API catalog assets. */}
              <img
                alt=""
                className="h-12 w-24 rounded-sm border border-border bg-muted object-contain"
                src={templateThumbnailUrl(template.thumbnail_url)}
              />
              <span className="grid min-w-0 gap-1">
                <span className="truncate font-medium">{template.label}</span>
                <span className="flex flex-wrap gap-1">
                  <Badge variant="muted">{template.view}</Badge>
                  <Badge variant="muted">{template.source.source_type}</Badge>
                  <Badge variant={template.source.license_status === "approved" ? "primary" : "warning"}>
                    {template.source.license_status}
                  </Badge>
                </span>
              </span>
            </button>
          );
        })}
      </div>
      {visibleTemplates.length === 0 ? (
        <p className="rounded-md border border-dashed border-border bg-muted px-3 py-2 text-xs text-secondary-foreground">
          没有匹配模板。
        </p>
      ) : null}
      {selectedTemplate ? (
        <div className="grid grid-cols-2 gap-2">
          <InfoRow label="安全区" value={`${selectedTemplate.safe_zone_summary.length}`} />
          <InfoRow label="缩略图" value={selectedTemplate.thumbnail_url} />
        </div>
      ) : null}
      {selectedMessages.length > 0 ? (
        <div className="grid gap-1 rounded-md border border-warning/30 bg-warning/10 p-2 text-xs text-warning">
          {selectedMessages.map((message) => (
            <span key={message}>{message}</span>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function ProviderButton({
  onSelect,
  option,
  selected,
}: {
  onSelect: (providerId: string) => void;
  option: WorkbenchProviderOption;
  selected: boolean;
}) {
  const Icon = option.id === BFL_PROVIDER_ID ? Cloud : Cpu;

  return (
    <Button
      aria-label={option.label}
      aria-pressed={selected}
      className={selected ? "border-primary bg-primary/10" : undefined}
      disabled={!option.enabled}
      onClick={() => {
        onSelect(option.id);
      }}
      type="button"
      variant="outline"
    >
      <Icon aria-hidden="true" className="h-4 w-4" />
      <span className="min-w-0 truncate">{option.label}</span>
      <Badge variant={option.enabled ? "primary" : "muted"}>{option.statusLabel}</Badge>
    </Button>
  );
}

function ReferenceSummary({
  assets,
  referenceAssignments,
  selectedProvider,
}: {
  assets: AssetResponse[];
  referenceAssignments: ReferenceUsageDraft[];
  selectedProvider: WorkbenchProviderOption | undefined;
}) {
  if (referenceAssignments.length === 0) {
    return null;
  }

  const assetsById = new Map(assets.map((asset) => [asset.id, asset]));
  const enabledAssignments = referenceAssignments.filter((assignment) => assignment.enabled);
  const ineligibleAssignments = enabledAssignments.filter((assignment) => {
    const asset = assetsById.get(assignment.assetId);
    return asset ? !getReferenceEligibility(asset).canUseForGeneration : true;
  });
  const unsupportedAssignments = enabledAssignments.filter((assignment) =>
    selectedProvider?.referenceInput.unsupportedRoles.includes(assignment.role),
  );
  const roleCounts = enabledAssignments.reduce<Record<string, number>>((counts, assignment) => {
    counts[assignment.role] = (counts[assignment.role] ?? 0) + 1;
    return counts;
  }, {});

  return (
    <section className="grid gap-2 rounded-md border border-border bg-card p-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">引用素材</h3>
        <Badge variant="muted">{enabledAssignments.length} 个启用</Badge>
      </div>
      <div className="flex flex-wrap gap-2">
        {Object.entries(roleCounts).map(([role, count]) => (
          <Badge key={role} variant="muted">
            {referenceRoleLabel(role as ReferenceRole)} {count}
          </Badge>
        ))}
      </div>
      {selectedProvider ? (
        <InfoRow label="引用支持" value={formatReferenceSupport(selectedProvider)} />
      ) : null}
      {selectedProvider?.referenceInput.supportLabel === "prompt-only" &&
      enabledAssignments.length > 0 ? (
        <p className="text-xs text-secondary-foreground">
          当前供应商只会把引用作为提示上下文记录，不会发送图片引用。
        </p>
      ) : null}
      {unsupportedAssignments.length > 0 ? (
        <ReferenceWarning
          title="引用受限"
          detail={`供应商不支持 ${formatAssignmentRoles(unsupportedAssignments)}`}
        />
      ) : null}
      {ineligibleAssignments.length > 0 ? (
        <ReferenceWarning
          title="引用素材需要权利确认"
          detail={ineligibleAssignments.map((assignment) => assignment.assetId).join(", ")}
        />
      ) : null}
    </section>
  );
}

function ReferenceWarning({ detail, title }: { detail: string; title: string }) {
  return (
    <div className="grid gap-1 rounded-md border border-warning/30 bg-warning/10 p-2 text-xs text-warning">
      <div className="flex items-center gap-1 font-medium">
        <ShieldAlert aria-hidden="true" className="h-4 w-4" />
        {title}
      </div>
      <span>{detail}</span>
    </div>
  );
}

function TextInput({
  id,
  label,
  onChange,
  value,
}: {
  id: string;
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <div>
      <label className="text-xs font-medium text-secondary-foreground" htmlFor={id}>
        {label}
      </label>
      <input
        className="mt-1 h-9 w-full rounded-md border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
        id={id}
        onChange={(event) => {
          onChange(event.target.value);
        }}
        value={value}
      />
    </div>
  );
}

function TextArea({
  id,
  label,
  onChange,
  value,
}: {
  id: string;
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <div>
      <label className="text-xs font-medium text-secondary-foreground" htmlFor={id}>
        {label}
      </label>
      <textarea
        className="mt-1 min-h-20 w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm leading-6 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
        id={id}
        onChange={(event) => {
          onChange(event.target.value);
        }}
        value={value}
      />
    </div>
  );
}

function SaveStatus({
  isDirty,
  saveState,
}: {
  isDirty: boolean;
  saveState: SaveState;
}) {
  if (saveState === "saving") {
    return <Badge variant="muted">保存中</Badge>;
  }

  if (saveState === "saved") {
    return (
      <span
        aria-live="polite"
        className="inline-flex items-center gap-1 text-sm font-medium text-success"
      >
        <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
        参数已保存
      </span>
    );
  }

  if (saveState === "error") {
    return (
      <span
        aria-live="polite"
        className="inline-flex items-center gap-1 text-sm font-medium text-destructive"
      >
        <AlertTriangle aria-hidden="true" className="h-4 w-4" />
        参数保存失败
      </span>
    );
  }

  return <Badge variant={isDirty ? "warning" : "muted"}>{isDirty ? "未保存" : "已同步"}</Badge>;
}

function Warnings({ warnings }: { warnings: string[] }) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-2 rounded-md border border-warning/30 bg-warning/10 p-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-warning">
        <AlertTriangle aria-hidden="true" className="h-4 w-4" />
        质量提示
      </div>
      <ul className="grid gap-1 text-xs text-warning">
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex min-h-9 items-center justify-between gap-3 rounded-md border border-border bg-muted px-3">
      <span className="text-secondary-foreground">{label}</span>
      <span className="min-w-0 truncate font-medium">{value}</span>
    </div>
  );
}

function createDraft(
  brief: WorkbenchBrief | null,
  selectedReferenceAssetIds: string[] = [],
): ParameterDraft {
  const payload = brief ? readPayload(brief) : {};
  const referenceAssetIds =
    selectedReferenceAssetIds.length > 0
      ? selectedReferenceAssetIds
      : readStringArray(payload, "reference_asset_ids");

  return {
    characterFocus: readString(payload, "character_focus"),
    characterTheme: readString(payload, "character_theme"),
    colorHarmony: readString(payload, "color_harmony"),
    coverage: readString(payload, "coverage"),
    overlayLogoAssetIdsText: readStringArray(payload, "overlay_logo_asset_ids").join("\n"),
    paletteText: readStringArray(payload, "palette").join("\n"),
    racingCuesText: readStringArray(payload, "racing_cues").join("\n"),
    referenceAssetIdsText: referenceAssetIds.join("\n"),
    style: readString(payload, "style"),
    supportingGraphicsText: readStringArray(payload, "supporting_graphics").join("\n"),
    textText: readStringArray(payload, "text").join("\n"),
    typographyIntent: readString(payload, "typography_intent"),
  };
}

function buildUpdatePayload(
  payload: Partial<GenerationBriefPayload>,
  draft: ParameterDraft,
  referenceAssignments: ReferenceUsageDraft[] = [],
): GenerationBriefUpdateRequest {
  const updatePayload: GenerationBriefUpdateRequest = {};
  addChangedString(
    updatePayload,
    "character_focus",
    readString(payload, "character_focus"),
    draft.characterFocus,
  );
  addChangedString(
    updatePayload,
    "character_theme",
    readString(payload, "character_theme"),
    draft.characterTheme,
  );
  addChangedString(
    updatePayload,
    "color_harmony",
    readString(payload, "color_harmony"),
    draft.colorHarmony,
  );
  addChangedString(updatePayload, "style", readString(payload, "style"), draft.style);
  addChangedString(updatePayload, "coverage", readString(payload, "coverage"), draft.coverage);
  addChangedString(
    updatePayload,
    "typography_intent",
    readString(payload, "typography_intent"),
    draft.typographyIntent,
  );
  addChangedArray(
    updatePayload,
    "overlay_logo_asset_ids",
    readStringArray(payload, "overlay_logo_asset_ids"),
    draft.overlayLogoAssetIdsText,
  );
  addChangedArray(updatePayload, "palette", readStringArray(payload, "palette"), draft.paletteText);
  addChangedArray(
    updatePayload,
    "racing_cues",
    readStringArray(payload, "racing_cues"),
    draft.racingCuesText,
  );
  addChangedArray(updatePayload, "text", readStringArray(payload, "text"), draft.textText);
  const previousReferenceIds = readStringArray(payload, "reference_asset_ids");
  const draftReferenceIds = splitList(draft.referenceAssetIdsText);
  const referenceIdsChanged =
    draftReferenceIds.join("\n") !== previousReferenceIds.join("\n");
  if (referenceIdsChanged) {
    updatePayload.reference_asset_ids = draftReferenceIds;
  }
  addChangedArray(
    updatePayload,
    "supporting_graphics",
    readStringArray(payload, "supporting_graphics"),
    draft.supportingGraphicsText,
  );
  addReferenceUsageUpdate(updatePayload, payload, referenceAssignments, {
    draftReferenceIds,
    referenceIdsChanged,
  });

  return updatePayload;
}

function addReferenceUsageUpdate(
  updatePayload: GenerationBriefUpdateRequest,
  payload: Partial<GenerationBriefPayload>,
  referenceAssignments: ReferenceUsageDraft[],
  options: { draftReferenceIds: string[]; referenceIdsChanged: boolean },
) {
  const previousReferenceUsage = Array.isArray(payload.reference_usage)
    ? payload.reference_usage
    : [];
  const previousReferenceIds = readStringArray(payload, "reference_asset_ids");
  const hasEnabledReferenceAssignments = referenceAssignments.some(
    (assignment) => assignment.enabled,
  );

  if (options.referenceIdsChanged && options.draftReferenceIds.length === 0) {
    updatePayload.reference_asset_ids = [];
    updatePayload.reference_usage = [];
    return;
  }

  if (referenceAssignments.length === 0 || !hasEnabledReferenceAssignments) {
    if (previousReferenceUsage.length > 0 || previousReferenceIds.length > 0) {
      updatePayload.reference_asset_ids = [];
      updatePayload.reference_usage = [];
    }
    return;
  }

  const referencePayload = buildReferenceUsagePayload(referenceAssignments);

  if (
    referenceUsageSignature(previousReferenceUsage) !==
      referenceUsageSignature(referencePayload.reference_usage ?? []) ||
    previousReferenceIds.join("\n") !== referencePayload.reference_asset_ids?.join("\n")
  ) {
    updatePayload.reference_asset_ids = referencePayload.reference_asset_ids;
    updatePayload.reference_usage = referencePayload.reference_usage;
  }
}

function addChangedString(
  updatePayload: GenerationBriefUpdateRequest,
  key: StringUpdateKey,
  previous: string,
  next: string,
) {
  const normalizedNext = next.trim();
  if (normalizedNext !== previous) {
    updatePayload[key] = normalizedNext;
  }
}

function addChangedArray(
  updatePayload: GenerationBriefUpdateRequest,
  key: ArrayUpdateKey,
  previous: string[],
  next: string,
) {
  const normalizedNext = splitList(next);
  if (normalizedNext.join("\n") !== previous.join("\n")) {
    updatePayload[key] = normalizedNext;
  }
}

function splitList(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function readPayload(brief: WorkbenchBrief): Partial<GenerationBriefPayload> {
  return isRecord(brief.payload) ? (brief.payload as Partial<GenerationBriefPayload>) : {};
}

function findTemplate(
  templates: TemplateCatalogItemResponse[],
  templateId: string,
): TemplateCatalogItemResponse | undefined {
  return templates.find(
    (template) => template.id === templateId || (template.aliases ?? []).includes(templateId),
  );
}


function readTemplateSections(
  templateDetail: TemplateDetailResponse | null,
): TemplateSectionSelection[] {
  if (!templateDetail?.sections) {
    return [];
  }
  return templateDetail.sections
    .map((section) => normalizeTemplateSection(section as TemplateSectionRecord))
    .filter((section): section is TemplateSectionSelection => section !== null);
}

function normalizeTemplateSection(
  section: TemplateSectionRecord,
): TemplateSectionSelection | null {
  const id = typeof section.id === "string" ? section.id : "";
  const bounds = section.bounds;
  const views = Array.isArray(section.views)
    ? section.views.filter((view): view is string => typeof view === "string")
    : [];
  const firstView = views.find(isWorkbenchView);
  if (!id || !bounds || !firstView) {
    return null;
  }
  const normalizedBounds = {
    height: readNumber(bounds.height),
    width: readNumber(bounds.width),
    x: readNumber(bounds.x),
    y: readNumber(bounds.y),
  };
  if (normalizedBounds.width <= 0 || normalizedBounds.height <= 0) {
    return null;
  }
  return {
    bounds: normalizedBounds,
    id,
    label: typeof section.label === "string" ? section.label : id,
    realSizeLabel: formatRealSize(section.real_size_mm),
    view: firstView,
    views,
  };
}

function formatRealSize(value: TemplateSectionRecord["real_size_mm"]): string {
  if (!value) {
    return "未提供";
  }
  const width = readNumber(value.width);
  const height = readNumber(value.height);
  if (width <= 0 || height <= 0) {
    return "未提供";
  }
  return `${width} x ${height} mm`;
}

function isWorkbenchView(value: string): value is TemplateSectionSelection["view"] {
  return value === "front" || value === "rear" || value === "side" || value === "top";
}

function readNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function readString(payload: Record<string, unknown>, key: keyof GenerationBriefPayload): string {
  const value = payload[key];
  return typeof value === "string" ? value : "";
}

function readStringArray(payload: Record<string, unknown>, key: keyof GenerationBriefPayload): string[] {
  const value = payload[key];
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === "string");
}

function formatBriefStatus(status: string | null | undefined): string {
  if (status === "draft") {
    return "草稿";
  }
  if (status === "archived") {
    return "已作废";
  }

  return status || "-";
}

function formatCanvas(payload: Record<string, unknown>): string {
  const width = payload.canvas_width;
  const height = payload.canvas_height;

  if (typeof width === "number" && typeof height === "number") {
    return `${width} x ${height}`;
  }

  return "-";
}

function formatAssignmentRoles(assignments: ReferenceUsageDraft[]): string {
  return Array.from(new Set(assignments.map((assignment) => referenceRoleLabel(assignment.role))))
    .filter(Boolean)
    .join(", ");
}

function formatReferenceSupport(provider: WorkbenchProviderOption): string {
  if (provider.referenceInput.accepted) {
    return "accepted";
  }
  if (provider.referenceInput.promptGuidanceRoles.length > 0) {
    return "prompt-only";
  }

  return "unsupported";
}

function referenceRoleLabel(role: ReferenceRole): string {
  return REFERENCE_ROLE_OPTIONS.find((option) => option.value === role)?.label ?? role;
}

function referenceUsageSignature(assignments: ReferenceAssignment[]): string {
  return assignments
    .map((assignment) => {
      const enabled = assignment.enabled !== false;
      return `${assignment.asset_id}:${assignment.role}:${enabled}`;
    })
    .sort()
    .join("|");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
