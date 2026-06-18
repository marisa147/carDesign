import type { ArtifactResponse } from "@caragent/contracts";

import { SIDE_DECAL_MATERIAL_SLOT } from "./shells";

export const PREVIEW_3D_UV_WARNING_TEXT = "UV 贴图未经过车型级验证。";
export const PREVIEW_3D_CONCEPT_WARNING_TEXT = "3D 材质映射仅用于概念位置参考。";

export interface Preview3DMaterialBounds {
  height: number;
  width: number;
  x: number;
  y: number;
}

export interface Preview3DMaterialSource {
  artifactContentType: string | null;
  artifactHeight: number | null;
  artifactId: string;
  artifactObjectKey: string;
  artifactWidth: number | null;
}

export interface Preview3DMaterialSafeZone {
  bounds: Preview3DMaterialBounds;
  id: string;
  kind: string;
  label: string;
  slot: string;
}

export interface Preview3DMaterialOverlay {
  assetId: string | null;
  bounds: Preview3DMaterialBounds;
  id: string;
  kind: string;
  label: string;
  slot: string;
  zoneId: string | null;
}

export interface Preview3DMaterialPlan {
  overlays: Preview3DMaterialOverlay[];
  safeZones: Preview3DMaterialSafeZone[];
  source: Preview3DMaterialSource;
  warningIds: string[];
  warnings: string[];
}

const fallbackOverlayBounds: Preview3DMaterialBounds = {
  height: 0.14,
  width: 0.28,
  x: 0.36,
  y: 0.44,
};

export function buildPreview3DMaterialPlan({
  artifact,
  previewSpec,
}: {
  artifact: ArtifactResponse | null;
  previewSpec: Record<string, unknown> | null | undefined;
}): Preview3DMaterialPlan {
  const safeZones = readSafeZones(previewSpec?.safe_zones);
  const safeZonesById = new Map(safeZones.map((zone) => [zone.id, zone]));
  return {
    overlays: readOverlays(previewSpec?.overlay_layers, safeZonesById),
    safeZones,
    source: sourceFromArtifact(artifact),
    warningIds: ["non_production_preview", "uv_not_verified"],
    warnings: [PREVIEW_3D_CONCEPT_WARNING_TEXT, PREVIEW_3D_UV_WARNING_TEXT],
  };
}

export function materialPlanFromProjectionRecords({
  artifact,
  overlayLayers,
  safeZoneOverlays,
  source,
  warningIds = ["non_production_preview", "uv_not_verified"],
}: {
  artifact: ArtifactResponse | null;
  overlayLayers: Array<Record<string, unknown>>;
  safeZoneOverlays: Array<Record<string, unknown>>;
  source?: Preview3DMaterialSource;
  warningIds?: string[];
}): Preview3DMaterialPlan {
  const safeZones = safeZoneOverlays
    .map((record, index) => materialSafeZoneFromRecord(record, index))
    .filter((zone): zone is Preview3DMaterialSafeZone => zone !== null);
  const safeZonesById = new Map(safeZones.map((zone) => [zone.id, zone]));
  return {
    overlays: readOverlays(overlayLayers, safeZonesById),
    safeZones,
    source: source ?? sourceFromArtifact(artifact),
    warningIds,
    warnings: warningTextsForIds(warningIds),
  };
}

function sourceFromArtifact(artifact: ArtifactResponse | null): Preview3DMaterialSource {
  return {
    artifactContentType: artifact?.content_type ?? null,
    artifactHeight: artifact?.height ?? null,
    artifactId: artifact?.id ?? "unknown-artifact",
    artifactObjectKey: artifact?.object_key ?? "unknown-object-key",
    artifactWidth: artifact?.width ?? null,
  };
}

function readSafeZones(value: unknown): Preview3DMaterialSafeZone[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .filter(isRecord)
    .map((record, index) => materialSafeZoneFromRecord(record, index))
    .filter((zone): zone is Preview3DMaterialSafeZone => zone !== null);
}

function materialSafeZoneFromRecord(
  record: Record<string, unknown>,
  index: number,
): Preview3DMaterialSafeZone | null {
  const bounds = readBounds(record);
  if (!bounds) {
    return null;
  }
  return {
    bounds,
    id: readString(record.id, `safe-zone-${index + 1}`),
    kind: readString(record.kind, "body"),
    label: readString(record.label, readString(record.id, `Safe zone ${index + 1}`)),
    slot: readString(record.slot, SIDE_DECAL_MATERIAL_SLOT),
  };
}

function readOverlays(
  value: unknown,
  safeZonesById: Map<string, Preview3DMaterialSafeZone>,
): Preview3DMaterialOverlay[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(isRecord).map((record, index) => {
    const zoneId = readNullableString(record.zone_id);
    const zoneBounds = zoneId ? safeZonesById.get(zoneId)?.bounds : undefined;
    const kind = readString(record.kind, "overlay");
    const assetId = readNullableString(record.asset_id);
    const id = readString(record.id, `overlay-${index + 1}`);
    return {
      assetId,
      bounds: zoneBounds ?? fallbackOverlayBounds,
      id,
      kind,
      label: readOverlayLabel({ assetId, id, kind, record }),
      slot: readString(record.slot, SIDE_DECAL_MATERIAL_SLOT),
      zoneId,
    };
  });
}

function readOverlayLabel({
  assetId,
  id,
  kind,
  record,
}: {
  assetId: string | null;
  id: string;
  kind: string;
  record: Record<string, unknown>;
}): string {
  if (kind === "text") {
    return readString(record.text, id);
  }
  return assetId ?? readString(record.text, id);
}

function readBounds(record: Record<string, unknown>): Preview3DMaterialBounds | null {
  const x = readNumber(record.x);
  const y = readNumber(record.y);
  const width = readNumber(record.width);
  const height = readNumber(record.height);
  if (width === null || height === null || width <= 0 || height <= 0) {
    return null;
  }
  const boundedX = clamp01(x ?? 0);
  const boundedY = clamp01(y ?? 0);
  return {
    height: clampDimension(height, boundedY),
    width: clampDimension(width, boundedX),
    x: boundedX,
    y: boundedY,
  };
}

function warningTextsForIds(warningIds: string[]): string[] {
  const warnings = [PREVIEW_3D_CONCEPT_WARNING_TEXT];
  if (warningIds.includes("uv_not_verified")) {
    warnings.push(PREVIEW_3D_UV_WARNING_TEXT);
  }
  return warnings;
}

function clampDimension(value: number, start: number): number {
  return Math.min(1 - start, Math.max(0, value));
}

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function readNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function readNullableString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

function readString(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
