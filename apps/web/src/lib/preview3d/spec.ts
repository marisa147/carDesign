import type {
  ArtifactResponse,
  DesignVersionResponse,
  Preview3DSpec,
} from "@caragent/contracts";

import {
  buildPreview3DMaterialPlan,
  materialPlanFromProjectionRecords,
  type Preview3DMaterialPlan,
} from "./materials";
import {
  DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID,
  GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID,
  SIDE_DECAL_MATERIAL_SLOT,
  type LightweightPreview3DShell,
  resolvePreview3DShell,
} from "./shells";

export {
  DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID,
  GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID,
  SIDE_DECAL_MATERIAL_SLOT,
} from "./shells";

export const PREVIEW_3D_SCHEMA_VERSION = 1;
export const PREVIEW_3D_FALLBACK_MESSAGE = "当前模板暂无 3D 壳体，继续使用 2D 预览。";

export interface Preview3DProjectionRecord extends Record<string, unknown> {
  id: string;
  slot: string;
}

export interface Preview3DCompatibilitySource {
  artifactId: string;
  artifactObjectKey: string;
  previewSpecTemplateId: string;
  previewSpecView: string;
  versionId: string;
  workspaceId: string;
}

export interface Preview3DCompatibilityResult {
  cameraPresetId: string;
  fallbackMessage: string | null;
  materialPlan: Preview3DMaterialPlan;
  overlayLayers: Preview3DProjectionRecord[];
  preview3dSpec: Preview3DSpec;
  reason: string | null;
  safeZoneOverlays: Preview3DProjectionRecord[];
  shell: LightweightPreview3DShell | null;
  source: Preview3DCompatibilitySource;
  status: "compatible" | "incompatible";
}

export function buildPreview3DCompatibility({
  artifact,
  version,
}: {
  artifact: ArtifactResponse | null;
  version: DesignVersionResponse;
}): Preview3DCompatibilityResult {
  const existingSpec = readExistingPreview3DSpec(version);
  if (existingSpec) {
    return compatibilityFromPreview3DSpec(existingSpec);
  }

  const previewSpec = readPreviewSpec(version);
  const { templateId, view } = readPreviewSpecIdentity(previewSpec);
  const shell = resolvePreview3DShell({ templateId, view });
  const reason =
    shell === null ? preview3DFallbackReason({ templateId, view }) : null;
  const source: Preview3DCompatibilitySource = {
    artifactId: artifact?.id ?? "unknown-artifact",
    artifactObjectKey: artifact?.object_key ?? "unknown-object-key",
    previewSpecTemplateId: templateId,
    previewSpecView: view,
    versionId: version.id,
    workspaceId: version.workspace_id,
  };
  const overlayLayers = projectionRecords(previewSpec?.overlay_layers);
  const safeZoneOverlays = projectionRecords(previewSpec?.safe_zones);
  const materialPlan = buildPreview3DMaterialPlan({ artifact, previewSpec });
  const preview3dSpec = buildPreview3DSpec({
    overlayLayers,
    reason,
    safeZoneOverlays,
    shell,
    source,
  });

  return {
    cameraPresetId: preview3dSpec.camera.preset_id,
    fallbackMessage: shell === null ? PREVIEW_3D_FALLBACK_MESSAGE : null,
    materialPlan,
    overlayLayers,
    preview3dSpec,
    reason,
    safeZoneOverlays,
    shell,
    source,
    status: shell === null ? "incompatible" : "compatible",
  };
}

function compatibilityFromPreview3DSpec(
  preview3dSpec: Preview3DSpec,
): Preview3DCompatibilityResult {
  const shell = preview3dSpec.shell ? shellFromContract(preview3dSpec.shell) : null;
  const status = preview3dSpec.compatibility.status;
  const reason = preview3dSpec.compatibility.reason ?? null;
  const overlayLayers = projectionRecords(preview3dSpec.materials.overlay_layers);
  const safeZoneOverlays = projectionRecords(preview3dSpec.materials.safe_zone_overlays);
  const materialPlan = materialPlanFromProjectionRecords({
    artifact: null,
    overlayLayers,
    safeZoneOverlays,
    source: {
      artifactContentType: null,
      artifactHeight: null,
      artifactId: preview3dSpec.source.artifact_id,
      artifactObjectKey: preview3dSpec.source.artifact_object_key,
      artifactWidth: null,
    },
    warningIds: preview3dSpec.warnings?.map((warning) => warning.id) ?? [],
  });
  return {
    cameraPresetId: preview3dSpec.camera.preset_id,
    fallbackMessage: status === "compatible" ? null : PREVIEW_3D_FALLBACK_MESSAGE,
    materialPlan,
    overlayLayers,
    preview3dSpec,
    reason,
    safeZoneOverlays,
    shell,
    source: {
      artifactId: preview3dSpec.source.artifact_id,
      artifactObjectKey: preview3dSpec.source.artifact_object_key,
      previewSpecTemplateId: preview3dSpec.source.preview_spec_template_id,
      previewSpecView: preview3dSpec.source.preview_spec_view,
      versionId: preview3dSpec.source.version_id,
      workspaceId: preview3dSpec.source.workspace_id,
    },
    status,
  };
}

function buildPreview3DSpec({
  overlayLayers,
  reason,
  safeZoneOverlays,
  shell,
  source,
}: {
  overlayLayers: Preview3DProjectionRecord[];
  reason: string | null;
  safeZoneOverlays: Preview3DProjectionRecord[];
  shell: LightweightPreview3DShell | null;
  source: Preview3DCompatibilitySource;
}): Preview3DSpec {
  return {
    camera: {
      position: { x: 2.8, y: 1.4, z: 4.2 },
      preset_id: DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID,
      target: { x: 0, y: 0.4, z: 0 },
      zoom: 1,
    },
    compatibility:
      shell === null
        ? { reason: reason ?? "No lightweight 3D shell is registered.", status: "incompatible" }
        : { shell_id: shell.id, status: "compatible" },
    materials: {
      decal_strategy: "preview_spec_projection",
      overlay_layers: overlayLayers,
      safe_zone_overlays: safeZoneOverlays,
      source_artifact_id: source.artifactId,
      source_kind: "preview_spec",
    },
    mode: "lightweight_shell",
    schema_version: PREVIEW_3D_SCHEMA_VERSION,
    shell:
      shell === null
        ? null
        : {
            dimensions: { ...shell.dimensions },
            id: shell.id,
            label: shell.label,
            material_slots: [...shell.materialSlots],
            template_id: shell.templateId,
          },
    source: {
      artifact_id: source.artifactId,
      artifact_object_key: source.artifactObjectKey,
      preview_spec_template_id: source.previewSpecTemplateId,
      preview_spec_view: source.previewSpecView,
      version_id: source.versionId,
      workspace_id: source.workspaceId,
    },
    warnings: [
      {
        id: "non_production_preview",
        message: "Lightweight 3D preview is concept-only and not production wrap proof.",
        severity: "warning",
      },
      {
        id: "uv_not_verified",
        message: "Vehicle-specific UV mapping has not been verified.",
        severity: "warning",
      },
      {
        id: "single_shell_fixture",
        message: "Preview uses one lightweight shell fixture for MVP validation.",
        severity: "info",
      },
    ],
  };
}

function readExistingPreview3DSpec(version: DesignVersionResponse): Preview3DSpec | null {
  if (version.preview_3d) {
    return version.preview_3d;
  }
  const preview3d = version.parameters.preview_3d;
  return isRecord(preview3d) ? (preview3d as unknown as Preview3DSpec) : null;
}

function readPreviewSpec(version: DesignVersionResponse): Record<string, unknown> | null {
  const previewSpec = version.parameters.preview_spec;
  return isRecord(previewSpec) ? previewSpec : null;
}

function readPreviewSpecIdentity(previewSpec: Record<string, unknown> | null): {
  templateId: string;
  view: string;
} {
  const template = isRecord(previewSpec?.template) ? previewSpec.template : null;
  return {
    templateId: readString(template?.id, "unknown-template"),
    view: readString(template?.view, "unknown-view").toLowerCase(),
  };
}

function projectionRecords(value: unknown): Preview3DProjectionRecord[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(isRecord).map((record, index) => {
    const id = readString(record.id, `projection-${index + 1}`);
    return {
      ...record,
      id,
      slot: readString(record.slot, SIDE_DECAL_MATERIAL_SLOT),
    };
  });
}

function shellFromContract(shell: Preview3DSpec["shell"]): LightweightPreview3DShell | null {
  if (!shell) {
    return null;
  }
  return {
    dimensions: {
      height: shell.dimensions.height ?? 0,
      length: shell.dimensions.length ?? 0,
      width: shell.dimensions.width ?? 0,
    },
    id: shell.id,
    label: shell.label,
    materialSlots: [...shell.material_slots],
    templateId: shell.template_id,
  };
}

function preview3DFallbackReason({
  templateId,
  view,
}: {
  templateId: string;
  view: string;
}): string {
  return (
    "No lightweight 3D shell is registered for template " +
    `'${templateId}' with view '${view}'. Continue with the 2D PreviewSpec fallback.`
  );
}

function readString(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
