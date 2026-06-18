"use client";

import type { ArtifactResponse, DesignVersionResponse } from "@caragent/contracts";
import type { CSSProperties } from "react";
import { Image as ImageIcon, Minus, Plus, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useWorkbenchStore, type WorkbenchView } from "@/lib/workbench/store";

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
    resetPreviewTransform,
    selectedVersionId,
    selectedView,
    setSelectedVersionId,
    setSelectedView,
    showOverlayLayers,
    showSafeZones,
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

  return (
    <div className="grid gap-4">
      <div className="flex min-h-[420px] items-center justify-center rounded-md border border-dashed border-border bg-muted">
        {selectedArtifact && selectedVersion ? (
          <div className="grid w-full gap-3 p-5">
            <div>
              <h3 className="text-lg font-semibold">2D 概念预览</h3>
              <p className="mt-1 text-sm text-secondary-foreground">
                {selectedVersion.summary ?? selectedVersion.title ?? "Generated 2D concept preview."}
              </p>
            </div>
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
                </div>
                <PreviewSpecCanvas
                  previewSpec={previewSpec}
                  previewZoom={previewZoom}
                  showOverlayLayers={showOverlayLayers}
                  showSafeZones={showSafeZones}
                />
                <TemplateLegend previewSpec={previewSpec} showSafeZones={showSafeZones} />
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
      <div className="flex flex-wrap gap-2">
        {viewOptions.map((view) => (
          <Button
            aria-pressed={selectedView === view.value}
            key={view.value}
            onClick={() => {
              setSelectedView(view.value);
            }}
            size="sm"
            type="button"
            variant={selectedView === view.value ? "default" : "outline"}
          >
            {view.label}
          </Button>
        ))}
      </div>
      {versions.length > 0 ? (
        <div className="grid gap-2">
          <p className="text-xs font-medium text-secondary-foreground">版本历史</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {versions.map((version) => (
              <Button
                aria-pressed={selectedVersion?.id === version.id}
                key={version.id}
                onClick={() => {
                  setSelectedVersionId(version.id);
                }}
                size="sm"
                type="button"
                variant={selectedVersion?.id === version.id ? "default" : "outline"}
              >
                {version.title ?? version.id}
              </Button>
            ))}
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
  template: { id: string; label: string; view: string } | null;
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

function PreviewSpecSummary({ previewSpec }: { previewSpec: PreviewSpec }) {
  return (
    <div className="grid gap-2 rounded-md border border-border bg-background p-3">
      <p className="text-xs font-medium text-secondary-foreground">PreviewSpec 摘要</p>
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
    </div>
  );
}

function PreviewSpecCanvas({
  previewSpec,
  previewZoom,
  showOverlayLayers,
  showSafeZones,
}: {
  previewSpec: PreviewSpec;
  previewZoom: number;
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
        <div className="absolute left-[9%] top-[36%] h-[36%] w-[82%] rounded-[48px] border-2 border-foreground bg-card" />
        <div className="absolute left-[22%] top-[28%] h-[16%] w-[42%] border-2 border-foreground bg-background" />
        <div className="absolute left-[20%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
        <div className="absolute left-[72%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
        {showSafeZones
          ? previewSpec.safeZones.map((zone) => (
              <div
                className="absolute overflow-hidden rounded border border-primary/70 bg-primary/10 px-1 py-0.5 text-[10px] font-medium text-primary"
                key={zone.id}
                style={zoneStyle(zone)}
              >
                {zone.id}
              </div>
            ))
          : null}
        {showOverlayLayers
          ? previewSpec.overlayLayers.map((layer) => {
              const zone = layer.zoneId ? safeZonesById.get(layer.zoneId) : undefined;
              return (
                <div
                  className="absolute overflow-hidden rounded border border-foreground bg-foreground px-2 py-1 text-[10px] font-semibold text-background"
                  key={layer.id}
                  style={zoneStyle(zone)}
                >
                  {layer.kind === "logo" ? layer.assetId ?? "LOGO" : layer.text ?? layer.id}
                </div>
              );
            })
          : null}
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
  return {
    id: readString(value.id),
    label: readString(value.label),
    view: readString(value.view),
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

function zoneStyle(zone: SafeZone | undefined): CSSProperties {
  const safeZone = zone ?? {
    height: 0.16,
    id: "fallback",
    kind: "body",
    label: "",
    width: 0.24,
    x: 0.38,
    y: 0.5,
  };
  return {
    height: `${safeZone.height * 100}%`,
    left: `${safeZone.x * 100}%`,
    top: `${safeZone.y * 100}%`,
    width: `${safeZone.width * 100}%`,
  };
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
