"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, FileArchive, RefreshCw, ShieldCheck, Upload } from "lucide-react";
import type { TemplateCatalogItemResponse, TemplateDetailResponse } from "@caragent/contracts";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  getTemplate,
  listTemplates,
  templateThumbnailUrl,
  validateTemplatePackage,
  type TemplatePackageValidationResponse,
} from "@/lib/api/templates";

type AuthorizationMap = Record<string, unknown>;

export default function TemplateSettingsPage() {
  const [templates, setTemplates] = useState<TemplateCatalogItemResponse[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<TemplateDetailResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validation, setValidation] = useState<TemplatePackageValidationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    listTemplates({ catalog_eligible: true })
      .then((items) => {
        if (isCancelled) {
          return;
        }
        setTemplates(items);
        setSelectedId(items[0]?.id ?? null);
        setError(null);
      })
      .catch((caught: unknown) => {
        if (!isCancelled) {
          setError(caught instanceof Error ? caught.message : "模板列表读取失败");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoading(false);
        }
      });
    return () => {
      isCancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setSelectedDetail(null);
      return;
    }
    let isCancelled = false;
    setIsDetailLoading(true);
    getTemplate(selectedId)
      .then((detail) => {
        if (!isCancelled) {
          setSelectedDetail(detail);
        }
      })
      .catch((caught: unknown) => {
        if (!isCancelled) {
          setError(caught instanceof Error ? caught.message : "模板详情读取失败");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsDetailLoading(false);
        }
      });
    return () => {
      isCancelled = true;
    };
  }, [selectedId]);

  const summary = useMemo(() => {
    const maintained = templates.filter((item) => sourceClass(item) === "maintained_internal").length;
    const commercial = templates.filter((item) => item.source.distribution_allowed).length;
    return { commercial, maintained, total: templates.length };
  }, [templates]);

  async function handleValidate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }
    setIsValidating(true);
    setError(null);
    try {
      setValidation(await validateTemplatePackage(selectedFile));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "模板包校验失败");
    } finally {
      setIsValidating(false);
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="flex min-h-14 items-center justify-between gap-4 border-b border-border bg-card px-5 max-[720px]:flex-wrap max-[720px]:px-4 max-[720px]:py-3">
        <div className="min-w-0">
          <h1 className="truncate text-xl font-semibold leading-[1.2]">模板管理</h1>
          <p className="truncate text-xs text-secondary-foreground">Template packages and authorization</p>
        </div>
        <Link
          className="inline-flex min-h-9 items-center justify-center gap-2 rounded-md border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
          href="/"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          返回工作台
        </Link>
      </header>

      <section className="mx-auto grid w-full max-w-7xl grid-cols-[minmax(300px,420px)_1fr] gap-4 px-4 py-5 max-[980px]:grid-cols-1">
        <div className="flex min-w-0 flex-col gap-4">
          <div className="grid grid-cols-3 gap-2 rounded-md border border-border bg-card p-3">
            <Metric label="已安装" value={summary.total} />
            <Metric label="维护模板" value={summary.maintained} />
            <Metric label="可分发" value={summary.commercial} />
          </div>

          {error ? (
            <Alert className="border-destructive/40 text-destructive">
              <AlertTitle>模板操作失败</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          <div className="rounded-md border border-border bg-card p-3">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold leading-[1.25]">安装模板</h2>
              <Button type="button" variant="outline" onClick={() => window.location.reload()}>
                <RefreshCw aria-hidden="true" className="h-4 w-4" />
                刷新
              </Button>
            </div>
            <div className="flex max-h-[620px] flex-col gap-2 overflow-auto pr-1">
              {isLoading ? <p className="text-sm text-secondary-foreground">正在读取模板...</p> : null}
              {templates.map((item) => (
                <button
                  className={`flex w-full items-start gap-3 rounded-md border p-3 text-left transition hover:bg-muted ${
                    item.id === selectedId ? "border-primary bg-primary/5" : "border-border bg-background"
                  }`}
                  key={item.id}
                  onClick={() => setSelectedId(item.id)}
                  type="button"
                >
                  <img
                    alt=""
                    className="h-16 w-24 shrink-0 rounded border border-border bg-muted object-contain"
                    src={templateThumbnailUrl(item.thumbnail_url)}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-semibold">{item.label}</span>
                    <span className="mt-1 block truncate text-xs text-secondary-foreground">{item.id}</span>
                    <span className="mt-2 flex flex-wrap gap-1">
                      <Badge variant="primary">{sourceClassLabel(sourceClass(item))}</Badge>
                      {item.supported_views.map((view) => (
                        <Badge key={view} variant="muted">{view}</Badge>
                      ))}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex min-w-0 flex-col gap-4">
          <TemplateDetailPanel detail={selectedDetail} isLoading={isDetailLoading} />
          <form className="rounded-md border border-border bg-card p-4" onSubmit={handleValidate}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold leading-[1.25]">导入校验</h2>
                <p className="mt-1 text-sm text-secondary-foreground">上传包含 PNG/SVG/JSON 的模板 zip 包。</p>
              </div>
              <Badge variant={validation?.accepted ? "primary" : validation ? "warning" : "muted"}>
                {validation ? (validation.accepted ? "校验通过" : "校验失败") : "未校验"}
              </Badge>
            </div>
            <label className="mt-4 flex min-h-28 cursor-pointer flex-col items-center justify-center gap-2 rounded-md border border-dashed border-border bg-background px-4 py-5 text-center text-sm hover:bg-muted">
              <FileArchive aria-hidden="true" className="h-6 w-6 text-secondary-foreground" />
              <span className="font-medium">{selectedFile?.name ?? "选择模板 zip 包"}</span>
              <span className="text-xs text-secondary-foreground">template.json、safe_zones.json、sections.json、forbidden_zones.json、PNG/SVG 资产</span>
              <input
                accept=".zip,application/zip"
                className="sr-only"
                onChange={(event) => {
                  setSelectedFile(event.target.files?.[0] ?? null);
                  setValidation(null);
                }}
                type="file"
              />
            </label>
            <div className="mt-4 flex justify-end">
              <Button disabled={!selectedFile || isValidating} type="submit">
                <Upload aria-hidden="true" className="h-4 w-4" />
                校验模板包
              </Button>
            </div>
            {validation ? <ValidationReport report={validation} /> : null}
          </form>
        </div>
      </section>
    </main>
  );
}

function TemplateDetailPanel({ detail, isLoading }: { detail: TemplateDetailResponse | null; isLoading: boolean }) {
  const authorization = (detail?.authorization ?? null) as AuthorizationMap | null;
  return (
    <section className="rounded-md border border-border bg-card p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold leading-[1.25]">{detail?.label ?? "模板详情"}</h2>
          <p className="mt-1 truncate text-sm text-secondary-foreground">{detail?.id ?? (isLoading ? "正在读取..." : "未选择模板")}</p>
        </div>
        {detail ? <Badge variant="primary">{sourceClassLabel(sourceClass(detail))}</Badge> : null}
      </div>

      {detail ? (
        <>
          <div className="mt-4 grid grid-cols-4 gap-2 max-[760px]:grid-cols-2">
            <Metric label="视图" value={detail.supported_views.length} />
            <Metric label="分区" value={detail.sections?.length ?? 0} />
            <Metric label="禁区" value={detail.forbidden_zones?.length ?? 0} />
            <Metric label="安全区" value={detail.safe_zones.length} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 max-[760px]:grid-cols-1">
            <InfoRow label="尺寸" value={formatDimensions(detail.dimensions)} />
            <InfoRow label="比例" value={formatScale(detail.scale)} />
            <InfoRow label="导出" value={formatList(detail.export_config?.formats)} />
            <InfoRow label="授权范围" value={formatValue(authorization?.scope)} />
          </div>
          <div className="mt-4 rounded-md border border-border bg-background p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <ShieldCheck aria-hidden="true" className="h-4 w-4" />
              授权状态
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm max-[760px]:grid-cols-1">
              <InfoRow label="来源" value={formatValue(authorization?.source)} />
              <InfoRow label="授权文件" value={formatValue(authorization?.authorization_file)} />
              <InfoRow label="过期时间" value={formatValue(authorization?.expires_at)} />
              <InfoRow label="商业使用" value={formatBoolean(authorization?.commercial_use)} />
              <InfoRow label="审核人" value={formatValue(authorization?.reviewer)} />
              <InfoRow label="版本历史" value={formatVersionHistory(authorization?.version_history)} />
            </div>
          </div>
        </>
      ) : null}
    </section>
  );
}

function ValidationReport({ report }: { report: TemplatePackageValidationResponse }) {
  return (
    <div className="mt-4 rounded-md border border-border bg-background p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold">{report.label ?? report.template_id ?? "模板包"}</p>
          <p className="text-xs text-secondary-foreground">检查 {report.files_checked.length} 个文件</p>
        </div>
        <Badge variant={report.accepted ? "primary" : "warning"}>{report.accepted ? "accepted" : "blocked"}</Badge>
      </div>
      {report.issues.length > 0 ? (
        <div className="mt-3 flex flex-col gap-2">
          {report.issues.map((issue, index) => (
            <div className="rounded-md border border-border bg-card p-2 text-sm" key={`${issue.code}-${index}`}>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={issue.severity === "error" ? "warning" : "muted"}>{issue.code}</Badge>
                <span className="font-medium">{issue.path ?? "package"}</span>
              </div>
              <p className="mt-1 text-secondary-foreground">{issue.message}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-secondary-foreground">未发现阻塞问题。</p>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-xs text-secondary-foreground">{label}</p>
      <p className="mt-1 text-xl font-semibold leading-none">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-border bg-card px-3 py-2">
      <p className="text-xs text-secondary-foreground">{label}</p>
      <p className="mt-1 break-words text-sm font-medium">{value}</p>
    </div>
  );
}

function sourceClass(template: TemplateCatalogItemResponse | TemplateDetailResponse): string {
  const auth = "authorization" in template ? (template.authorization as AuthorizationMap | null) : null;
  if (template.source.source_type === "internal_original" || auth?.source === "internal_generated") {
    return "maintained_internal";
  }
  if (template.source.source_type === "user_provided_with_rights") {
    return "user_provided";
  }
  if (template.source.source_type === "licensed_template") {
    return "third_party_authorized";
  }
  if (template.source.source_type === "third_party_reference_only") {
    return "reference_only";
  }
  return "unknown";
}

function sourceClassLabel(value: string): string {
  switch (value) {
    case "maintained_internal":
      return "维护内置";
    case "user_provided":
      return "用户提供";
    case "third_party_authorized":
      return "第三方授权";
    case "reference_only":
      return "仅参考";
    default:
      return "未知来源";
  }
}

function formatDimensions(dimensions: Record<string, unknown> | null | undefined): string {
  if (!dimensions) {
    return "未提供";
  }
  const length = formatValue(dimensions.overall_length);
  const width = formatValue(dimensions.overall_width);
  return `${length} x ${width} mm`;
}

function formatScale(scale: Record<string, unknown> | null | undefined): string {
  if (!scale) {
    return "未提供";
  }
  return `${formatValue(scale.unit)} / ${formatValue(scale.side)}`;
}

function formatList(value: unknown): string {
  return Array.isArray(value) && value.length > 0 ? value.join(", ") : "未提供";
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "未提供";
  }
  return String(value);
}

function formatBoolean(value: unknown): string {
  if (typeof value !== "boolean") {
    return "未提供";
  }
  return value ? "允许" : "不允许";
}

function formatVersionHistory(value: unknown): string {
  if (!Array.isArray(value) || value.length === 0) {
    return "未提供";
  }
  return `${value.length} 条记录`;
}
