## feature

- **Design**：将 `tests/integration` 下的三个流水线冒烟测试迁移为 pytest e2e 测试，放入 `tests/e2e/`，并删除原 `tests/integration/` 目录。测试逻辑不变，改写为 module-scoped fixture 链式传递状态（JD → Resume → Feedback），每个阶段有明确断言。

- **Source Details**：
  ```python
  # tests/e2e/conftest.py — module-scoped fixtures 链式传递状态
  @pytest.fixture(scope="module")
  def criteria(): ...          # 运行 JD graph，返回 criteria
  def scored_resumes(criteria): ...  # 运行 resume graph，返回 resumes

  # tests/e2e/test_pipeline.py
  @pytest.mark.e2e
  def test_jd_extracts_criteria(criteria): assert 4 <= len(criteria) <= 6
  ```

- **Source Tree**：
  ```
  tests/
  ├── e2e/
  │   ├── conftest.py       ← new: criteria / scored_resumes fixtures
  │   ├── sample_data.py    ← new: SAMPLE_JD / SAMPLE_RESUME 常量
  │   └── test_pipeline.py  ← new: 3 个 @pytest.mark.e2e 测试
  └── integration/          ← deleted
  pyproject.toml            ← updated: 注册 e2e marker
  ```

- **Test Details**：端到端测试，运行方式：
  ```
  uv run pytest tests/e2e -m e2e -v
  ```
  需要 `OPENAI_API_KEY` 环境变量。三个测试断言：
  1. `test_jd_extracts_criteria`：criteria 数量在 4–6 之间，每项有 name
  2. `test_resume_scoring`：`total_score` 非空，`reason` 非空
  3. `test_feedback_rescoring`：重新评分后 `total_score` 非空，`hr_memory.scoring_preferences` 非空

- **Test Tree**：
  ```
  tests/
  └── e2e/
      └── test_pipeline.py    ← new
  ```

- **Test Result**：端到端测试，需要 OPENAI_API_KEY，不在本地自动执行。具体验证方式见 Test Details。

---

**Reply**：approve
