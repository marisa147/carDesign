"use client";

import type {
  DesignBriefResponse,
  GenerationBriefResponse,
  MessageResponse,
} from "@caragent/contracts";
import { AlertTriangle, Loader2, MessageSquareText, Send, UserRound } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export type WorkbenchBrief = DesignBriefResponse | GenerationBriefResponse;

interface ChatPanelProps {
  currentBrief: WorkbenchBrief | null;
  draft: string;
  error: string | null;
  isLoading: boolean;
  isSubmitting: boolean;
  messages: MessageResponse[];
  onDraftChange: (value: string) => void;
  onSubmit: () => void;
}

export function ChatPanel({
  currentBrief,
  draft,
  error,
  isLoading,
  isSubmitting,
  messages,
  onDraftChange,
  onSubmit,
}: ChatPanelProps) {
  const canSubmit = draft.trim().length > 0 && !isLoading && !isSubmitting;

  return (
    <form
      className="flex min-h-[520px] flex-col gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSubmit) {
          onSubmit();
        }
      }}
    >
      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
        <SystemMessage>
          描述车型、角色、风格、颜色、文案和参考素材后，我会整理成可生成的结构化 brief。
        </SystemMessage>

        {isLoading ? (
          <div className="flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-sm text-secondary-foreground">
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin text-primary" />
            正在恢复工作台记录
          </div>
        ) : null}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {currentBrief ? (
          <SystemMessage badge="brief">
            结构化 brief 已保存
          </SystemMessage>
        ) : null}

        {error ? (
          <div
            className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
            role="alert"
          >
            <AlertTriangle aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : null}
      </div>

      <div className="mt-auto">
        <label
          className="text-xs font-medium text-secondary-foreground"
          htmlFor="workbench-prompt"
        >
          设计需求
        </label>
        <textarea
          className="mt-2 min-h-28 w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm leading-6 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
          disabled={isSubmitting}
          id="workbench-prompt"
          onChange={(event) => {
            onDraftChange(event.target.value);
          }}
          placeholder="例如：白色双门车，樱色女主角，车门文字 MOON DRIVE，清爽赛博风。"
          value={draft}
        />
        <Button className="mt-3 w-full" disabled={!canSubmit} type="submit">
          {isSubmitting ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <Send aria-hidden="true" className="h-4 w-4" />
          )}
          发送需求
        </Button>
      </div>
    </form>
  );
}

function ChatMessage({ message }: { message: MessageResponse }) {
  const isUser = message.role === "user";

  return (
    <div
      className={
        isUser
          ? "rounded-md border border-primary/25 bg-primary/10 p-3"
          : "rounded-md border border-border bg-muted p-3"
      }
    >
      <div className="flex items-center gap-2 text-sm font-semibold">
        {isUser ? (
          <UserRound aria-hidden="true" className="h-4 w-4 text-primary" />
        ) : (
          <MessageSquareText aria-hidden="true" className="h-4 w-4 text-primary" />
        )}
        {isUser ? "你" : "系统"}
      </div>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-foreground">
        {message.content}
      </p>
    </div>
  );
}

function SystemMessage({
  badge,
  children,
}: {
  badge?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-md border border-border bg-muted p-3">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <MessageSquareText aria-hidden="true" className="h-4 w-4 text-primary" />
        系统
        {badge ? <Badge variant="muted">{badge}</Badge> : null}
      </div>
      <p className="mt-2 text-sm leading-6 text-secondary-foreground">{children}</p>
    </div>
  );
}
