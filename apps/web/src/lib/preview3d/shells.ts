export const GENERIC_SIDE_COUPE_TEMPLATE_ID = "generic-side-coupe";
export const GENERIC_SIDE_COUPE_VIEW = "side";
export const GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID =
  "generic-side-coupe-lightweight-v1";
export const DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID = "front-left-default";
export const SIDE_DECAL_MATERIAL_SLOT = "side-decal-plane";

export interface LightweightPreview3DShell {
  dimensions: {
    height: number;
    length: number;
    width: number;
  };
  id: string;
  label: string;
  materialSlots: string[];
  templateId: string;
}

export const GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL: LightweightPreview3DShell = {
  dimensions: { height: 1.4, length: 4.4, width: 1.8 },
  id: GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID,
  label: "Generic side coupe lightweight shell",
  materialSlots: ["body", SIDE_DECAL_MATERIAL_SLOT, "glass", "wheel"],
  templateId: GENERIC_SIDE_COUPE_TEMPLATE_ID,
};

const shellRegistry = new Map<string, LightweightPreview3DShell>([
  [
    shellRegistryKey({
      templateId: GENERIC_SIDE_COUPE_TEMPLATE_ID,
      view: GENERIC_SIDE_COUPE_VIEW,
    }),
    GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL,
  ],
]);

export function listPreview3DShells(): LightweightPreview3DShell[] {
  return Array.from(shellRegistry.values()).map(copyShell);
}

export function resolvePreview3DShell({
  templateId,
  view,
}: {
  templateId: string;
  view: string;
}): LightweightPreview3DShell | null {
  const shell = shellRegistry.get(shellRegistryKey({ templateId, view }));
  return shell ? copyShell(shell) : null;
}

function shellRegistryKey({
  templateId,
  view,
}: {
  templateId: string;
  view: string;
}): string {
  return `${templateId}:${view.toLowerCase()}`;
}

function copyShell(shell: LightweightPreview3DShell): LightweightPreview3DShell {
  return {
    ...shell,
    dimensions: { ...shell.dimensions },
    materialSlots: [...shell.materialSlots],
  };
}
