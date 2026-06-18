import { create } from "zustand";

export type WorkbenchView = "front" | "rear" | "side" | "top";
export type WorkbenchTab = "assets" | "history" | "parameters";
export type TargetedEditRoutePreference =
  | "deterministic_recomposition"
  | "provider_masked_generation";
export type TargetedEditTargetType = "safe_zone" | "overlay_layer";

export interface PreviewPan {
  x: number;
  y: number;
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
  previewPan: PreviewPan;
  previewZoom: number;
  selectedComparisonChildId: string | null;
  selectedEditTarget: TargetedEditTarget | null;
  selectedVersionId: string | null;
  selectedView: WorkbenchView;
  showEditMaskPreview: boolean;
  showOverlayLayers: boolean;
  showSafeZones: boolean;
  clearVersionComparison: () => void;
  clearTargetedEditDraft: () => void;
  panPreview: (pan: PreviewPan) => void;
  resetPreviewTransform: () => void;
  resetWorkbenchUi: () => void;
  setActiveInspectorTab: (tab: WorkbenchTab) => void;
  setSelectedComparisonChildId: (versionId: string | null) => void;
  setEditPromptDelta: (value: string) => void;
  setEditRoutePreference: (routePreference: TargetedEditRoutePreference) => void;
  setPreviewZoom: (zoom: number) => void;
  setSelectedEditTarget: (target: TargetedEditTarget | null) => void;
  setSelectedVersionId: (versionId: string | null) => void;
  setSelectedView: (view: WorkbenchView) => void;
  setShowEditMaskPreview: (isVisible: boolean) => void;
  setTargetedEditMode: (isEnabled: boolean) => void;
  toggleEditMaskPreview: () => void;
  toggleOverlayLayers: () => void;
  toggleSafeZones: () => void;
  zoomPreviewIn: () => void;
  zoomPreviewOut: () => void;
}

const initialWorkbenchUiState = {
  activeInspectorTab: "parameters" as WorkbenchTab,
  editPromptDelta: "",
  editRoutePreference: "deterministic_recomposition" as TargetedEditRoutePreference,
  isTargetedEditMode: false,
  isVersionComparisonMode: false,
  previewPan: { x: 0, y: 0 },
  previewZoom: 1,
  selectedComparisonChildId: null,
  selectedEditTarget: null,
  selectedVersionId: null,
  selectedView: "side" as WorkbenchView,
  showEditMaskPreview: false,
  showOverlayLayers: true,
  showSafeZones: false,
};

const previewZoomStep = 0.25;
const minPreviewZoom = 0.5;
const maxPreviewZoom = 3;

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
  resetPreviewTransform: () => {
    set({
      previewPan: initialWorkbenchUiState.previewPan,
      previewZoom: initialWorkbenchUiState.previewZoom,
    });
  },
  resetWorkbenchUi: () => {
    set(initialWorkbenchUiState);
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
  setEditPromptDelta: (editPromptDelta) => {
    set({ editPromptDelta });
  },
  setEditRoutePreference: (editRoutePreference) => {
    set({ editRoutePreference });
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
