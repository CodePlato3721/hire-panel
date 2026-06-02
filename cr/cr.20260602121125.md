# CR — Task L: Feedback/Chat 流程

**Type**: feature

---

## Design

实现 Feedback/Chat 流程：简历评分完成后右栏切换为聊天输入框 → 提交反馈 → `POST /feedback` SSE 流 → 左栏表格实时更新简历评分；支持多轮累积反馈。

---

## Source Details

```ts
// useFeedback：每轮提交前清空 feedbackText，完成后重置 isLoading，左栏表格由 onFeedbackDone 驱动更新
const text = feedbackText
setFeedbackText('')
enterStreaming()
await submitFeedback(sessionId, text, onEvent)
```

---

## Source Tree

```
frontend/src/
├── App.tsx                           ← updated: 新增 FeedbackChat，右栏三段式条件渲染
├── App.css                           ← updated: 新增 feedback-chat 样式
├── hooks/
│   ├── useSession.ts                 ← updated: 新增 handleFeedbackDone
│   ├── useSession.test.ts            ← updated: 新增 handleFeedbackDone 测试
│   ├── useFeedback.ts                ← new: 反馈流状态管理
│   └── useFeedback.test.ts           ← new: 4 个单元测试
└── components/
    └── FeedbackChat.tsx              ← new: 右栏反馈输入组件
```

---

## Test Details

`useFeedback`（4 tests）：
- 空输入不触发状态变化
- 提交后 feedbackText 清空
- token 累积到 streamText
- isLoading 提交后恢复 false

`useSession` 新增（1 test）：
- `handleFeedbackDone` 更新 resumes，stage → FeedbackDone

---

## Test Tree

```
frontend/src/hooks/
├── useFeedback.test.ts    ← new: 4 tests
└── useSession.test.ts     ← updated: +1 test
```

---

## Test Result

30 passed / 0 failed（`npm test`，Duration 2.27s）

---

## Reply

approve
