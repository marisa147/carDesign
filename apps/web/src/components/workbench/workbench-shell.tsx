import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { publicEnv } from "@/lib/config/public-env";
import { cn } from "@/lib/utils";

interface WorkbenchShellProps {
  assets: ReactNode;
  chat: ReactNode;
  futureGates: ReactNode;
  history: ReactNode;
  parameters: ReactNode;
  preview: ReactNode;
  progress: ReactNode;
}

export function WorkbenchShell({
  assets,
  chat,
  futureGates,
  history,
  parameters,
  preview,
  progress,
}: WorkbenchShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="flex min-h-14 items-center justify-between gap-4 border-b border-border bg-card px-5 max-[720px]:min-h-[72px] max-[720px]:flex-wrap max-[720px]:px-4 max-[720px]:py-3">
        <div className="min-w-0">
          <h1 className="truncate text-xl font-semibold leading-[1.2]">
            痛车设计 Agent
          </h1>
          <p className="truncate text-xs text-secondary-foreground">
            AI workbench
          </p>
        </div>
        <div className="flex min-w-0 flex-wrap items-center justify-end gap-2 text-xs">
          <Badge variant="muted">local</Badge>
          <Badge variant="default">API 合约已生成</Badge>
          <span className="truncate text-secondary-foreground">
            API base URL: {publicEnv.apiBaseUrl}
          </span>
        </div>
      </header>

      <main className="grid min-h-[calc(100vh-56px)] grid-cols-[minmax(300px,360px)_minmax(420px,1fr)_minmax(320px,380px)] gap-4 p-4 max-[1180px]:grid-cols-[minmax(300px,360px)_1fr] max-[840px]:grid-cols-1 max-[540px]:p-3">
        <WorkbenchPanel className="max-[840px]:order-1" title="对话">
          {chat}
        </WorkbenchPanel>

        <section className="flex min-w-0 flex-col gap-4 max-[840px]:order-2">
          <WorkbenchPanel title="2D 预览">{preview}</WorkbenchPanel>
          <div className="grid grid-cols-[minmax(0,1fr)_minmax(220px,0.8fr)] gap-4 max-[720px]:grid-cols-1">
            <WorkbenchPanel title="进度">{progress}</WorkbenchPanel>
            <WorkbenchPanel title="历史方案">{history}</WorkbenchPanel>
          </div>
        </section>

        <aside className="flex min-w-0 flex-col gap-4 max-[1180px]:col-span-2 max-[840px]:order-3 max-[840px]:col-span-1">
          <WorkbenchPanel title="参数">{parameters}</WorkbenchPanel>
          <WorkbenchPanel title="素材">{assets}</WorkbenchPanel>
          <WorkbenchPanel title="未来能力">{futureGates}</WorkbenchPanel>
        </aside>
      </main>
    </div>
  );
}

function WorkbenchPanel({
  children,
  className,
  title,
}: {
  children: ReactNode;
  className?: string;
  title: string;
}) {
  return (
    <section
      aria-labelledby={`${title}-heading`}
      className={cn(
        "min-w-0 rounded-md border border-border bg-card p-4",
        className,
      )}
    >
      <h2 className="text-lg font-semibold leading-[1.25]" id={`${title}-heading`}>
        {title}
      </h2>
      <div className="mt-3 min-w-0">{children}</div>
    </section>
  );
}
