"use client";

import type {
  DesignBriefResponse,
  GenerationBriefPayload,
  GenerationBriefResponse,
  MessageResponse,
} from "@caragent/contracts";
import { AlertTriangle, Loader2, MessageSquareText, Plus, Send, Trash2, UserRound } from "lucide-react";
import { useSyncExternalStore } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export type WorkbenchBrief = DesignBriefResponse | GenerationBriefResponse;

const subscribeClientReady = () => () => undefined;
const getClientReadySnapshot = () => true;
const getServerClientReadySnapshot = () => false;

interface ChatPanelProps {
  currentBrief: WorkbenchBrief | null;
  draft: string;
  error: string | null;
  isLoading: boolean;
  isSubmitting: boolean;
  messages: MessageResponse[];
  onDraftChange: (value: string) => void;
  onClearConversation: () => void;
  onNewConversation: () => void;
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
  onClearConversation,
  onNewConversation,
  onSubmit,
}: ChatPanelProps) {
  const isClientReady = useSyncExternalStore(
    subscribeClientReady,
    getClientReadySnapshot,
    getServerClientReadySnapshot,
  );

  const isInputLocked = !isClientReady || isLoading || isSubmitting;
  const canSubmit = draft.trim().length > 0 && !isInputLocked;
  const canStartNewConversation =
    isClientReady &&
    !isLoading &&
    !isSubmitting &&
    (draft.trim().length > 0 || messages.length > 0 || currentBrief !== null);
  const canClearConversation =
    isClientReady && !isLoading && !isSubmitting && (draft.trim().length > 0 || messages.length > 0);
  const briefAssistantMessage = currentBrief
    ? buildBriefAssistantMessage(currentBrief)
    : null;

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
          描述车型、角色、风格、颜色、文案和参考素材后，我会整理成可生成的结构化 brief；也可以直接说“交给 GPT 补充设计”。
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

        {briefAssistantMessage ? (
          <SystemMessage badge="brief">
            <span className="block font-medium text-foreground">结构化 brief 已保存</span>
            <span className="mt-1 block">{briefAssistantMessage.summary}</span>
            <span className="mt-1 block">{briefAssistantMessage.followUp}</span>
          </SystemMessage>
        ) : null}

        {currentBrief ? <RequirementCompletionPanel brief={currentBrief} /> : null}

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
        <div className="flex items-center justify-between gap-2">
          <label
            className="text-xs font-medium text-secondary-foreground"
            htmlFor="workbench-prompt"
          >
            设计需求
          </label>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              disabled={!canClearConversation}
              onClick={onClearConversation}
              size="sm"
              type="button"
              variant="outline"
            >
              <Trash2 aria-hidden="true" className="h-4 w-4" />
              清除对话
            </Button>
            <Button
              disabled={!canStartNewConversation}
              onClick={onNewConversation}
              size="sm"
              type="button"
              variant="outline"
            >
              <Plus aria-hidden="true" className="h-4 w-4" />
              新建对话
            </Button>
          </div>
        </div>
        <textarea
          className="mt-2 min-h-28 w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm leading-6 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
          disabled={isInputLocked}
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

function buildBriefAssistantMessage(brief: WorkbenchBrief) {
  const payload = brief.payload as Partial<GenerationBriefPayload>;
  const summaryParts = [
    formatSummaryPart("主题", readBriefString(payload, "character_theme")),
    formatSummaryPart("风格", readBriefString(payload, "style")),
    formatSummaryPart("配色", readBriefStringArray(payload, "palette").join("、")),
    formatSummaryPart("文字", readBriefStringArray(payload, "text").join("、")),
  ].filter(Boolean);
  const missingPrompts = [
    readBriefString(payload, "character_focus") ? null : "角色在车身上的构图位置",
    readBriefStringArray(payload, "supporting_graphics").length > 0 ? null : "辅助图形元素",
    readBriefString(payload, "typography_intent") ? null : "文字排版方向",
    readBriefString(payload, "color_harmony") ? null : "颜色比例",
  ].filter((item): item is string => Boolean(item));

  return {
    followUp:
      missingPrompts.length > 0
        ? `还可以继续补充：${missingPrompts.slice(0, 3).join("、")}。`
        : "信息已足够，可以直接生成概念。",
    summary:
      summaryParts.length > 0
        ? `已写入右侧概念：${summaryParts.join("；")}。`
        : "已写入右侧概念。",
  };
}

function formatSummaryPart(label: string, value: string): string | null {
  return value ? `${label}：${value}` : null;
}

function readBriefString(
  payload: Partial<GenerationBriefPayload>,
  key: keyof GenerationBriefPayload,
): string {
  const value = payload[key];
  return typeof value === "string" ? value : "";
}

function readBriefStringArray(
  payload: Partial<GenerationBriefPayload>,
  key: keyof GenerationBriefPayload,
): string[] {
  const value = payload[key];
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}


interface RequirementFieldState {
  label: string;
  missing: boolean;
  question: string;
}

function RequirementCompletionPanel({ brief }: { brief: WorkbenchBrief }) {
  const payload = brief.payload as Partial<GenerationBriefPayload>;
  const fields = buildRequiredFieldState(payload);
  const missingFields = fields.filter((field) => field.missing);
  const firstQuestion = missingFields[0]?.question;
  const gptSupplementRequested = requestsGptSupplement(readBriefString(payload, "original_request"));

  return (
    <div className="rounded-md border border-border bg-card p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <MessageSquareText aria-hidden="true" className="h-4 w-4 text-primary" />
          需求补全
        </div>
        <Badge variant={missingFields.length === 0 ? "primary" : "warning"}>
          {missingFields.length === 0 ? "可生成" : `${missingFields.length} 项待补充`}
        </Badge>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 max-[520px]:grid-cols-1">
        {fields.map((field) => (
          <span
            className="inline-flex min-h-8 items-center justify-between gap-2 rounded-md border border-border bg-background px-2 text-xs"
            key={field.label}
          >
            {field.label}
            <Badge variant={field.missing ? "warning" : "primary"}>
              {field.missing ? "待补充" : "已填写"}
            </Badge>
          </span>
        ))}
      </div>
      {firstQuestion ? (
        <p className="mt-3 rounded-md border border-border bg-muted px-3 py-2 text-sm text-secondary-foreground">
          下一步：{firstQuestion}
        </p>
      ) : (
        <p className="mt-3 rounded-md border border-border bg-muted px-3 py-2 text-sm text-secondary-foreground">
          核心需求已齐，可以继续细化分区或直接生成概念。
        </p>
      )}
      {gptSupplementRequested ? (
        <p className="mt-2 text-xs font-medium text-primary">
          已识别“交给 GPT 补充”意图：系统会允许 GPT 补全合理的风格、构图、配色和分区建议。
        </p>
      ) : null}
    </div>
  );
}

function buildRequiredFieldState(
  payload: Partial<GenerationBriefPayload>,
): RequirementFieldState[] {
  return [
    {
      label: "车型模板",
      missing: !readBriefString(payload, "vehicle_template_id"),
      question: "这次要基于哪一个车型模板？",
    },
    {
      label: "角色/主题",
      missing: !readBriefString(payload, "character_theme"),
      question: "这套痛车的角色或主题是什么？",
    },
    {
      label: "主色",
      missing: readBriefStringArray(payload, "palette").length === 0,
      question: "主色和辅助色希望怎么搭配？",
    },
    {
      label: "包覆范围",
      missing: !readBriefString(payload, "coverage"),
      question: "要覆盖哪些区域，例如车门、后翼子板、引擎盖或全车？",
    },
    {
      label: "文字/Logo",
      missing:
        readBriefStringArray(payload, "text").length === 0 &&
        readBriefStringArray(payload, "overlay_logo_asset_ids").length === 0,
      question: "需要放哪些文字、编号或 Logo？",
    },
  ];
}

function requestsGptSupplement(value: string): boolean {
  const normalized = value.toLowerCase();
  return /gpt|ai|补充|你来|自行|自动|发挥|完善/.test(normalized);
}
