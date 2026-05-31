# CR — feature

## Design

两项配套改动：
1. `CLAUDE.md` 新增 CR (commit request) 工作流规范，定义 feature / defect 两种 CR 格式、
   approve / reject 的执行行为，以及 CR 文件的本地归档规则。
2. `.gitignore` 新增 `.cr.md` 和 `.cr/` 排除项，确保 CR 文件不被提交。

## Source Details

- `CLAUDE.md`: 新增 `## CR(commit request)` 一节，包含 reply 规则、文件操作规则、feature/defect 格式定义
- `.gitignore`: 在 `# UV` 块下方新增两行 `.cr.md` / `.cr/`

## Source Tree

```
hire-panel/
├── CLAUDE.md      ← added CR workflow spec
└── .gitignore     ← added .cr.md and .cr/ exclusions
```

## Test Details

无测试用例。

## Test Tree

```
(无变更)
```
