# CR — feature

## Design

在"单次改动颗粒度"规范中补充"颗粒度不应过小"原则：纯配置改动可单独成 CR，但为业务逻辑服务的配置变更（如新增依赖）须与源码改动合并在同一 CR。

## Source Details

- `CLAUDE.md`：`## 单次改动颗粒度` 节新增第三条 bullet

## Source Tree

```
hire-panel/
└── CLAUDE.md    ← added "颗粒度不应过小" bullet
```

## Test Details

无。

## Test Tree

```
(无变更)
```
