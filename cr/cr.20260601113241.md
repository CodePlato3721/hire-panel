**Type**: feature

**Design**: 创建 `frontend/` Vite + React + TypeScript 项目骨架，并在 `src/api.ts` 封装全部 5 个后端端点的 HTTP + SSE 调用。

**Source Details**:
```ts
// src/api.ts — SSE 流读取核心
async function streamSSE(response: Response, onEvent: (event: SSEEvent) => void): Promise<void> {
  const reader = response.body!.getReader()
  ...
}
```

**Source Tree**:
```
frontend/
├── src/
│   ├── api.ts          ← new（全部 API 封装）
│   ├── App.tsx         ← new（占位骨架）
│   ├── main.tsx        ← new
│   ├── App.css         ← new
│   └── index.css       ← new
├── index.html          ← new
├── package.json        ← new
├── vite.config.ts      ← new
├── tsconfig.json       ← new
├── tsconfig.app.json   ← new
└── tsconfig.node.json  ← new
```

**Test Details**: 无变更

**Test Tree**: 无变更

**Test Result**: 无变更

---

**Reply**: approve
