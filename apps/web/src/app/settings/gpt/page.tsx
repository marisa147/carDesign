"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, ExternalLink, RotateCw, Save, ShieldCheck } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  getOpenAISettings,
  updateOpenAISettings,
  type OpenAISettings,
  type OpenAISettingsUpdate,
} from "@/lib/api/operations";

const DEFAULT_FORM: OpenAISettingsUpdate = {
  apiKey: "",
  baseUrl: "https://api.openai.com/v1",
  callsEnabled: true,
  dailyCallLimit: 6,
  defaultProvider: "openai",
  imageModel: "gpt-image-2",
  imagePath: "/images/generations",
  maxEstimatedCostPerJob: "0.9000",
  parserEnabled: true,
  rateLimitPerMinute: 2,
  responsesPath: "/responses",
  rolloutEnabled: true,
  textModel: "gpt-5.5",
};

export default function GptSettingsPage() {
  const [settings, setSettings] = useState<OpenAISettings | null>(null);
  const [form, setForm] = useState<OpenAISettingsUpdate>(DEFAULT_FORM);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    getOpenAISettings()
      .then((nextSettings) => {
        if (isCancelled) {
          return;
        }
        setSettings(nextSettings);
        setForm(formFromSettings(nextSettings));
        setError(null);
      })
      .catch((caught: unknown) => {
        if (!isCancelled) {
          setError(caught instanceof Error ? caught.message : "GPT 设置读取失败");
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

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    setNotice(null);
    try {
      const saved = await updateOpenAISettings({
        ...form,
        apiKey: form.apiKey?.trim() ? form.apiKey.trim() : undefined,
      });
      setSettings(saved);
      setForm({ ...formFromSettings(saved), apiKey: "" });
      setNotice("设置已保存，重启 API 和 Worker 后生效。");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "GPT 设置保存失败");
    } finally {
      setIsSaving(false);
    }
  }

  const imageUrl = `${form.baseUrl.replace(/\/$/, "")}${normalizePath(form.imagePath)}`;

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="flex min-h-14 items-center justify-between gap-4 border-b border-border bg-card px-5 max-[720px]:flex-wrap max-[720px]:px-4 max-[720px]:py-3">
        <div className="min-w-0">
          <h1 className="truncate text-xl font-semibold leading-[1.2]">GPT 设置</h1>
          <p className="truncate text-xs text-secondary-foreground">OpenAI text and image provider</p>
        </div>
        <Link
          className="inline-flex min-h-9 items-center justify-center gap-2 rounded-md border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
          href="/"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          返回工作台
        </Link>
      </header>

      <section className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-5">
        <div className="rounded-md border border-border bg-card p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="text-lg font-semibold leading-[1.25]">连接状态</h2>
              <p className="mt-1 text-sm text-secondary-foreground">
                {settings?.imageUrl ?? imageUrl}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={settings?.apiKeyConfigured ? "primary" : "muted"}>
                {settings?.apiKeyConfigured ? "Key 已配置" : "Key 未配置"}
              </Badge>
              <Badge variant={settings?.callsEnabled ? "primary" : "muted"}>
                {settings?.callsEnabled ? "调用开启" : "调用关闭"}
              </Badge>
              <Badge variant={settings?.parserEnabled ? "primary" : "muted"}>
                {settings?.parserEnabled ? "解析开启" : "解析关闭"}
              </Badge>
            </div>
          </div>
        </div>

        {notice ? (
          <Alert className="border-primary/40">
            <AlertTitle>已保存</AlertTitle>
            <AlertDescription>{notice}</AlertDescription>
          </Alert>
        ) : null}
        {error ? (
          <Alert className="border-destructive/40 text-destructive">
            <AlertTitle>设置失败</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        <form className="rounded-md border border-border bg-card p-4" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4 max-[760px]:grid-cols-1">
            <TextField
              label="OpenAI API Key"
              onChange={(value) => setForm((current) => ({ ...current, apiKey: value }))}
              placeholder={settings?.apiKeyMasked ?? "粘贴新的 OpenAI key"}
              type="password"
              value={form.apiKey ?? ""}
            />
            <TextField
              label="图片模型"
              onChange={(value) => setForm((current) => ({ ...current, imageModel: value }))}
              value={form.imageModel}
            />
            <TextField
              label="文字模型"
              onChange={(value) => setForm((current) => ({ ...current, textModel: value }))}
              value={form.textModel}
            />
            <TextField
              label="Base URL"
              onChange={(value) => setForm((current) => ({ ...current, baseUrl: value }))}
              value={form.baseUrl}
            />
            <TextField
              label="Image Path"
              onChange={(value) => setForm((current) => ({ ...current, imagePath: value }))}
              value={form.imagePath}
            />
            <TextField
              label="Responses Path"
              onChange={(value) => setForm((current) => ({ ...current, responsesPath: value }))}
              value={form.responsesPath}
            />
            <TextField
              label="单任务成本上限"
              onChange={(value) =>
                setForm((current) => ({ ...current, maxEstimatedCostPerJob: value || null }))
              }
              value={form.maxEstimatedCostPerJob ?? ""}
            />
            <NumberField
              label="每日调用上限"
              onChange={(value) => setForm((current) => ({ ...current, dailyCallLimit: value }))}
              value={form.dailyCallLimit}
            />
            <NumberField
              label="每分钟调用上限"
              onChange={(value) =>
                setForm((current) => ({ ...current, rateLimitPerMinute: value }))
              }
              value={form.rateLimitPerMinute}
            />
          </div>

          <div className="mt-4 grid grid-cols-4 gap-3 max-[900px]:grid-cols-2 max-[560px]:grid-cols-1">
            <ToggleRow
              checked={form.defaultProvider === "openai"}
              label="GPT 默认托管"
              onChange={(checked) =>
                setForm((current) => ({
                  ...current,
                  callsEnabled: checked ? true : current.callsEnabled,
                  defaultProvider: checked ? "openai" : "disabled",
                  rolloutEnabled: checked ? true : current.rolloutEnabled,
                }))
              }
            />
            <ToggleRow
              checked={form.rolloutEnabled}
              label="托管灰度开关"
              onChange={(checked) =>
                setForm((current) => ({
                  ...current,
                  defaultProvider:
                    checked && current.defaultProvider === "openai" ? "openai" : "disabled",
                  rolloutEnabled: checked,
                }))
              }
            />
            <ToggleRow
              checked={form.callsEnabled}
              label="允许托管调用"
              onChange={(checked) => setForm((current) => ({ ...current, callsEnabled: checked }))}
            />
            <ToggleRow
              checked={form.parserEnabled}
              label="GPT 解析 brief"
              onChange={(checked) => setForm((current) => ({ ...current, parserEnabled: checked }))}
            />
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
            <div className="flex min-w-0 items-center gap-2 text-sm text-secondary-foreground">
              <ShieldCheck aria-hidden="true" className="h-4 w-4 shrink-0" />
              <span className="truncate">{imageUrl}</span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button disabled={isLoading || isSaving} type="button" variant="outline" onClick={() => window.location.reload()}>
                <RotateCw aria-hidden="true" className="h-4 w-4" />
                重新读取
              </Button>
              <Button disabled={isLoading || isSaving} type="submit">
                <Save aria-hidden="true" className="h-4 w-4" />
                保存 GPT 设置
              </Button>
            </div>
          </div>
        </form>

        <a
          className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-primary hover:underline"
          href="https://developers.openai.com/api/docs/guides/image-generation"
          rel="noreferrer"
          target="_blank"
        >
          <ExternalLink aria-hidden="true" className="h-4 w-4" />
          OpenAI 图像文档
        </a>
      </section>
    </main>
  );
}

function TextField({
  label,
  onChange,
  placeholder,
  type = "text",
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "password" | "text";
  value: string;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1 text-sm font-medium">
      <span>{label}</span>
      <input
        className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
        value={value}
      />
    </label>
  );
}

function NumberField({
  label,
  onChange,
  value,
}: {
  label: string;
  onChange: (value: number | null) => void;
  value: number | null;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1 text-sm font-medium">
      <span>{label}</span>
      <input
        className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
        min="1"
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
        type="number"
        value={value ?? ""}
      />
    </label>
  );
}

function ToggleRow({
  checked,
  label,
  onChange,
}: {
  checked: boolean;
  label: string;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex min-h-11 items-center justify-between gap-3 rounded-md border border-border bg-background px-3 py-2 text-sm font-medium">
      <span>{label}</span>
      <input
        checked={checked}
        className="h-5 w-5 accent-primary"
        onChange={(event) => onChange(event.target.checked)}
        type="checkbox"
      />
    </label>
  );
}

function formFromSettings(settings: OpenAISettings): OpenAISettingsUpdate {
  return {
    apiKey: "",
    baseUrl: settings.baseUrl,
    callsEnabled: settings.callsEnabled,
    dailyCallLimit: settings.dailyCallLimit,
    defaultProvider: settings.defaultProvider === "openai" ? "openai" : "disabled",
    imageModel: settings.imageModel,
    imagePath: settings.imagePath,
    maxEstimatedCostPerJob: settings.maxEstimatedCostPerJob,
    parserEnabled: settings.parserEnabled,
    rateLimitPerMinute: settings.rateLimitPerMinute,
    responsesPath: settings.responsesPath,
    rolloutEnabled: settings.rolloutEnabled,
    textModel: settings.textModel,
  };
}

function normalizePath(path: string): string {
  return path.startsWith("/") ? path : `/${path}`;
}
