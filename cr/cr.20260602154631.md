# CR — 删除 main.py，pipeline 移入 backend/

**Type**: feature

---

## Design

移除命令行入口 `main.py`，将 `pipeline/` 整体移入 `backend/pipeline/`，全量替换所有 `from pipeline.*` 和 `patch("pipeline.*")` 引用。

---

## Source Details

```bash
git rm main.py
git mv pipeline backend/pipeline
# 全量替换：from pipeline → from backend.pipeline
# patch 字符串：'pipeline.' → 'backend.pipeline.'
```

---

## Source Tree

```
（deleted）main.py
backend/
└── pipeline/                        ← moved from pipeline/ (git mv, history preserved)
backend/services/
├── jd.py                            ← updated: import path
├── resume.py                        ← updated: import path
├── feedback.py                      ← updated: import path
└── snapshot.py                      ← updated: import path
tests/
├── unit/
│   ├── test_extract_jd.py           ← updated: import + patch 路径
│   └── test_approve_criteria.py     ← updated: import + patch 路径
├── e2e/
│   ├── conftest.py                  ← updated: import 路径
│   └── test_pipeline.py             ← updated: import 路径
ui/
└── state.py                         ← updated: import 路径
```

---

## Test Details

27 个单元测试全部通过，无行为变更。

---

## Test Tree

```
tests/unit/
├── test_extract_jd.py        ← updated: 6 tests
├── test_approve_criteria.py  ← updated: 16 tests
└── test_get_session.py       ← unchanged: 5 tests
```

---

## Test Result

27 passed / 0 failed（`uv run pytest tests/unit/ -v`，Duration 1.37s）

---

## Reply

approve
