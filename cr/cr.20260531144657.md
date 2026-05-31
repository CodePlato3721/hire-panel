## feature

- **Design**：新增 Feedback 端点（Task E）：POST `/api/sessions/{session_id}/feedback` 接收 HR 反馈，继承上一轮 resumes 和 hr_memory，运行 feedback graph 重新评分，SSE 流返回结果。同步引入 `graph_config()` helper，统一三个 graph 的 thread_id 命名规范（`session_id:jd` / `session_id:resume` / `session_id:feedback`），消除各 router 中的字符串拼接散落。

- **Source Details**：
  ```python
  # backend/services/session.py
  def graph_config(session_id: str, graph: str) -> dict:
      return {"configurable": {"thread_id": f"{session_id}:{graph}"}}

  # backend/routers/feedback.py — 多轮累积：有上一轮状态则继承，否则从 resume 图读取
  prev = await graph.aget_state(feedback_config)
  resumes = prev.values.get("resumes", []) if prev and prev.values else resume_state.values.get("resumes", [])
  ```

- **Source Tree**：
  ```
  backend/
  ├── main.py                ← added include_router(feedback.router)
  ├── services/
  │   └── session.py         ← new: graph_config() helper
  ├── routers/
  │   ├── feedback.py        ← new: POST /{session_id}/feedback
  │   ├── jd.py              ← updated: graph_config(session_id, "jd")
  │   └── resume.py          ← updated: graph_config(session_id, "jd"/"resume")
  └── schemas/
      └── feedback.py        ← new: FeedbackRequest
  ```

- **Test Details**：人工验证步骤（需要 `OPENAI_API_KEY` + neon.tech 连接）：

  **1. 启动服务**
  ```
  uv run --env-file .env uvicorn backend.main:app --reload
  ```

  **2. 先跑完 JD + 简历流程（取得 session_id）**

  **3. 提交首轮反馈（预期：token 流 + done 事件含重新评分的 resumes 和 hr_memory）**
  ```
  curl -N -X POST http://localhost:8000/api/sessions/<session_id>/feedback \
    -H "Content-Type: application/json" \
    -d "{\"feedback\": \"LangChain experience should be weighted more heavily.\"}"
  ```

  **4. 提交第二轮反馈（验证多轮累积）**
  ```
  curl -N -X POST http://localhost:8000/api/sessions/<session_id>/feedback \
    -H "Content-Type: application/json" \
    -d "{\"feedback\": \"Also prioritize cloud experience.\"}"
  ```
  预期：done 事件中 `hr_memory.scoring_preferences` 包含两轮偏好的累积

- **Test Tree**：
  ```
  (无变更)
  ```

- **Test Result**：人工测试，不提供 Test Result，具体验证方式见 Test Details
