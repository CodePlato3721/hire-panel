# CR — feature

## Design

移除 B1/B2 任务（graph_runner.py 过早抽象），graph 构建改为在各 router 内联，更新 TASKS.md 对齐。

## Source Details

- `TASKS.md`: 删除 Task B1、B2，Task C/D/E 描述补充"router 内直接调用 build_*_graph(get_checkpointer())"

## Source Tree

```
hire-panel/
└── TASKS.md    ← removed B1/B2, updated C/D/E descriptions
```

## Test Details

纯文档改动，无需验证。

## Test Tree

```
(无变更)
```

## Test Result

人工测试，不提供 Test Result，具体验证方式见 Test Details。
