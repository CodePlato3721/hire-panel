# CR — Fix stale Postgres connections on Neon

**Type**: defect

---

## Root Cause

Neon serverless PostgreSQL 会在连接空闲 ~5 分钟后主动断开（`AdminShutdown`）。`AsyncConnectionPool` 默认 `min_size=4`，会维持常驻连接；浏览器关闭无流量期间这些连接被 Neon 杀掉，重新打开浏览器时池子拿到死连接直接崩。

## Solution

`min_size=0` 使池不维持常驻连接；`max_idle=60` 使空闲连接 60 秒内自动关闭，早于 Neon 的超时阈值，重新请求时始终建立新连接。

## Source Details

```python
AsyncConnectionPool(conninfo=url, min_size=0, max_size=10, max_idle=60, open=False)
```

## Source Tree

```
backend/
└── services/
    └── db.py    ← updated
```

## Test Details

无自动化测试。手动验证步骤：
1. 启动后端，完整走一遍 JD + resume 流程
2. 关闭浏览器，等待 5 分钟以上
3. 重新打开浏览器，再次提交 JD
4. 后端不应再报 `psycopg.errors.AdminShutdown`

## Test Tree

```
（无变更）
```

## Test Result

待用户手动验证。

## Reply

approve
