**CR — feature（Task G）**

**Design**
在 `backend/main.py` 中加入 `CORSMiddleware`，允许 React dev server（`http://localhost:5173`）跨域访问所有 API 端点。

**Source Details**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Source Tree**
```
hire-panel/
└── backend/
    └── main.py    ← updated
```

**Test Details**
无变更

**Test Tree**
无变更

**Test Result**
无变更

**Reply**
approve
