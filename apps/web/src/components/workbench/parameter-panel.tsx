"use client";

import type {
  GenerationBriefPayload,
  GenerationBriefResponse,
  GenerationBriefUpdateRequest,
} from "@caragent/contracts";
import {
  AlertTriangle,
  CheckCircle2,
  Cloud,
  Cpu,
  Loader2,
  Save,
  ShieldAlert,
  SlidersHorizontal,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { WorkbenchBrief } from "@/components/workbench/chat-panel";
import {
  BFL_PROVIDER_ID,
  LOCAL_PROVIDER_ID,
  type WorkbenchProviderOption,
  type WorkbenchProviderStatus,
} from "@/lib/api/operations";

interface ParameterPanelProps {
  currentBrief: WorkbenchBrief | null;
  isLoading: boolean;
  onSave: (payload: GenerationBriefUpdateRequest) => Promise<GenerationBriefResponse>;
  onProviderChange: (providerId: string) => void;
  providerStatus: WorkbenchProviderStatus;
  selectedReferenceAssetIds: string[];
  selectedProviderId: string;
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
  currentBrief,
  isLoading,
  onSave,
  onProviderChange,
  providerStatus,
  selectedReferenceAssetIds,
  selectedProviderId,
}: ParameterPanelProps) {
  const [draft, setDraft] = useState(() =>
    createDraft(currentBrief, selectedReferenceAssetIds),
  );
  const [saveState, setSaveState] = useState<SaveState>("idle");

  if (!currentBrief) {
    return (
      <div className="grid gap-3 text-sm">
        <InfoRow label="车型模板" value="Generic side-view coupe" />
        <InfoRow label="视角" value="side" />
        <InfoRow label="风格" value="等待 brief" />
        <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
          先发送设计需求以生成结构化 brief。
        </p>
        <Button disabled type="button" variant="outline">
          <SlidersHorizontal aria-hidden="true" className="h-4 w-4" />
          保存参数
        </Button>
      </div>
    );
  }

  const payload = readPayload(currentBrief);
  const updatePayload = buildUpdatePayload(payload, draft);
  const isDirty = Object.keys(updatePayload).length > 0;
  const canSave = isDirty && saveState !== "saving" && !isLoading;

  const handleSave = async () => {
    if (!canSave) {
      return;
    }

    setSaveState("saving");
    try {
      const updatedBrief = await onSave(updatePayload);
      setDraft(createDraft(updatedBrief));
      setSaveState("saved");
    } catch {
      setSaveState("error");
    }
  };

  return (
    <div className="grid gap-3 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <InfoRow label="车型模板" value={readString(payload, "vehicle_template_label") || "-"} />
        <InfoRow label="视角" value={readString(payload, "view") || "-"} />
      </div>
      <InfoRow label="画布" value={formatCanvas(payload)} />
      <ProviderSelector
        onProviderChange={onProviderChange}
        providerStatus={providerStatus}
        selectedProviderId={selectedProviderId}
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
          setDraft((current) => ({ ...current, referenceAssetIdsText: value }));
          setSaveState("idle");
        }}
        value={draft.referenceAssetIdsText}
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
        <SaveStatus isDirty={isDirty} saveState={saveState} />
      </div>

      <Warnings warnings={readStringArray(payload, "warnings")} />
    </div>
  );
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
  addChangedArray(
    updatePayload,
    "reference_asset_ids",
    readStringArray(payload, "reference_asset_ids"),
    draft.referenceAssetIdsText,
  );
  addChangedArray(
    updatePayload,
    "supporting_graphics",
    readStringArray(payload, "supporting_graphics"),
    draft.supportingGraphicsText,
  );

  return updatePayload;
}

function addChangedString(
  updatePayload: GenerationBriefUpdateRequest,
  key: StringUpdateKey,
  previous: string,
  next: string,
) {
  const normalizedNext = next.trim();
  if (normalizedNext.length > 0 && normalizedNext !== previous) {
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
  if (normalizedNext.length > 0 && normalizedNext.join("\n") !== previous.join("\n")) {
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

function formatCanvas(payload: Record<string, unknown>): string {
  const width = payload.canvas_width;
  const height = payload.canvas_height;

  if (typeof width === "number" && typeof height === "number") {
    return `${width} x ${height}`;
  }

  return "-";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
