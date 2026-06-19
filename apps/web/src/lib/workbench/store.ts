import { create } from "zustand";

export type WorkbenchView = "front" | "rear" | "side" | "top";
export type WorkbenchTab = "assets" | "history" | "parameters";
export type PreviewMode = "2d" | "3d";
export const DEFAULT_WORKBENCH_TEMPLATE_ID = "generic_coupe_side_v1";
export type TargetedEditRoutePreference =
  | "deterministic_recomposition"
  | "provider_masked_generation";
export type TargetedEditTargetType = "safe_zone" | "overlay_layer";

export interface PreviewPan {
  x: number;
  y: number;
}

export interface Preview3DCamera {
  rotationY: number;
  zoom: number;
}

export interface TargetedEditRegion {
  height: number;
  type: "rectangle";
  unit: "normalized";
  width: number;
  x: number;
  y: number;
}

export interface TargetedEditTarget {
  assetId?: string | null;
  id: string;
  label?: string | null;
  layerKind?: string | null;
  region: TargetedEditRegion;
  text?: string | null;
  type: TargetedEditTargetType;
  zoneId?: string | null;
}

interface WorkbenchUiState {
  activeInspectorTab: WorkbenchTab;
  editPromptDelta: string;
  editRoutePreference: TargetedEditRoutePreference;
  isTargetedEditMode: boolean;
  isVersionComparisonMode: boolean;
  preview3DCamera: Preview3DCamera;
  previewMode: PreviewMode;
  previewPan: PreviewPan;
  previewZoom: number;
  selectedComparisonChildId: string | null;
  selectedEditTarget: TargetedEditTarget | null;
  selectedTemplateId: string;
  selectedVersionId: string | null;
  selectedView: WorkbenchView;
  showEditMaskPreview: boolean;
  showOverlayLayers: boolean;
  showSafeZones: boolean;
  clearVersionComparison: () => void;
  clearTargetedEditDraft: () => void;
  panPreview: (pan: PreviewPan) => void;
  resetPreview3DCamera: () => void;
  resetPreviewTransform: () => void;
  resetWorkbenchUi: () => void;
  rotatePreview3D: (deltaDegrees: number) => void;
  setActiveInspectorTab: (tab: WorkbenchTab) => void;
  setSelectedComparisonChildId: (versionId: string | null) => void;
  setSelectedTemplateId: (templateId: string) => void;
  setEditPromptDelta: (value: string) => void;
  setEditRoutePreference: (routePreference: TargetedEditRoutePreference) => void;
  setPreviewMode: (mode: PreviewMode) => void;
  setPreviewZoom: (zoom: number) => void;
  setSelectedEditTarget: (target: TargetedEditTarget | null) => void;
  setSelectedVersionId: (versionId: string | null) => void;
  setSelectedView: (view: WorkbenchView) => void;
  setShowEditMaskPreview: (isVisible: boolean) => void;
  setTargetedEditMode: (isEnabled: boolean) => void;
  toggleEditMaskPreview: () => void;
  toggleOverlayLayers: () => void;
  toggleSafeZones: () => void;
  zoomPreview3DIn: () => void;
  zoomPreview3DOut: () => void;
  zoomPreviewIn: () => void;
  zoomPreviewOut: () => void;
}

const initialWorkbenchUiState = {
  activeInspectorTab: "parameters" as WorkbenchTab,
  editPromptDelta: "",
  editRoutePreference: "deterministic_recomposition" as TargetedEditRoutePreference,
  isTargetedEditMode: false,
  isVersionComparisonMode: false,
  preview3DCamera: { rotationY: 0, zoom: 1 },
  previewMode: "2d" as PreviewMode,
  previewPan: { x: 0, y: 0 },
  previewZoom: 1,
  selectedComparisonChildId: null,
  selectedEditTarget: null,
  selectedTemplateId: DEFAULT_WORKBENCH_TEMPLATE_ID,
  selectedVersionId: null,
  selectedView: "side" as WorkbenchView,
  showEditMaskPreview: false,
  showOverlayLayers: true,
  showSafeZones: false,
};

const previewZoomStep = 0.25;
const minPreviewZoom = 0.5;
const maxPreviewZoom = 3;
const preview3DZoomStep = 0.25;
const minPreview3DZoom = 0.5;
const maxPreview3DZoom = 3;

export const useWorkbenchStore = create<WorkbenchUiState>()((set) => ({
  ...initialWorkbenchUiState,
  clearVersionComparison: () => {
    set(versionComparisonDefaults);
  },
  clearTargetedEditDraft: () => {
    set(targetedEditDraftDefaults);
  },
  panPreview: (previewPan) => {
    set({ previewPan });
  },
  resetPreview3DCamera: () => {
    set({ preview3DCamera: initialWorkbenchUiState.preview3DCamera });
  },
  resetPreviewTransform: () => {
    set({
      previewPan: initialWorkbenchUiState.previewPan,
      previewZoom: initialWorkbenchUiState.previewZoom,
    });
  },
  resetWorkbenchUi: () => {
    set(initialWorkbenchUiState);
  },
  rotatePreview3D: (deltaDegrees) => {
    set((state) => ({
      preview3DCamera: {
        ...state.preview3DCamera,
        rotationY: normalizeRotation(state.preview3DCamera.rotationY + deltaDegrees),
      },
    }));
  },
  setActiveInspectorTab: (activeInspectorTab) => {
    set({ activeInspectorTab });
  },
  setSelectedComparisonChildId: (selectedComparisonChildId) => {
    set((state) => ({
      isVersionComparisonMode: selectedComparisonChildId !== null,
      selectedComparisonChildId,
      selectedVersionId: selectedComparisonChildId ?? state.selectedVersionId,
      ...(state.selectedVersionId !== selectedComparisonChildId && selectedComparisonChildId !== null
        ? targetedEditDraftDefaults
        : {}),
    }));
  },
  setSelectedTemplateId: (selectedTemplateId) => {
    set({ selectedTemplateId });
  },
  setEditPromptDelta: (editPromptDelta) => {
    set({ editPromptDelta });
  },
  setEditRoutePreference: (editRoutePreference) => {
    set({ editRoutePreference });
  },
  setPreviewMode: (previewMode) => {
    set({ previewMode });
  },
  setPreviewZoom: (previewZoom) => {
    set({ previewZoom });
  },
  setSelectedEditTarget: (selectedEditTarget) => {
    set(
      selectedEditTarget === null
        ? { selectedEditTarget, showEditMaskPreview: false }
        : { selectedEditTarget },
    );
  },
  setSelectedVersionId: (selectedVersionId) => {
    set((state) => ({
      selectedVersionId,
      ...(state.selectedVersionId !== selectedVersionId
        ? { ...targetedEditDraftDefaults, ...versionComparisonDefaults }
        : {}),
    }));
  },
  setSelectedView: (selectedView) => {
    set({ selectedView });
  },
  setShowEditMaskPreview: (showEditMaskPreview) => {
    set({ showEditMaskPreview });
  },
  setTargetedEditMode: (isTargetedEditMode) => {
    set({
      isTargetedEditMode,
      ...(!isTargetedEditMode ? targetedEditDraftDefaults : {}),
    });
  },
  toggleEditMaskPreview: () => {
    set((state) => ({ showEditMaskPreview: !state.showEditMaskPreview }));
  },
  toggleOverlayLayers: () => {
    set((state) => ({ showOverlayLayers: !state.showOverlayLayers }));
  },
  toggleSafeZones: () => {
    set((state) => ({ showSafeZones: !state.showSafeZones }));
  },
  zoomPreview3DIn: () => {
    set((state) => ({
      preview3DCamera: {
        ...state.preview3DCamera,
        zoom: clamp3DZoom(state.preview3DCamera.zoom + preview3DZoomStep),
      },
    }));
  },
  zoomPreview3DOut: () => {
    set((state) => ({
      preview3DCamera: {
        ...state.preview3DCamera,
        zoom: clamp3DZoom(state.preview3DCamera.zoom - preview3DZoomStep),
      },
    }));
  },
  zoomPreviewIn: () => {
    set((state) => ({
      previewZoom: clampZoom(state.previewZoom + previewZoomStep),
    }));
  },
  zoomPreviewOut: () => {
    set((state) => ({
      previewZoom: clampZoom(state.previewZoom - previewZoomStep),
    }));
  },
}));

const targetedEditDraftDefaults = {
  editPromptDelta: initialWorkbenchUiState.editPromptDelta,
  editRoutePreference: initialWorkbenchUiState.editRoutePreference,
  selectedEditTarget: initialWorkbenchUiState.selectedEditTarget,
  showEditMaskPreview: initialWorkbenchUiState.showEditMaskPreview,
};

const versionComparisonDefaults = {
  isVersionComparisonMode: initialWorkbenchUiState.isVersionComparisonMode,
  selectedComparisonChildId: initialWorkbenchUiState.selectedComparisonChildId,
};

function clampZoom(value: number): number {
  return Math.min(maxPreviewZoom, Math.max(minPreviewZoom, value));
}

function clamp3DZoom(value: number): number {
  return Math.min(maxPreview3DZoom, Math.max(minPreview3DZoom, value));
}

function normalizeRotation(value: number): number {
  const normalized = ((((value + 180) % 360) + 360) % 360) - 180;
  return Object.is(normalized, -0) ? 0 : normalized;
}
