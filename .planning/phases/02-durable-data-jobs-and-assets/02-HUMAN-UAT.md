---
phase: 02-durable-data-jobs-and-assets
status: passed
scope: "Phase 2 durable workspace/job refresh proof"
created: 2026-06-17
updated: 2026-06-17
---

# Phase 2 Human UAT: Durable Refresh Proof

This checklist verifies the minimal Phase 2 persistence proof only. Real image generation, full chat, upload manager, 2D/3D preview, iteration, export, and production handoff remain out of scope for this UAT.

## Preconditions

- Docker services are running with PostgreSQL, Redis, and MinIO available.
- API service is running against the same database used by the web shell.
- Web app is running with `NEXT_PUBLIC_API_BASE_URL` pointing to the API.
- No real provider credentials or hosted image-generation calls are required.

## Checklist

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the web shell. | Foundation shell loads and future workbench regions remain disabled. |
| 2 | Click `创建持久工作区`. | A workspace ID appears, message count becomes `1`, and only the workspace ID is stored in browser local storage. |
| 3 | Click `创建模拟任务`. | A job status appears from API-backed state, event count becomes at least `1`, and the idempotency key is stored locally. |
| 4 | Refresh the browser. | The same workspace ID, message count, job status, and event count are refetched from the API and remain visible. |
| 5 | Click `刷新状态`. | Workspace/job state is fetched again without creating a second workspace. |
| 6 | Repeat `创建模拟任务` with the stored idempotency key. | API returns the durable idempotent job state instead of requiring a real provider call. |

## Pass Criteria

- Workspace state survives refresh because canonical state is loaded from the API.
- Job status and events survive refresh because they are read from durable storage.
- The UI does not expose real prompt input, upload, preview, export, true 3D, or production-generation controls.
- No object-storage credentials, provider secrets, or raw binary data appear in browser-visible state.

## Run Results

Executed on 2026-06-17 with Docker-backed PostgreSQL/Redis/MinIO, Alembic head applied, local API on `127.0.0.1:8000`, and web on `127.0.0.1:3000`.

| Step | Result |
|------|--------|
| Open web shell | Passed |
| Click `创建持久工作区` | Passed; workspace ID appeared and message count became `1`. |
| Click `创建模拟任务` | Passed; queued job state was persisted. |
| Refresh browser | Passed; same workspace ID, `消息 1`, `事件 1`, and `任务 queued` remained visible. |
| Query API jobs/events | Passed; job count `1`, job status `queued`, event count `1`, event status `queued`. |

Workspace observed during UAT: `26e912ee-af29-49c0-8c38-0719e06b6581`.
