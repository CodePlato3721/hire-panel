# TASKS.md

当前进行中的工程：**前后端分离重构 — 前端阶段**

目标：用 Vite + React + TypeScript 构建前端，对接已完成的 FastAPI 后端。

---

## 已完成

- [x] **Step 1** — `pyproject.toml` 新增后端依赖 + `backend/services/db.py`（AsyncPostgresSaver）
- [x] **Step 2** — `backend/main.py`（FastAPI app + lifespan）
- [x] **Step 3** — `backend/routers/sessions.py` + `backend/schemas/session.py`（POST/GET /api/sessions）

---

## 待完成

- [x] **Task A** — pipeline graphs 改为 checkpointer 参数注入
  `pipeline/jd_graph.py`、`resume_graph.py`、`feedback_graph.py` 将 `InMemorySaver()` 改为外部传入，pipeline 层。

- [x] **Task C** — JD 端点
  `POST /api/sessions/{session_id}/jd`（提交 JD，启动 JD graph，SSE 流）
  `POST /api/sessions/{session_id}/jd/reply`（审批/修改 criteria，恢复 graph，SSE 流）
  router 内直接调用 `build_jd_graph(get_checkpointer())`，router + schema 层。

- [x] **Task D** — Resume 端点
  `POST /api/sessions/{session_id}/resumes`（上传文件，运行 resume graph，SSE 流）
  router 内直接调用 `build_resume_graph(get_checkpointer())`，router + schema 层。

- [x] **Task E** — Feedback 端点
  `POST /api/sessions/{session_id}/feedback`（提交反馈，运行 feedback graph，SSE 流）
  router 内直接调用 `build_feedback_graph(get_checkpointer())`，router + schema 层。

- [x] **Task F** — 真实 session 状态推导
  `GET /api/sessions/{session_id}` 从 checkpointer 读取 graph 状态，推导真实 stage / criteria / resumes。
  router 层。

- [x] **Task G** — CORS middleware
  `backend/main.py` 加 `CORSMiddleware`，允许 React dev server（localhost:5173）跨域。
  app 层。

---

## 前端阶段

- [ ] **Task H** — Scaffold + API 客户端层
  创建 `frontend/` 目录，Vite React TS 项目，`src/api.ts` 封装所有 HTTP + SSE 调用（5 个后端端点）。

- [ ] **Task I** — App shell：两栏布局 + Session 生命周期
  `App.tsx` 管理 session（localStorage 存 session_id，启动时创建或恢复），渲染左右两栏骨架。

- [ ] **Task J** — JD 流程
  "Fill JD" 按钮 → 文本输入 → `POST /jd`（SSE）→ interrupt 时展示审批界面 → `POST /jd/reply` → 左栏显示 criteria。

- [ ] **Task K** — Resume 上传流程
  "Upload Resumes" 按钮 → 文件选择（PDF/txt）→ `POST /resumes`（multipart，SSE）→ 左栏表格显示评分。

- [ ] **Task L** — Feedback/Chat 流程
  右栏输入框 → `POST /feedback`（SSE）→ 左栏表格实时更新简历评分。
