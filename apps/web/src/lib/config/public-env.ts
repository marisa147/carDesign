const readPublicBoolean = (value: string | undefined): boolean =>
  value === "true" || value === "1" || value === "yes" || value === "on";

export const publicEnv = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  v2HostedProviderRolloutEnabled: readPublicBoolean(
    process.env.NEXT_PUBLIC_V2_HOSTED_PROVIDER_ROLLOUT_ENABLED,
  ),
  v2TargetedRegenerationEnabled: readPublicBoolean(
    process.env.NEXT_PUBLIC_V2_TARGETED_REGENERATION_ENABLED,
  ),
  v2ReferenceGuidanceEnabled: readPublicBoolean(
    process.env.NEXT_PUBLIC_V2_REFERENCE_GUIDANCE_ENABLED,
  ),
  v2Lightweight3dPreviewEnabled: readPublicBoolean(
    process.env.NEXT_PUBLIC_V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED,
  ),
  v2EnhancedHandoffPackageEnabled: readPublicBoolean(
    process.env.NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED,
  ),
} as const;

export const isV2EnhancedHandoffPackageEnabled = (): boolean =>
  readPublicBoolean(process.env.NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED);
