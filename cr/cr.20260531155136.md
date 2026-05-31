**CR — feature**

**Design**
将 CR 归档目录从 `.cr/`（本地专用）改为 `cr/`（提交到 git），同时更新文件命名规范去掉前缀点号（`.cr.<ts>.md` → `cr.<ts>.md`）。

**Source Details**
```
cr 文件夹会提交到 git；`.cr.md` 已加入 `.gitignore`
重命名规范：`cr.<timestamp>.md`，timestamp 格式 `yyyyMMddHHmmss`
```

**Source Tree**
```
hire-panel/
├── CLAUDE.md          ← updated（reply 后的 CR 文件操作 一节）
└── .gitignore         ← updated（移除 .cr/）
```

**Test Details**
无变更

**Test Tree**
无变更

**Test Result**
无变更

**Reply**
approve
