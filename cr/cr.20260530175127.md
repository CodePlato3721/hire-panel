# CR — feature

## Design

新增 Resume 端点：POST /resumes 上传简历文件，从 JD 图状态读取 criteria，运行 resume graph，SSE 流返回评分结果。

## Source Details

- `backend/routers/resume.py`: `_parse_file()` 处理 PDF/文本文件；端点从 JD graph checkpoint 读取 `scoring_criteria`，传入 `build_resume_graph`；`_stream_resume(events, graph, config)` 与 jd.py 结构一致
- `backend/main.py`: 新增 `app.include_router(resume.router)`

## Source Tree

```
hire-panel/backend/
├── main.py          ← added include_router(resume.router)
└── routers/
    └── resume.py    ← new
```

## Test Details

人工测试步骤（需要 `OPENAI_API_KEY`、neon.tech 连接、先完成 JD 审批）：

**1. 启动服务**
```
uv run --env-file .env uvicorn backend.main:app --reload
```

**2. 先跑完 JD 流程**（取得 session_id 并完成 criteria 审批，参考 Task C 测试步骤）

**3. 上传简历（预期：token 流 + done 事件含评分后的 resumes 列表）**
```
curl -N -X POST http://localhost:8000/api/sessions/<session_id>/resumes \
  -F "files=@/path/to/resume.pdf"
```
预期 done 事件：`{"type":"done","resumes":[{"filename":"...","total_score":...,"reason":"..."}]}`

## Test Tree

```
(无变更)
```

## Test Result

人工测试，不提供 Test Result，具体验证方式见 Test Details。
