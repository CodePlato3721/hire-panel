# CR — Score display: show score / maxScore

**Type**: feature

---

## Design

在 `ResumeTable` 中将分数显示从 `50` 改为 `50 / 50`（score / maxScore），maxScore 由调用方传入（`criteria.length * 10`）。

## Source Details

```tsx
// ResumeTable.tsx
`${r.total_score} / ${maxScore}`

// App.tsx
maxScore={criteria.length * 10}
```

## Source Tree

```
frontend/src/
├── App.tsx                       ← updated
└── components/
    └── ResumeTable.tsx           ← updated
```

## Test Details

无自动化测试。手动验证：`npm run dev` 启动前端，上传 JD + resume 后，Score 列应显示 `50 / 50` 格式。

## Test Tree

```
（无变更）
```

## Test Result

待用户手动验证。

## Reply

approve
