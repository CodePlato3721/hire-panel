# CR.md

历史代码改动摘要，按主题归类。数据来源：`cr/` 文件夹下所有已归档 CR 记录。
仅收录涉及代码/配置的改动，CLAUDE.md 和 TASKS.md 的纯文档修改不在此列。

---

## 一、后端基础设施

### 1.1 PostgreSQL DB 服务（cr.20260530115344）

引入 neon.tech PostgreSQL 作为 LangGraph checkpointer 后端。

- `backend/services/db.py` 新增 `init_db()` / `get_checkpointer()` / `close_db()`
- 新增依赖：`fastapi`, `uvicorn[standard]`, `psycopg[binary,pool]`, `langgraph-checkpoint-postgres`

### 1.2 FastAPI 应用入口（cr.20260530160743）

`backend/main.py` 以 lifespan 管理 DB 连接的启动与关闭。

- Windows 下显式设置 `WindowsSelectorEventLoopPolicy`（psycopg3 不兼容 ProactorEventLoop）

### 1.3 Sessions 路由初版（cr.20260530161855）

`POST /api/sessions` 生成 UUID；`GET /api/sessions/{session_id}` 返回固定初始状态 `stage="idle"`。
后续在 1.4 节中改为真实状态推导。

---

## 二、Pipeline 重构

### 2.1 Checkpointer 外部注入（cr.20260530164114 / cr.20260530164954）

三个 pipeline graph（jd / resume / feedback）移除硬编码 `InMemorySaver`，`build_*_graph()` 改为接受外部 `checkpointer` 参数。
决定依据：需要跨请求将图状态持久化到 PostgreSQL。

cr.20260530164954 为最终版本，附带完整集成测试验证（JD 流 5 条 criteria、Resume 评分 49 pts、Feedback 流正常）。

### 2.2 graph_runner 服务：引入后放弃（cr.20260530165946）

新增 `backend/services/graph_runner.py` 封装三个 graph 的构建，随后认定为过早抽象（premature abstraction），决定放弃，graph 构建改为在各 router 内直接内联调用。
临时脚手架 `test_graph_runner.py` 在验证通过后删除。

### 2.3 删除 main.py，pipeline/ 迁移至 backend/（cr.20260602154631）

删除命令行入口 `main.py`；`pipeline/` 整体 `git mv` 至 `backend/pipeline/`，保留 git history。

- 全量替换所有 `from pipeline.*` 导入路径及 `patch("pipeline.*")` 测试 patch 字符串
- 涉及 `services/`、`tests/unit`、`tests/e2e`、`ui/state.py` 共 8+ 文件同步更新
- 测试：27 passed / 0 failed（`pytest tests/unit/`）

---

## 三、API 路由

### 3.1 JD 路由（cr.20260530173318）

- `POST /api/sessions/{id}/jd`：提交 JD 文本，启动 JD graph，SSE 流返回 token
- `POST /api/sessions/{id}/jd/reply`：提交 HR 审批，恢复中断的 graph 执行
- `backend/routers/sse.py` 新增公共函数 `events_to_sse_tokens()`
- 状态通过 PostgreSQL checkpointer 跨请求恢复

### 3.2 Resume 路由（cr.20260530175127）

`POST /api/sessions/{id}/resumes` 接受 PDF / 文本文件上传，从 JD graph checkpoint 读取 `scoring_criteria`，运行 resume graph，SSE 流返回评分结果。

### 3.3 Feedback 路由 + graph_config() helper（cr.20260531144657）

`POST /api/sessions/{id}/feedback` 接受 HR 反馈，继承上一轮 `resumes` 和 `hr_memory`，运行 feedback graph 重新评分，SSE 流返回结果。支持多轮累积（每轮继承前一轮偏好）。

同步引入 `backend/services/session.py` 中的 `graph_config(session_id, graph)` helper，统一三个 graph 的 thread_id 命名规范：`{session_id}:jd` / `{session_id}:resume` / `{session_id}:feedback`，消除各 router 中的字符串拼接散落。

---

## 四、Session 状态推断

### 4.1 GET /api/sessions/{id} 真实状态推导（cr.20260531154607）

将 `GET /api/sessions/{session_id}` 从返回固定初始值改为从 checkpointer 读取三个 graph 快照，按优先级推导 `stage`，并返回真实的 `criteria`、`resumes`、`hr_memory`：
