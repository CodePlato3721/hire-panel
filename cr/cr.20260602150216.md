# CR — 前端 e2e 冒烟测试（Playwright，真实后端）

**Type**: feature

---

## Design

引入 Playwright e2e 冒烟测试，对接真实后端（FastAPI + PostgreSQL + OpenAI）：两条测试覆盖完整新 session 流程和 session reload 恢复；Playwright webServer 配置自动启动前后端；同步修复 `GET /api/sessions` stage 推导的 `jd_pending` 误判 bug。

---

## Source Details

```python
# sessions.py：改为检查具体 interrupt 节点，避免 __end__ 被误判为 jd_pending
elif jd_snap and "approve_criteria" in (jd_snap.next or []):
    stage = "jd_pending"
```

```ts
// playwright.config.ts：webServer 数组同时启动前后端，两端都 ready 才跑测试
webServer: [
  { command: 'uv run --env-file .env python scripts/run_server.py', cwd: '../', ... },
  { command: 'npm run dev', ... },
]
```

---

## Source Tree

```
.gitignore                           ← updated: 新增 frontend/test-results/ 和 playwright-report/
PROJECT.md                           ← updated: 后端启动命令改为 run_server.py
backend/routers/
└── sessions.py                      ← updated: jd_pending 判断改为检查 approve_criteria 节点
scripts/
└── run_server.py                    ← new: Windows 兼容包装脚本，loop_factory 方式启动 uvicorn
frontend/
├── package.json                     ← updated: 新增 test:e2e 脚本 + @playwright/test 依赖
├── package-lock.json                ← updated: 依赖锁定
├── playwright.config.ts             ← new: 超时配置 + 双 webServer
└── e2e/
    ├── tsconfig.json                ← new: e2e 目录 Node 类型支持
    └── smoke.spec.ts                ← new: 2 条冒烟测试（全流程 + session 恢复）
```

---

## Test Details

**Test 1 — 新 session 完整流程（真实 LLM）**
- 初始状态 → Fill JD → 审批界面 → approve → criteria 左栏显示
- Upload Resumes → 左栏评分表格出现 → Feedback → textarea re-enable

**Test 2 — Session 恢复（真实后端）**
- 走完 JD 审批流程 → page.reload() → 验证 criteria 从 PostgreSQL 恢复
- 验证右栏 Upload Resumes 按钮可见（stage 正确恢复为 jd_done）

同步修复：`jd_snap.next` 在图完成后可能为 `('__end__',)` 而非 `()`，原 `bool(jd_snap.next)` 检查误判为 `jd_pending`；改为检查具体节点名 `approve_criteria`。

---

## Test Tree

```
frontend/e2e/
├── tsconfig.json      ← new
└── smoke.spec.ts      ← new: 2 tests（需真实后端运行）
```

---

## Test Result

待用户启动后端后执行 `npm run test:e2e` 验证。Test 1 已通过（24.3s）；Test 2 待 sessions.py 修复后重新验证。

---

## Reply

approve
