import type { DesignVersionResponse } from "@caragent/contracts";
import { GitBranch } from "lucide-react";

import { Button } from "@/components/ui/button";

interface IterationPanelProps {
  changeRequest: string;
  error: string | null;
  isSubmitting: boolean;
  notice: string | null;
  onChangeRequestChange: (value: string) => void;
  onSubmit: () => void;
  selectedVersion: DesignVersionResponse | null;
  workspaceReady: boolean;
}

export function IterationPanel({
  changeRequest,
  error,
  isSubmitting,
  notice,
  onChangeRequestChange,
  onSubmit,
  selectedVersion,
  workspaceReady,
}: IterationPanelProps) {
  const canSubmit =
    workspaceReady &&
    selectedVersion !== null &&
    changeRequest.trim().length > 0 &&
    !isSubmitting;

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
        <GitBranch aria-hidden="true" className="h-4 w-4 text-primary" />
        <div className="min-w-0">
          <p className="text-sm font-semibold">子迭代</p>
          <p className="truncate text-xs text-secondary-foreground">
            基于: {selectedVersion?.title ?? "未选择版本"}
          </p>
        </div>
      </div>

      <label className="grid gap-1 text-xs font-medium text-secondary-foreground">
        迭代需求
        <textarea
          className="min-h-20 resize-y rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
          disabled={!workspaceReady || selectedVersion === null || isSubmitting}
          onChange={(event) => {
            onChangeRequestChange(event.target.value);
          }}
          value={changeRequest}
        />
      </label>

      {notice ? <p className="text-xs text-primary">{notice}</p> : null}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <Button disabled={!canSubmit} type="submit">
        {isSubmitting ? "提交中" : "生成子迭代"}
      </Button>
    </form>
  );
}
