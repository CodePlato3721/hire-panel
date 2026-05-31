# CR — feature

## Design

在 CR reply 规范中新增 ask 类型：用户可通过多轮提问理解改动细节，不触发任何代码变更，问完后再做 approve/reject 决定。

## Source Details

- `CLAUDE.md`：`#### CR 的 reply` 节新增 `ask` 条目，并将 `modify` 说明中"询问细节"部分移入 `ask` 定义

## Source Tree

```
hire-panel/
└── CLAUDE.md    ← added ask reply type
```

## Test Details

纯文档改动，无需验证。

## Test Tree

```
(无变更)
```

## Test Result

人工测试，不提供 Test Result，具体验证方式见 Test Details。
