# Phase 30 Context: Construction Brief And Smart Q&A

## Goal

Make the assistant start a customization process with the user instead of only categorizing a prompt. Submitting a requirement should surface missing core fields, allow GPT/design supplementation intent, and update the right-side construction brief so the user understands what is ready, missing, saved, or discarded.

## Requirements

- BRIF-01: User can start a customization conversation where the assistant asks missing core fields one by one.
- BRIF-02: User can allow GPT to supplement reasonable design details instead of only classifying the input.
- BRIF-03: User can review and edit a right-side construction-order brief grouped by 车型, 范围, 设计, 素材, 导出, and 风险.
- BRIF-04: The system treats vehicle template, character/theme, main color, wrap range, and text/logo as required core fields for generation readiness.
- BRIF-05: Construction, authorization, and delivery-risk fields show warnings when incomplete but do not block the first v5 generation flow.
- BRIF-06: User can create a new conversation, clear the current conversation, save a draft, and discard a draft without losing saved workspace state.

## Current System

- `ChatPanel` already renders messages and a saved brief summary.
- `WorkbenchApp.handleChatSubmit` creates a user message and generation brief from the submitted prompt.
- `ParameterPanel` already supports save, generate, new concept, and archive current brief.
- `handleNewConversation` currently clears workspace state and local storage.
- The OpenAI parser prompt already instructs GPT not to only classify, but the UI does not yet make missing fields or supplementation visible.

## Scope

In scope:
- Frontend requirement-completion model derived from saved brief payloads.
- Chat follow-up panel with one-by-one missing core question and GPT supplementation cue.
- Clear conversation control separate from new conversation.
- Construction-order grouping in the right panel.
- Tests for ChatPanel missing-field/Q&A controls and ParameterPanel construction grouping.

Out of scope:
- Persisted multi-turn assistant messages in the database.
- New backend conversation tables.
- Full GPT autonomous brief completion beyond existing parser boundary.
- Blocking generation on incomplete construction details.
