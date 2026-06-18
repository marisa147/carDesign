# 痛车设计生成 Agent 项目计划（含前端 UI/UX）

## 1. 项目背景与目标
痛车设计生成 Agent 项目旨在利用 AI 技术自动生成高质量痛车设计图案，实现用户文字提示 → 图像生成 → 3D 贴图预览 → 可下载方案的闭环流程。

项目目标：
- 支持动漫角色 / 风格 / 颜色 / 文案输入
- 生成高分辨率、风格统一的痛车设计
- 提供 2D / 3D 预览及下载功能
- 提供类似 GPT 聊天页面的操作体验
- 可扩展多车型、多角色组合、自动文案生成等功能

---

## 2. 核心设计理念
1. **模块化 Agent 架构**：每个 Agent 聚焦单一职责，支持替换和扩展
2. **任务调度与闭环**：Planner / Orchestrator 管理任务流，支持迭代反馈
3. **多模态协作**：支持文字、图片、3D 模型等多种输入输出
4. **可回溯和日志**：记录全过程输入、输出、参数和版本
5. **前端 UI/UX 体验**：GPT 风格聊天交互 + 右侧 3D/2D 模型预览

---

## 3. 功能模块设计

### 3.1 用户输入解析 Agent
- 功能：
  - 校验用户输入（车型、角色、风格、颜色、文案）
  - 输出结构化任务参数
- 技术：
  - Python + Pydantic
  - 可选 GPT 系列解析自然语言

### 3.2 Prompt / 风格规划 Agent
- 功能：
  - 根据用户需求生成 AI Prompt
  - 生成 ControlNet 条件信息
- 技术：
  - LangGraph / LangChain
  - Prompt 模板管理系统

### 3.3 文案生成 Agent
- 功能：
  - 自动生成车身口号、副标题、贴花文案
- 技术：
  - GPT / Claude 类 LLM

### 3.4 图像生成 Agent
- 功能：
  - 调用 SDXL / FLUX / DALL·E + LoRA
  - 支持 Inpainting 局部重绘
- 技术：
  - Python + HuggingFace diffusers
  - GPU + Docker 容器化

### 3.5 控制与贴图 Agent
- 功能：
  - Mask / ControlNet / IP-Adapter 贴图控制
  - 图像局部增强
- 技术：
  - OpenCV + Pillow + Inpainting / Real-ESRGAN

### 3.6 后处理 Agent
- 功能：
  - 图像增强、去瑕疵、高清放大
- 技术：
  - OpenCV / Pillow / Real-ESRGAN

### 3.7 预览输出 Agent
- 功能：
  - 2D / 3D 模型可视化预览
  - 用户下载导出
- 技术：
  - Three.js / Canvas / Fabric.js
  - 支持缩放、旋转、拖拽、视角切换

### 3.8 Feedback & Evaluation Agent
- 功能：
  - 用户对生成结果打分或提出修改
  - 自动评估风格一致性、清晰度、贴合度
  - 不满意 → 任务迭代 / Prompt 调整
- 技术：
  - Python + Celery / Redis
  - 日志记录、版本管理

---

## 4. 前端 UI/UX 设计

### 4.1 布局设计
- **左侧聊天窗口**
  - 类似 GPT 页面
  - 显示用户输入与系统生成的设计反馈
  - 支持多轮对话与历史折叠
  - 快捷按钮（再生成 / 局部修改 / 风格切换）
- **右侧 3D / 2D 模型窗口**
  - 显示 3D 模型或贴图效果
  - 支持缩放 / 旋转 / 平移
  - 可切换视角（左/右/前/后/俯视/自由视角）
  - 下方显示多方案缩略图，点击切换
- **顶部工具栏**
  - 模型选择、贴花模板、渲染模式切换、保存/导出按钮
- **底部状态栏**
  - 渲染进度、Token 消耗、API 状态提示

### 4.2 交互优化
- 双向联动：
  - 聊天修改 → 右侧 3D/2D 实时更新
  - 右侧操作（旋转/选择贴花） → 自动生成聊天反馈
- 反馈循环：
  - 用户可点赞 / 点踩 / 再生成，自动调整 Prompt 或参数
- 响应式布局：
  - 窗口宽度变化自动调整左/右比例
  - 手机 / 平板：上下布局，聊天在上，3D 模型在下

### 4.3 视觉优化
- GPT 风格对话气泡 + 深色 3D 背景
- 紫色主题高亮按钮 / 交互元素
- 渲染中显示 Loading / 动态粒子 / 进度条
- 高分辨率贴图与高清渲染显示

---

## 5. 技术选型

| 层 | 技术栈 | 说明 |
|----|--------|------|
| 前端 | React / TypeScript + Three.js / Canvas | 聊天交互 + 3D/2D 预览 |
| Agent 调度 | Python + LangGraph / FastAPI + Celery / Redis | 多 Agent 协作与异步调度 |
| 图像生成 | SDXL / FLUX / DALL·E + LoRA | 高质量可控生成 |
| 图像处理 | OpenCV / Pillow / Real-ESRGAN | 贴图、增强、超分 |
| 数据存储 | PostgreSQL + MinIO / S3 | 素材、任务记录、版本管理 |
| 部署 | Docker + GPU 云服务 | 容器化、可扩展部署 |

---

## 6. 系统流程

1. 用户输入需求（车型/角色/风格/文案）
2. 上传素材（车辆照片、角色立绘、参考图、Logo）
3. 用户输入解析 Agent → 输出结构化参数
4. Prompt / 风格规划 Agent → 生成控制信息
5. 文案生成 Agent → 输出车身文案
6. 图像生成 Agent → 输出初稿
7. 控制与贴图 Agent → Mask / ControlNet / 局部增强
8. 后处理 Agent → 图像增强 / 修复
9. 预览输出 Agent → 2D / 3D 展示
10. Feedback & Evaluation → 迭代优化
11. 最终方案导出 / 用户下载

---

## 7. 原型开发计划

### 阶段 1：单 Agent 原型
- Python + FastAPI + Gradio / Streamlit
- 实现文字输入 → 图像生成 → 下载

### 阶段 2：多 Agent 协作
- Planner / Orchestrator
- 风格规划 + 文案生成 + 后处理 Agent
- 支持迭代反馈闭环

### 阶段 3：前端 UI/UX 集成
- React / TypeScript + Three.js / Canvas
- GPT 风格聊天界面
- 2D / 3D 模型实时预览
- 多方案缩略图展示

### 阶段 4：系统优化与扩展
- 多车型 / 多角色组合
- 自动文案生成
- 报价与下单系统
- GPU 并行生成 + 缓存优化

---

## 8. 项目里程碑

| 阶段 | 时间 | 输出 |
|------|------|------|
| 原型开发 | 1个月 | 单 Agent 流程可运行 |
| 多 Agent 协作 | 2个月 | Planner + 多 Agent 闭环 |
| 前端集成 | 1个月 | 2D/3D 可视化 + 聊天交互 |
| 系统优化 | 1-2个月 | 扩展功能 + 性能优化 + 上线部署 |

---

## 9. 风险与对策

| 风险 | 对策 |
|------|------|
| 图像生成效果不稳定 | LoRA 微调 + ControlNet 精确控制 |
| 用户需求难以结构化 | GPT 辅助解析 + 校验机制 |
| 系统性能瓶颈 | GPU 并行 + 异步队列 + 缓存 |
| 多 Agent 协作复杂 | Planner / Orchestrator + 日志追踪 |

---

## 10. 推荐落地方式
- 核心 Agent 编排、模型调用、图像处理：Python
- 前端交互与 2D/3D 预览：TypeScript + React + Three.js
- 建议先做单 Agent 原型，再演进为多 Agent 协作系统
