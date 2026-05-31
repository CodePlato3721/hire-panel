# CR — feature

## Design

在 `CLAUDE.md` Workflow Rules 中新增强制 CR 规则：任何源文件写入/编辑后，模型必须在
本轮结束前生成 `.cr.md` 并回显给用户，然后停止等待 approve/reject，不得提前宣布任务完成
或建议下一步。

## Source Details

- `CLAUDE.md` Workflow Rules: 新增 "CR is mandatory after every code change" 条目，
  列出三步强制流程（写 `.cr.md` → 回显 → 停止），并标注 "No exceptions"

## Source Tree

```
hire-panel/
└── CLAUDE.md    ← added mandatory CR enforcement rule
```

## Test Details

无测试用例。

## Test Tree

```
(无变更)
```
