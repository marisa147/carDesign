import "@/test/setup";

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { ChatPanel } from "./chat-panel";

const defaultProps = {
  currentBrief: null,
  draft: "",
  error: null,
  isLoading: false,
  isSubmitting: false,
  messages: [],
  onDraftChange: vi.fn(),
  onClearConversation: vi.fn(),
  onNewConversation: vi.fn(),
  onSubmit: vi.fn(),
};

describe("ChatPanel", () => {
  it("does not expose editable prompt controls before client hydration", () => {
    const html = renderToString(<ChatPanel {...defaultProps} />);

    expect(html).toContain('id="workbench-prompt"');
    expect(html).toMatch(/<textarea[^>]*disabled=""/);
    expect(html).toMatch(/<button[^>]*disabled=""/);
  });

  it("enables submit after hydration when the prompt has content", async () => {
    const user = userEvent.setup();
    const onDraftChange = vi.fn();
    const { rerender } = render(
      <ChatPanel {...defaultProps} onDraftChange={onDraftChange} />,
    );

    const prompt = screen.getByRole("textbox", { name: "设计需求" });
    await waitFor(() => {
      expect(prompt).toBeEnabled();
    });

    await user.type(prompt, "白色双门车，樱色女主角");
    expect(onDraftChange).toHaveBeenCalled();

    rerender(
      <ChatPanel
        {...defaultProps}
        draft="白色双门车，樱色女主角"
        onDraftChange={onDraftChange}
      />,
    );

    expect(screen.getByRole("button", { name: "发送需求" })).toBeEnabled();
  });

  it("starts a new conversation from the chat panel", async () => {
    const user = userEvent.setup();
    const onNewConversation = vi.fn();

    render(
      <ChatPanel
        {...defaultProps}
        currentBrief={{ payload: { character_theme: "初音未来主题" } } as never}
        messages={[
          {
            content: "白色双门车，初音未来主题。",
            created_at: "2026-06-17T00:00:00Z",
            id: "message-1",
            role: "user",
            sequence: 1,
            updated_at: "2026-06-17T00:00:00Z",
            workspace_id: "workspace-1",
          },
        ]}
        onNewConversation={onNewConversation}
      />,
    );

    await user.click(screen.getByRole("button", { name: "新建对话" }));

    expect(onNewConversation).toHaveBeenCalledTimes(1);
  });

  it("summarizes the parsed brief and prompts for missing concept details", () => {
    render(
      <ChatPanel
        {...defaultProps}
        currentBrief={
          {
            payload: {
              character_theme: "初音未来主题",
              palette: ["白色车身", "青绿色线条"],
              style: "干净赛车感",
              text: ["MIKU RACING"],
            },
          } as never
        }
      />,
    );

    expect(screen.getByText("结构化 brief 已保存")).toBeVisible();
    expect(screen.getByText(/已写入右侧概念：主题：初音未来主题/)).toBeVisible();
    expect(screen.getByText(/配色：白色车身、青绿色线条/)).toBeVisible();
    expect(screen.getByText(/还可以继续补充：角色在车身上的构图位置/)).toBeVisible();
  });

  it("asks the first missing required field and recognizes GPT supplementation", () => {
    render(
      <ChatPanel
        {...defaultProps}
        currentBrief={
          {
            payload: {
              character_theme: "初音未来主题",
              coverage: "车门和后翼子板",
              original_request: "GR86 初音未来主题，其他设计交给 GPT 自行补充",
              palette: [],
              text: [],
              vehicle_template_id: "toyota_gr86_brz_v1",
            },
          } as never
        }
      />,
    );

    expect(screen.getByText("需求补全")).toBeVisible();
    expect(screen.getByText("主色")).toBeVisible();
    expect(screen.getByText("2 项待补充")).toBeVisible();
    expect(screen.getByText(/下一步：主色和辅助色希望怎么搭配/)).toBeVisible();
    expect(screen.getByText(/已识别“交给 GPT 补充”意图/)).toBeVisible();
  });

  it("clears the local conversation without starting a new workspace", async () => {
    const user = userEvent.setup();
    const onClearConversation = vi.fn();

    render(
      <ChatPanel
        {...defaultProps}
        draft="临时输入"
        onClearConversation={onClearConversation}
      />,
    );

    await user.click(screen.getByRole("button", { name: "清除对话" }));

    expect(onClearConversation).toHaveBeenCalledTimes(1);
  });

});

