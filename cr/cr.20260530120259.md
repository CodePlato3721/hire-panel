# CR — feature

## Design

将"单次改动颗粒度"与"CR"合并到父节"单次改动规范"下，并新增"改动必须闭合"原则（按优先级要求单元测试/E2E测试/手动验证步骤/临时脚手架）。

## Source Details

- `CLAUDE.md`：`## 单次改动颗粒度` + `## CR` → 合并为 `## 单次改动规范`，下设 `### 颗粒度` 和 `### CR` 两个子节；颗粒度新增"改动必须闭合"第四条 bullet

## Source Tree

```
hire-panel/
└── CLAUDE.md    ← restructured + added closure rule
```

## Test Details

纯文档改动，无需验证。

## Test Tree

```
(无变更)
```
