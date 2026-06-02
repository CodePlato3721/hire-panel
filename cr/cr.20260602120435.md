# CR — Task K: Resume 上传流程

**Type**: feature

---

## Design

实现 Resume 上传流程：JD 完成后右栏切换为 "Upload Resumes" 按钮 → 文件选择（PDF/txt）→ `POST /resumes` SSE 流 → 左栏表格显示各简历评分；同步扩展 `useSession` 增加 `resumes` 状态。

---

## Source Details

```ts
// App.tsx：根据 jdDone 标志切换右栏内容
const jdDone = stage === Stage.JdDone || stage === Stage.ResumeDone || stage === Stage.FeedbackDone
```

---

## Source Tree

```
frontend/src/
├── App.tsx                              ← updated: 引入 ResumeUpload / ResumeTable，右栏条件渲染
├── App.css                              ← updated: 新增 resume upload 与 resume table 样式
├── hooks/
│   ├── useSession.ts                    ← updated: 新增 resumes state + handleResumesDone
│   ├── useSession.test.ts               ← updated: 新增 handleResumesDone 测试
│   ├── useResumeUpload.ts               ← new: resume 上传状态机（Idle/Streaming/Done）
│   └── useResumeUpload.test.ts          ← new: 6 个单元测试
└── components/
    ├── ResumeUpload.tsx                 ← new: 右栏上传组件
    └── ResumeTable.tsx                  ← new: 左栏评分表格
```

---

## Test Details

`useResumeUpload`（6 tests）：
- 初始状态推导（jd_done→Idle，resume_done/feedback_done→Done）
- 空文件列表不触发状态变化
- token 累积到 streamText
- done 事件 → 转为 Done 状态
- 网络错误 → 回退到 Idle

`useSession` 新增（1 test）：
- `handleResumesDone` 更新 resumes，stage → ResumeDone

---

## Test Tree

```
frontend/src/hooks/
├── useResumeUpload.test.ts    ← new: 6 tests
└── useSession.test.ts         ← updated: +1 test
```

---

## Test Result

25 passed / 0 failed（`npm test`，Duration 2.14s）

---

## Reply

approve
