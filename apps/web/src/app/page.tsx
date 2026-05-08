"use client";

import {
  Activity,
  AlertCircle,
  Braces,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  Loader2,
  Monitor,
  Server,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";

import {
  checkStackHealth,
  type FoundationStatusCard,
  type FoundationStatusId,
  type StackHealthResult,
} from "@/lib/api/health";
import { publicEnv } from "@/lib/config/public-env";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

const defaultCards: FoundationStatusCard[] = [
  {
    detail: "Next.js workbench shell is loaded.",
    id: "web",
    label: "Web",
    state: "connected",
    statusLabel: "已连接",
  },
  {
    detail: "API 未连接",
    id: "api",
    label: "API",
    state: "unavailable",
    statusLabel: "未连接",
  },
  {
    detail: "Worker 将在后续任务接入队列状态",
    id: "worker",
    label: "Worker",
    state: "not-configured",
    statusLabel: "未配置",
  },
  {
    detail: "API 合约已生成",
    id: "contracts",
    label: "Contracts",
    state: "current",
    statusLabel: "已生成",
  },
  {
    detail: "PostgreSQL、Redis 和 MinIO 等待本地服务启动。",
    id: "local-services",
    label: "Local Services",
    state: "unavailable",
    statusLabel: "未连接",
  },
];

const initialHealth: StackHealthResult = {
  apiBaseUrl: publicEnv.apiBaseUrl,
  apiVersion: "0.1.0",
  cards: defaultCards,
  contractStatus: "current",
  runtimeMode: "local",
};

const futureRegions = [
  "对话",
  "参数",
  "素材",
  "预览",
  "历史",
  "生成",
  "导出",
  "3D",
];

const cardIcons: Record<FoundationStatusId, LucideIcon> = {
  api: Activity,
  contracts: Braces,
  "local-services": Server,
  web: Monitor,
  worker: CircleDashed,
};

export default function Home() {
  const [health, setHealth] = useState<StackHealthResult>(initialHealth);
  const [isChecking, setIsChecking] = useState(false);
  const [hasError, setHasError] = useState(false);

  async function handleHealthCheck() {
    setIsChecking(true);
    setHasError(false);

    try {
      setHealth(await checkStackHealth());
    } catch {
      setHasError(true);
    } finally {
      setIsChecking(false);
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="flex min-h-14 items-center justify-between border-b border-border bg-card px-6 max-[640px]:min-h-[72px] max-[640px]:items-start max-[640px]:gap-3 max-[640px]:px-4 max-[640px]:py-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-primary">
            <Monitor aria-hidden="true" className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-xl font-semibold leading-[1.2]">
              痛车设计 Agent
            </p>
            <p className="truncate text-xs text-secondary-foreground">
              Foundation workbench
            </p>
          </div>
          <Badge className="shrink-0" variant="muted">
            local
          </Badge>
        </div>
        <Button
          aria-label="检查堆栈健康"
          className="max-[640px]:min-h-11 max-[640px]:px-3"
          disabled={isChecking}
          onClick={handleHealthCheck}
          type="button"
        >
          {isChecking ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
          )}
          {isChecking ? "正在检查服务..." : "检查堆栈健康"}
        </Button>
      </header>

      <div className="grid min-h-[calc(100vh-88px)] grid-cols-[280px_1fr] max-[900px]:grid-cols-1">
        <nav
          aria-label="工作台区域"
          className="border-r border-border bg-card p-4 max-[900px]:border-b max-[900px]:border-r-0"
        >
          <div className="flex flex-col gap-2 max-[900px]:flex-row max-[900px]:overflow-x-auto">
            <button
              className="flex min-h-9 items-center justify-between rounded-md border-l-2 border-primary bg-muted px-3 py-2 text-left text-sm font-semibold text-foreground max-[900px]:min-w-32"
              type="button"
            >
              Foundation
              <ChevronRight aria-hidden="true" className="h-4 w-4 text-primary" />
            </button>
            {futureRegions.map((region) => (
              <button
                aria-describedby="future-region-note"
                aria-disabled="true"
                className="flex min-h-9 items-center justify-between rounded-md border border-border bg-card px-3 py-2 text-left text-sm text-muted-foreground max-[640px]:min-h-11 max-[900px]:min-w-28"
                disabled
                key={region}
                title="后续阶段开放"
                type="button"
              >
                <span>{region}</span>
                <span className="text-xs">后续阶段开放</span>
              </button>
            ))}
          </div>
          <p className="mt-4 text-xs text-secondary-foreground" id="future-region-note">
            后续阶段开放
          </p>
        </nav>

        <main className="min-w-0 px-6 py-6 max-[640px]:px-4">
          <section aria-labelledby="foundation-heading" className="mx-auto max-w-7xl">
            <div className="mb-6 flex items-start justify-between gap-4 max-[640px]:flex-col">
              <div>
                <h1
                  className="text-[28px] font-semibold leading-[1.15]"
                  id="foundation-heading"
                >
                  工作台基础已就绪
                </h1>
                <p className="mt-2 max-w-3xl text-sm text-secondary-foreground">
                  当前阶段只验证项目骨架、服务健康和 API 合约。聊天、上传、预览、生成和导出会在后续阶段开放。
                </p>
              </div>
              <Badge variant={health.contractStatus === "current" ? "default" : "warning"}>
                {health.contractStatus === "current"
                  ? "API 合约已生成"
                  : "API 合约需要重新生成"}
              </Badge>
            </div>

            {hasError ? (
              <Alert className="mb-6">
                <AlertCircle aria-hidden="true" className="mr-2 inline h-4 w-4 text-destructive" />
                <AlertTitle>基础服务暂不可用。</AlertTitle>
                <AlertDescription>
                  请确认本地服务已启动，并重新运行健康检查。
                </AlertDescription>
              </Alert>
            ) : null}

            <div
              aria-live="polite"
              className="grid grid-cols-5 gap-4 max-[1200px]:grid-cols-3 max-[900px]:grid-cols-2 max-[640px]:grid-cols-1"
            >
              {health.cards.map((card) => (
                <FoundationCard card={card} key={card.id} />
              ))}
            </div>
          </section>
        </main>
      </div>

      <footer className="flex min-h-8 items-center justify-between gap-4 border-t border-border bg-card px-6 text-xs text-secondary-foreground max-[640px]:min-h-16 max-[640px]:flex-col max-[640px]:items-start max-[640px]:justify-center max-[640px]:px-4">
        <span>local mode: {health.runtimeMode}</span>
        <span>API base URL: {health.apiBaseUrl}</span>
        <span>
          contract:{" "}
          {health.contractStatus === "current"
            ? "API 合约已生成"
            : "API 合约需要重新生成"}
        </span>
      </footer>
    </div>
  );
}

function FoundationCard({ card }: { card: FoundationStatusCard }) {
  const Icon = cardIcons[card.id];

  return (
    <Card className={cn("min-h-40", card.state === "current" && "border-primary")}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted text-primary">
              <Icon aria-hidden="true" className="h-4 w-4" />
            </div>
            <CardTitle className="truncate">{card.label}</CardTitle>
          </div>
          <Badge variant={statusVariant(card.state)}>{card.statusLabel}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-secondary-foreground">{card.detail}</p>
      </CardContent>
    </Card>
  );
}

function statusVariant(
  state: FoundationStatusCard["state"],
): "default" | "muted" | "warning" {
  if (state === "connected" || state === "current") {
    return "default";
  }

  if (state === "not-configured") {
    return "muted";
  }

  return "warning";
}
