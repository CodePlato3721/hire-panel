## feature

- **Design**：完善 CR 工作流规范：新增 `remake` reply 类型，修正 `modify` 的 CR 更新行为，补充 reply 归档时的 Reply 段落要求，并将原 Test Result 规则重构为独立的「CR 的测试方式」章节，明确无测试 / 单元测试 / 端到端测试三种模式及对应目录约定。

- **Source Details**：
  ```
  + remake：基于 git diff HEAD 全量 diff 从头生成新 CR
  + modify：重新生成时在现有 CR 基础上补充修正，根本性变化走 reject 流程
  + approve/reject 归档前在 .cr.md 中追加 Reply 段落
  + 测试方式章节：无测试 / 单元测试(tests/unit) / 端到端测试(tests/e2d)
  ```

- **Source Tree**：
  ```
  CLAUDE.md    ← updated
  ```

- **Test Details**：无需验证，纯文档改动。

- **Test Tree**：
  ```
  (无变更)
  ```

- **Test Result**：人工测试，不提供 Test Result，具体验证方式见 Test Details

---

**Reply**：approve
