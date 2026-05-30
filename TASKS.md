# TASKS.md

当前进行中的工程：**前后端分离重构 — 后端阶段**

目标：用 FastAPI + PostgreSQL（neon.tech）替代 Streamlit，前端留给后续 React 阶段。

---

## 已完成

- [x] **Step 1** — `pyproject.toml` 新增后端依赖 + `backend/services/db.py`（AsyncPostgresSaver）
- [x] **Step 2** — `backend/main.py`（FastAPI app + lifespan）
- [x] **Step 3** — `backend/routers/sessions.py` + `backend/schemas/session.py`（POST/GET /api/sessions）

---

## 待完成

- [x] **Task A** — pipeline graphs 改为 checkpointer 参数注入
  `pipeline/jd_graph.py`、`resume_graph.py`、`feedback_graph.py` 将 `InMemorySaver()` 改为外部传入，pipeline 层。

- [ ] **Task B1** — `backend/services/graph_runner.py`（graph 构建）
  三个 `build_*_graph(checkpointer)` 函数，只负责构建 compiled graph，service 层。

- [ ] **Task B2** — `backend/services/graph_runner.py`（SSE 执行）
  追加 `stream_graph()` 函数，执行 graph 并 yield SSE 格式事件，service 层。

- [ ] **Task C** — JD 端点
  `POST /api/sessions/{session_id}/jd`（提交 JD，启动 JD graph，SSE 流）
  `POST /api/sessions/{session_id}/jd/reply`（审批/修改 criteria，恢复 graph，SSE 流）
  router + schema 层。

- [ ] **Task D** — Resume 端点
  `POST /api/sessions/{session_id}/resumes`（上传文件，运行 resume graph，SSE 流）
  router + schema 层。

- [ ] **Task E** — Feedback 端点
  `POST /api/sessions/{session_id}/feedback`（提交反馈，运行 feedback graph，SSE 流）
  router + schema 层。

- [ ] **Task F** — 真实 session 状态推导
  `GET /api/sessions/{session_id}` 从 checkpointer 读取 graph 状态，推导真实 stage / criteria / resumes。
  router 层。

- [ ] **Task G** — CORS middleware
  `backend/main.py` 加 `CORSMiddleware`，允许 React dev server（localhost:5173）跨域。
  app 层。
