# CR — Task J: JD 流程前端

**Type**: feature

---

## Design

实现完整 JD 流程前端：右栏 "Fill JD" 按钮 → 文本输入 → `POST /jd` SSE 流 → interrupt 时展示 criteria 审批界面 → `POST /jd/reply` → 左栏显示已确认的 criteria 列表；同步修复 CORS 端口遗漏（5174）并将 `Stage` 字符串字面量枚举化。

---

## Source Details

`JdFlow` 以 `JdUiState` const 对象驱动五状态视图切换（`Idle → Input → Streaming → Approving → Done`）；`Stage` 同样改为 `as const` 对象，消除散落字面量。

```ts
// api.ts
export const Stage = { Idle: 'idle', JdPending: 'jd_pending', ... } as const
export type Stage = typeof Stage[keyof typeof Stage]
```

---

## Source Tree

```
backend/
└── main.py                          ← updated: allow_origins 补充 localhost:5174
frontend/src/
├── api.ts                           ← updated: Stage 改为 const 对象 + type
├── App.tsx                          ← updated: 新增 stage/criteria state，挂载 CriteriaList + JdFlow
├── App.css                          ← updated: 新增 JD 流程与 criteria 列表全部样式
└── components/
    ├── CriteriaList.tsx             ← new: 左栏 criteria 卡片列表
    └── JdFlow.tsx                   ← new: 右栏 JD 流程五状态机
```

---

## Test Details

手动验证步骤：

1. 启动后端：`uv run --env-file .env uvicorn backend.main:app --reload`
2. 启动前端：`cd frontend; npm run dev`
3. 打开页面，右栏显示 "Fill JD" 按钮，左栏显示占位文字
4. 点击按钮，输入 JD 文本，点击 "Analyze"，右栏出现 SSE token 流
5. 流结束后出现 "Review Criteria" 审批界面，展示提取的 criteria 列表
6. 输入 `approve`，点击 "Submit"，右栏切换为 "JD criteria confirmed"
7. 左栏显示已确认的 criteria 卡片列表
8. 刷新页面，左栏 criteria 从 session 状态恢复，右栏显示 "done" 状态

已人工验证步骤 1–7（用户截图确认审批界面正常，criteria 正确显示）。

---

## Test Tree

```
（无自动化测试变更）
```

---

## Test Result

步骤 1–7 人工验证通过（见用户截图）。步骤 8（刷新恢复）待验证。

---

## Reply

approve
