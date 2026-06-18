import type { DesignVersionResponse, FeedbackResponse } from "@caragent/contracts";
import { MessageSquareText, Star } from "lucide-react";

import { Button } from "@/components/ui/button";

type FeedbackApprovalState = "none" | "approved" | "rejected";

interface FeedbackPanelProps {
  approvalState: FeedbackApprovalState;
  comment: string;
  error: string | null;
  feedback: FeedbackResponse[];
  isSubmitting: boolean;
  notice: string | null;
  onApprovalStateChange: (value: FeedbackApprovalState) => void;
  onCommentChange: (value: string) => void;
  onRatingChange: (value: number) => void;
  onSubmit: () => void;
  rating: number | null;
  selectedVersion: DesignVersionResponse | null;
}

const approvalOptions: Array<{ label: string; value: FeedbackApprovalState }> = [
  { label: "中立", value: "none" },
  { label: "通过", value: "approved" },
  { label: "驳回", value: "rejected" },
];

export function FeedbackPanel({
  approvalState,
  comment,
  error,
  feedback,
  isSubmitting,
  notice,
  onApprovalStateChange,
  onCommentChange,
  onRatingChange,
  onSubmit,
  rating,
  selectedVersion,
}: FeedbackPanelProps) {
  const selectedFeedback = selectedVersion
    ? feedback.filter((entry) => entry.version_id === selectedVersion.id)
    : [];
  const hasFeedbackValue =
    rating !== null || approvalState !== "none" || comment.trim().length > 0;
  const canSubmit = selectedVersion !== null && hasFeedbackValue && !isSubmitting;

  return (
    <form
      className="grid gap-3 rounded-md border border-border bg-background p-3"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSubmit) {
          onSubmit();
        }
      }}
    >
      <div className="flex items-center gap-2">
        <MessageSquareText aria-hidden="true" className="h-4 w-4 text-primary" />
        <div className="min-w-0">
          <p className="text-sm font-semibold">版本反馈</p>
          <p className="truncate text-xs text-secondary-foreground">
            版本: {selectedVersion?.title ?? "未选择版本"}
          </p>
        </div>
      </div>

      <div className="grid gap-2">
        <p className="text-xs font-medium text-secondary-foreground">评分</p>
        <div className="grid grid-cols-5 gap-1">
          {[1, 2, 3, 4, 5].map((value) => (
            <Button
              aria-label={`评分 ${value}`}
              aria-pressed={rating === value}
              disabled={selectedVersion === null || isSubmitting}
              key={value}
              onClick={() => {
                onRatingChange(value);
              }}
              size="sm"
              type="button"
              variant={rating === value ? "default" : "outline"}
            >
              <Star aria-hidden="true" className="h-3.5 w-3.5" />
              {value}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-1">
        {approvalOptions.map((option) => (
          <Button
            aria-pressed={approvalState === option.value}
            disabled={selectedVersion === null || isSubmitting}
            key={option.value}
            onClick={() => {
              onApprovalStateChange(option.value);
            }}
            size="sm"
            type="button"
            variant={approvalState === option.value ? "default" : "outline"}
          >
            {option.label}
          </Button>
        ))}
      </div>

      <label className="grid gap-1 text-xs font-medium text-secondary-foreground">
        反馈评论
        <textarea
          className="min-h-20 resize-y rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
          disabled={selectedVersion === null || isSubmitting}
          onChange={(event) => {
            onCommentChange(event.target.value);
          }}
          value={comment}
        />
      </label>

      {notice ? <p className="text-xs text-primary">{notice}</p> : null}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <Button disabled={!canSubmit} type="submit">
        {isSubmitting ? "保存中" : "提交反馈"}
      </Button>

      <div className="grid gap-2 text-sm">
        <p className="text-xs font-medium text-secondary-foreground">反馈历史</p>
        {selectedFeedback.length > 0 ? (
          selectedFeedback.map((entry) => (
            <div className="rounded-md border border-border bg-card px-3 py-2" key={entry.id}>
              <div className="flex flex-wrap gap-2 text-xs text-secondary-foreground">
                <span>评分 {entry.rating ?? "-"}</span>
                <span>{formatApproval(entry.approval_state)}</span>
              </div>
              {entry.comment ? <p className="mt-1 text-sm">{entry.comment}</p> : null}
            </div>
          ))
        ) : (
          <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
            暂无反馈
          </p>
        )}
      </div>
    </form>
  );
}

function formatApproval(value: string): string {
  if (value === "approved") {
    return "通过";
  }
  if (value === "rejected") {
    return "驳回";
  }
  return "中立";
}

export type { FeedbackApprovalState };
