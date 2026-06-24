"use client";

import type { ArtifactResponse, DesignVersionResponse } from "@caragent/contracts";
import { useEffect, type CSSProperties } from "react";
import {
  Crosshair,
  Eye,
  EyeOff,
  GitCompareArrows,
  Image as ImageIcon,
  Minus,
  Plus,
  RotateCcw,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { publicEnv } from "@/lib/config/public-env";
import { cn } from "@/lib/utils";
import {
  useWorkbenchStore,
  type TargetedEditRegion,
  type TargetedEditTarget,
  type WorkbenchView,
} from "@/lib/workbench/store";

import { Preview3DPanel } from "./preview-3d-panel";

interface PreviewPanelProps {
  artifacts: ArtifactResponse[];
  isLoading: boolean;
  versions: DesignVersionResponse[];
}

const viewOptions: Array<{ label: string; value: WorkbenchView }> = [
  { label: "侧面", value: "side" },
  { label: "前视", value: "front" },
  { label: "后视", value: "rear" },
  { label: "俯视", value: "top" },
];

export function PreviewPanel({ artifacts, isLoading, versions }: PreviewPanelProps) {
  const {
    clearVersionComparison,
    isTargetedEditMode,
    previewMode,
    resetPreviewTransform,
    selectedComparisonChildId,
    selectedEditTarget,
    selectedVersionId,
    selectedView,
    setSelectedComparisonChildId,
    setSelectedEditTarget,
    setPreviewMode,
    setSelectedVersionId,
    setSelectedView,
    setTargetedEditMode,
    showEditMaskPreview,
    showOverlayLayers,
    showSafeZones,
    toggleEditMaskPreview,
    toggleOverlayLayers,
    toggleSafeZones,
    previewZoom,
    zoomPreviewIn,
    zoomPreviewOut,
  } = useWorkbenchStore();
  const selectedVersion =
    versions.find((version) => version.id === selectedVersionId) ?? versions[0] ?? null;
  const selectedArtifact =
    artifacts.find((artifact) => artifact.version_id === selectedVersion?.id) ??
    artifacts[0] ??
    null;
  const previewSpec = readPreviewSpec(selectedVersion);
  const conceptImageUrl = artifactContentUrl(selectedArtifact);
  const viewAvailability = resolveViewAvailability(previewSpec, selectedView);

  useEffect(() => {
    if (!selectedComparisonChildId) {
      return;
    }

    const comparisonVersion = versions.find(
      (version) => version.id === selectedComparisonChildId,
    );
    if (!comparisonVersion || !hasTargetedEditComparison(comparisonVersion)) {
      clearVersionComparison();
    }
  }, [clearVersionComparison, selectedComparisonChildId, versions]);

  useEffect(() => {
    if (!selectedEditTarget) {
      return;
    }
    if (!previewSpec || !previewSpecContainsTarget(previewSpec, selectedEditTarget)) {
      setSelectedEditTarget(null);
    }
  }, [previewSpec, selectedEditTarget, setSelectedEditTarget]);

  return (
    <div className="grid gap-4">
      <div className="flex min-h-[420px] items-center justify-center rounded-md border border-dashed border-border bg-muted">
        {selectedArtifact && selectedVersion ? (
          <div className="grid w-full gap-3 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <Button
                aria-pressed={previewMode === "2d"}
                onClick={() => {
                  setPreviewMode("2d");
                }}
                size="sm"
                type="button"
                variant={previewMode === "2d" ? "default" : "outline"}
              >
                2D 预览
              </Button>
              <Button
                aria-pressed={previewMode === "3d"}
                onClick={() => {
                  setPreviewMode("3d");
                }}
                size="sm"
                type="button"
                variant={previewMode === "3d" ? "default" : "outline"}
              >
                3D 预览
              </Button>
            </div>

            {previewMode === "3d" ? (
              <Preview3DPanel artifact={selectedArtifact} version={selectedVersion} />
            ) : (
              <>
                <div>
                  <h3 className="text-lg font-semibold">2D 概念预览</h3>
                  <p className="mt-1 text-sm text-secondary-foreground">
                    {selectedVersion.summary ??
                      selectedVersion.title ??
                      "Generated 2D concept preview."}
                  </p>
                </div>
                {conceptImageUrl && !previewSpec ? (
                  <ConceptImage imageUrl={conceptImageUrl} />
                ) : null}
                <div className="rounded-md border border-border bg-background p-4">
                  <p className="text-xs font-medium text-secondary-foreground">对象键</p>
                  <p className="mt-1 break-all text-sm">{selectedArtifact.object_key}</p>
                  <p className="mt-3 text-xs text-secondary-foreground">
                    {selectedArtifact.width ?? "-"} x {selectedArtifact.height ?? "-"} ·{" "}
                    {selectedArtifact.content_type ?? "unknown"}
                  </p>
                </div>
                {previewSpec ? (
                  <>
                    <PreviewSpecSummary previewSpec={previewSpec} />
                    {viewAvailability.isSelectedViewAvailable ? (
                      <>
                        <div className="flex flex-wrap items-center gap-2">
                          <Button
                            aria-pressed={showOverlayLayers}
                            onClick={toggleOverlayLayers}
                            size="sm"
                            type="button"
                            variant={showOverlayLayers ? "default" : "outline"}
                          >
                            <ImageIcon aria-hidden="true" className="h-4 w-4" />
                            文字/Logo 图层
                          </Button>
                          <Button
                            aria-pressed={showSafeZones}
                            onClick={toggleSafeZones}
                            size="sm"
                            type="button"
                            variant={showSafeZones ? "default" : "outline"}
                          >
                            <ImageIcon aria-hidden="true" className="h-4 w-4" />
                            安全区
                          </Button>
                          <Button
                            aria-pressed={isTargetedEditMode}
                            onClick={() => {
                              setTargetedEditMode(!isTargetedEditMode);
                            }}
                            size="sm"
                            type="button"
                            variant={isTargetedEditMode ? "default" : "outline"}
                          >
                            <Crosshair aria-hidden="true" className="h-4 w-4" />
                            局部编辑
                          </Button>
                          <Button
                            aria-pressed={showEditMaskPreview}
                            disabled={!isTargetedEditMode || selectedEditTarget === null}
                            onClick={toggleEditMaskPreview}
                            size="sm"
                            type="button"
                            variant={showEditMaskPreview ? "default" : "outline"}
                          >
                            {showEditMaskPreview ? (
                              <EyeOff aria-hidden="true" className="h-4 w-4" />
                            ) : (
                              <Eye aria-hidden="true" className="h-4 w-4" />
                            )}
                            {showEditMaskPreview ? "隐藏编辑遮罩" : "显示编辑遮罩"}
                          </Button>
                        </div>
                        {isTargetedEditMode && selectedEditTarget ? (
                          <p className="text-xs font-medium text-primary">
                            已选 {selectedEditTarget.type}: {selectedEditTarget.id}
                          </p>
                        ) : null}
                        <PreviewSpecCanvas
                          backgroundImageUrl={conceptImageUrl}
                          isTargetedEditMode={isTargetedEditMode}
                          onSelectEditTarget={setSelectedEditTarget}
                          previewSpec={previewSpec}
                          previewZoom={previewZoom}
                          selectedEditTarget={selectedEditTarget}
                          showEditMaskPreview={showEditMaskPreview}
                          showOverlayLayers={showOverlayLayers}
                          showSafeZones={showSafeZones}
                        />
                        <TemplateLegend previewSpec={previewSpec} showSafeZones={showSafeZones} />
                      </>
                    ) : (
                      <UnavailableViewState
                        selectedView={selectedView}
                        templateLabel={previewSpec.template?.label ?? null}
                      />
                    )}
                  </>
                ) : null}
                <div className="flex flex-wrap items-center gap-2">
                  <Button aria-label="缩小预览" onClick={zoomPreviewOut} size="sm" type="button" variant="outline">
                    <Minus aria-hidden="true" className="h-4 w-4" />
                  </Button>
                  <span className="min-w-14 text-center text-sm font-medium">
                    {Math.round(previewZoom * 100)}%
                  </span>
                  <Button aria-label="放大预览" onClick={zoomPreviewIn} size="sm" type="button" variant="outline">
                    <Plus aria-hidden="true" className="h-4 w-4" />
                  </Button>
                  <Button onClick={resetPreviewTransform} type="button" variant="outline">
                    <RotateCcw aria-hidden="true" className="h-4 w-4" />
                    重置预览
                  </Button>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="px-6 text-center">
            <ImageIcon aria-hidden="true" className="mx-auto h-10 w-10 text-primary" />
            <h3 className="mt-3 text-lg font-semibold">还没有生成图</h3>
            <p className="mt-2 max-w-md text-sm text-secondary-foreground">
              {isLoading
                ? "正在加载生成结果。"
                : "发送设计需求并生成概念后，这里会显示最新 2D 预览。"}
            </p>
          </div>
        )}
      </div>
      <div className="grid gap-2">
        <div className="flex flex-wrap gap-2">
          {viewOptions.map((view) => {
            const isAvailable = viewAvailability.availableViews.includes(view.value);
            return (
              <Button
                aria-pressed={selectedView === view.value}
                className={cn(!isAvailable && "border-dashed text-secondary-foreground")}
                key={view.value}
                onClick={() => {
                  setSelectedView(view.value);
                }}
                size="sm"
                title={isAvailable ? view.label : `${view.label}：模板未提供该视图`}
                type="button"
                variant={selectedView === view.value ? "default" : "outline"}
              >
                {view.label}
              </Button>
            );
          })}
        </div>
        {previewSpec ? (
          <p className="text-xs text-secondary-foreground">
            可用视图：{formatViewList(viewAvailability.availableViews)}
            {viewAvailability.missingViews.length > 0
              ? ` · 未提供：${formatViewList(viewAvailability.missingViews)}`
              : ""}
          </p>
        ) : null}
      </div>
      {versions.length > 0 ? (
        <div className="grid gap-2">
          <p className="text-xs font-medium text-secondary-foreground">版本历史</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {versions.map((version) => {
              const title = version.title ?? version.id;
              const isSelected = selectedVersion?.id === version.id;
              const canCompare = hasTargetedEditComparison(version);
              return (
                <div className="flex shrink-0 items-center gap-1" key={version.id}>
                  <Button
                    aria-pressed={isSelected}
                    onClick={() => {
                      setSelectedVersionId(version.id);
                    }}
                    size="sm"
                    type="button"
                    variant={isSelected ? "default" : "outline"}
                  >
                    {title}
                  </Button>
                  {canCompare ? (
                    <Button
                      aria-label={`对比 ${title}`}
                      aria-pressed={selectedComparisonChildId === version.id}
                      className="px-2"
                      onClick={() => {
                        setSelectedComparisonChildId(version.id);
                      }}
                      size="sm"
                      title={`对比 ${title}`}
                      type="button"
                      variant={
                        selectedComparisonChildId === version.id ? "default" : "outline"
                      }
                    >
                      <GitCompareArrows aria-hidden="true" className="h-4 w-4" />
                    </Button>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}

interface PreviewSpec {
  canvas: { height: number; width: number } | null;
  overlayLayers: OverlayLayer[];
  safeZones: SafeZone[];
  template: { id: string; label: string; supportedViews: WorkbenchView[]; view: WorkbenchView } | null;
  warnings: Array<{ id: string; message: string }>;
}

interface OverlayLayer {
  assetId: string | null;
  id: string;
  kind: string;
  text: string | null;
  zoneId: string | null;
}

interface SafeZone {
  height: number;
  id: string;
  kind: string;
  label: string;
  width: number;
  x: number;
  y: number;
}

function UnavailableViewState({
  selectedView,
  templateLabel,
}: {
  selectedView: WorkbenchView;
  templateLabel: string | null;
}) {
  return (
    <div className="grid min-h-80 place-items-center rounded-md border border-dashed border-border bg-background p-6 text-center">
      <div>
        <ImageIcon aria-hidden="true" className="mx-auto h-9 w-9 text-secondary-foreground" />
        <h4 className="mt-3 text-base font-semibold">模板未提供该视图</h4>
        <p className="mt-2 text-sm text-secondary-foreground">
          {templateLabel ?? "当前模板"} · {viewLabel(selectedView)}
        </p>
      </div>
    </div>
  );
}

function ConceptImage({ imageUrl }: { imageUrl: string }) {
  return (
    <div className="overflow-hidden rounded-md border border-border bg-background">
      {/* eslint-disable-next-line @next/next/no-img-element -- Generated artifacts are served by the API content route. */}
      <img
        alt="2D concept preview"
        className="aspect-[2/1] w-full bg-muted object-contain"
        src={imageUrl}
      />
    </div>
  );
}

function PreviewSpecSummary({ previewSpec }: { previewSpec: PreviewSpec }) {
  return (
    <div className="grid gap-2 rounded-md border border-border bg-background p-3">
      <p className="text-xs font-medium text-secondary-foreground">PreviewSpec 摘要</p>
      <div className="grid gap-1 text-xs">
        <div className="font-medium">
          {previewSpec.template?.label ?? "Unknown template"}
        </div>
        <div className="break-all text-secondary-foreground">
          {previewSpec.template?.id ?? "unknown-template"} ·{" "}
          {previewSpec.template?.view ?? "unknown-view"}
        </div>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded-md border border-border bg-muted px-2 py-1">
          图层 {previewSpec.overlayLayers.length}
        </span>
        <span className="rounded-md border border-border bg-muted px-2 py-1">
          安全区 {previewSpec.safeZones.length}
        </span>
        <span className="rounded-md border border-border bg-muted px-2 py-1">
          警告 {previewSpec.warnings.length}
        </span>
      </div>
      {previewSpec.warnings.length > 0 ? (
        <div className="grid gap-1 text-xs text-secondary-foreground">
          {previewSpec.warnings.map((warning) => (
            <p key={warning.id}>{warning.message}</p>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function PreviewSpecCanvas({
  backgroundImageUrl,
  isTargetedEditMode,
  onSelectEditTarget,
  previewSpec,
  previewZoom,
  selectedEditTarget,
  showEditMaskPreview,
  showOverlayLayers,
  showSafeZones,
}: {
  backgroundImageUrl: string | null;
  isTargetedEditMode: boolean;
  onSelectEditTarget: (target: TargetedEditTarget) => void;
  previewSpec: PreviewSpec;
  previewZoom: number;
  selectedEditTarget: TargetedEditTarget | null;
  showEditMaskPreview: boolean;
  showOverlayLayers: boolean;
  showSafeZones: boolean;
}) {
  const safeZonesById = new Map(previewSpec.safeZones.map((zone) => [zone.id, zone]));
  return (
    <div className="overflow-hidden rounded-md border border-border bg-background p-3">
      <div
        className="relative aspect-[2/1] min-h-36 overflow-hidden rounded-md border border-border bg-muted"
        style={{ transform: `scale(${previewZoom})`, transformOrigin: "center" }}
      >
        {backgroundImageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element -- Generated artifacts are served by the API content route.
          <img
            alt="2D concept preview"
            className="absolute inset-0 h-full w-full object-contain"
            src={backgroundImageUrl}
          />
        ) : (
          <>
            <div className="absolute left-[9%] top-[36%] h-[36%] w-[82%] rounded-[48px] border-2 border-foreground bg-card" />
            <div className="absolute left-[22%] top-[28%] h-[16%] w-[42%] border-2 border-foreground bg-background" />
            <div className="absolute left-[20%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
            <div className="absolute left-[72%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
          </>
        )}
        {showSafeZones
          ? previewSpec.safeZones.map((zone) => {
              const isSelected = isSelectedEditTarget(selectedEditTarget, "safe_zone", zone.id);
              const className = cn(
                "absolute overflow-hidden rounded border px-1 py-0.5 text-left text-[10px] font-medium",
                isSelected
                  ? "border-destructive bg-destructive/20 text-destructive"
                  : "border-primary/70 bg-primary/10 text-primary",
                isTargetedEditMode
                  ? "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  : "",
              );

              return isTargetedEditMode ? (
                <button
                  aria-label={`选择安全区 ${zone.id}`}
                  className={className}
                  key={zone.id}
                  onClick={() => {
                    onSelectEditTarget(safeZoneToTarget(zone));
                  }}
                  style={zoneStyle(zone)}
                  type="button"
                >
                  {zone.id}
                </button>
              ) : (
                <div className={className} key={zone.id} style={zoneStyle(zone)}>
                  {zone.id}
                </div>
              );
            })
          : null}
        {showOverlayLayers
          ? previewSpec.overlayLayers.map((layer) => {
              const zone = layer.zoneId ? safeZonesById.get(layer.zoneId) : undefined;
              const isSelected = isSelectedEditTarget(selectedEditTarget, "overlay_layer", layer.id);
              const label = layer.kind === "logo" ? layer.assetId ?? "LOGO" : layer.text ?? layer.id;
              const className = cn(
                "absolute overflow-hidden rounded border px-2 py-1 text-left text-[10px] font-semibold",
                isSelected
                  ? "border-destructive bg-destructive text-destructive-foreground"
                  : "border-foreground bg-foreground text-background",
                isTargetedEditMode
                  ? "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  : "",
              );

              return isTargetedEditMode ? (
                <button
                  aria-label={`选择图层 ${layer.id}`}
                  className={className}
                  key={layer.id}
                  onClick={() => {
                    if (isTargetedEditMode) {
                      onSelectEditTarget(overlayLayerToTarget(layer, zone));
                    }
                  }}
                  style={zoneStyle(zone)}
                  type="button"
                >
                  {label}
                </button>
              ) : (
                <div className={className} key={layer.id} style={zoneStyle(zone)}>
                  {label}
                </div>
              );
            })
          : null}
        {showEditMaskPreview && selectedEditTarget ? (
          <div
            className="pointer-events-none absolute rounded border-2 border-destructive bg-destructive/20 px-1 py-0.5 text-[10px] font-semibold text-destructive"
            style={regionStyle(selectedEditTarget.region)}
          >
            编辑遮罩预览
          </div>
        ) : null}
      </div>
    </div>
  );
}

function TemplateLegend({
  previewSpec,
  showSafeZones,
}: {
  previewSpec: PreviewSpec;
  showSafeZones: boolean;
}) {
  return (
    <div className="grid gap-2 rounded-md border border-border bg-background p-3 text-xs">
      <div className="font-medium">模板参考区</div>
      <div className="text-secondary-foreground">
        {previewSpec.template?.label ?? "Generic side-view coupe"} ·{" "}
        {previewSpec.template?.id ?? "unknown-template"} ·{" "}
        {previewSpec.template?.view ?? "side"}
      </div>
      {showSafeZones ? (
        <div className="flex flex-wrap gap-2">
          {previewSpec.safeZones.map((zone) => (
            <span className="rounded-md border border-border bg-muted px-2 py-1" key={zone.id}>
              {zone.id}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function artifactContentUrl(artifact: ArtifactResponse | null): string | null {
  const contentUrl = artifact?.content_url;
  if (!contentUrl) {
    return null;
  }
  if (contentUrl.startsWith("http://") || contentUrl.startsWith("https://")) {
    return contentUrl;
  }
  return `${publicEnv.apiBaseUrl}${contentUrl}`;
}

function readPreviewSpec(version: DesignVersionResponse | null): PreviewSpec | null {
  const previewSpec = version?.parameters.preview_spec;
  if (!isRecord(previewSpec)) {
    return null;
  }

  return {
    canvas: readCanvas(previewSpec.canvas),
    overlayLayers: readOverlayLayers(previewSpec.overlay_layers),
    safeZones: readSafeZones(previewSpec.safe_zones),
    template: readTemplate(previewSpec.template),
    warnings: readWarnings(previewSpec.warnings),
  };
}

function hasTargetedEditComparison(version: DesignVersionResponse): boolean {
  if (!version.parent_version_id) {
    return false;
  }

  const parameters = version.parameters;
  if (!isRecord(parameters)) {
    return false;
  }

  const editIntent = isRecord(parameters.edit_intent) ? parameters.edit_intent : null;
  return Boolean(
    readString(parameters.edit_route) ||
      isRecord(parameters.target) ||
      isRecord(parameters.region) ||
      isRecord(parameters.prompt_delta) ||
      (editIntent &&
        (isRecord(editIntent.target) ||
          isRecord(editIntent.region) ||
          isRecord(editIntent.prompt_delta))),
  );
}

function readCanvas(value: unknown): PreviewSpec["canvas"] {
  if (!isRecord(value)) {
    return null;
  }
  return {
    height: readNumber(value.height),
    width: readNumber(value.width),
  };
}

function readTemplate(value: unknown): PreviewSpec["template"] {
  if (!isRecord(value)) {
    return null;
  }

  const view = readWorkbenchView(value.view) ?? "side";
  const supportedViews = readSupportedViews(value.supported_views, view);
  return {
    id: readString(value.id),
    label: readString(value.label),
    supportedViews,
    view,
  };
}

function readOverlayLayers(value: unknown): OverlayLayer[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(isRecord).map((layer, index) => ({
    assetId: readNullableString(layer.asset_id),
    id: readString(layer.id) || `overlay-${index + 1}`,
    kind: readString(layer.kind),
    text: readNullableString(layer.text),
    zoneId: readNullableString(layer.zone_id),
  }));
}

function readSafeZones(value: unknown): SafeZone[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(isRecord).map((zone, index) => ({
    height: readNumber(zone.height),
    id: readString(zone.id) || `safe-zone-${index + 1}`,
    kind: readString(zone.kind),
    label: readString(zone.label),
    width: readNumber(zone.width),
    x: readNumber(zone.x),
    y: readNumber(zone.y),
  }));
}

function readWarnings(value: unknown): PreviewSpec["warnings"] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(isRecord).map((warning, index) => ({
    id: readString(warning.id) || `warning-${index + 1}`,
    message: readString(warning.message),
  }));
}

function resolveViewAvailability(
  previewSpec: PreviewSpec | null,
  selectedView: WorkbenchView,
): {
  availableViews: WorkbenchView[];
  isSelectedViewAvailable: boolean;
  missingViews: WorkbenchView[];
} {
  const availableViews = previewSpec?.template?.supportedViews.length
    ? previewSpec.template.supportedViews
    : viewOptions.map((view) => view.value);
  return {
    availableViews,
    isSelectedViewAvailable: availableViews.includes(selectedView),
    missingViews: viewOptions
      .map((view) => view.value)
      .filter((view) => !availableViews.includes(view)),
  };
}

function formatViewList(views: WorkbenchView[]): string {
  return views.map(viewLabel).join("、") || "无";
}

function viewLabel(view: WorkbenchView): string {
  return viewOptions.find((option) => option.value === view)?.label ?? view;
}

function readSupportedViews(value: unknown, fallbackView: WorkbenchView): WorkbenchView[] {
  if (!Array.isArray(value)) {
    return [fallbackView];
  }
  const views = value
    .map(readWorkbenchView)
    .filter((view): view is WorkbenchView => view !== null);
  return views.length > 0 ? Array.from(new Set(views)) : [fallbackView];
}

function readWorkbenchView(value: unknown): WorkbenchView | null {
  return typeof value === "string" && viewOptions.some((view) => view.value === value)
    ? (value as WorkbenchView)
    : null;
}

function zoneStyle(zone: SafeZone | undefined): CSSProperties {
  const safeZone = zone ?? fallbackSafeZone;
  return {
    height: `${safeZone.height * 100}%`,
    left: `${safeZone.x * 100}%`,
    top: `${safeZone.y * 100}%`,
    width: `${safeZone.width * 100}%`,
  };
}

const fallbackSafeZone: SafeZone = {
  height: 0.16,
  id: "fallback",
  kind: "body",
  label: "",
  width: 0.24,
  x: 0.38,
  y: 0.5,
};

function safeZoneToTarget(zone: SafeZone): TargetedEditTarget {
  return {
    id: zone.id,
    label: zone.label,
    region: editRegionFromZone(zone),
    type: "safe_zone",
  };
}

function overlayLayerToTarget(
  layer: OverlayLayer,
  zone: SafeZone | undefined,
): TargetedEditTarget {
  return {
    assetId: layer.assetId,
    id: layer.id,
    label: layer.text ?? layer.assetId ?? layer.id,
    layerKind: layer.kind,
    region: editRegionFromZone(zone),
    text: layer.text,
    type: "overlay_layer",
    zoneId: layer.zoneId,
  };
}

function editRegionFromZone(zone: SafeZone | undefined): TargetedEditRegion {
  const safeZone = zone ?? fallbackSafeZone;
  return {
    height: safeZone.height,
    type: "rectangle",
    unit: "normalized",
    width: safeZone.width,
    x: safeZone.x,
    y: safeZone.y,
  };
}

function regionStyle(region: TargetedEditRegion): CSSProperties {
  return {
    height: `${region.height * 100}%`,
    left: `${region.x * 100}%`,
    top: `${region.y * 100}%`,
    width: `${region.width * 100}%`,
  };
}

function isSelectedEditTarget(
  target: TargetedEditTarget | null,
  type: TargetedEditTarget["type"],
  id: string,
): boolean {
  return target?.type === type && target.id === id;
}

function previewSpecContainsTarget(
  previewSpec: PreviewSpec,
  target: TargetedEditTarget,
): boolean {
  if (target.type === "safe_zone") {
    return previewSpec.safeZones.some((zone) => zone.id === target.id);
  }

  const layer = previewSpec.overlayLayers.find((candidate) => candidate.id === target.id);
  if (!layer) {
    return false;
  }
  return !layer.zoneId || previewSpec.safeZones.some((zone) => zone.id === layer.zoneId);
}

function readNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function readNullableString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function readString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

