#!/usr/bin/env python3
"""
PostToolUse hook on Bash/PowerShell.
Triggers when a CR is archived: detects Move-Item / mv commands that
write to cr/cr.<14-digit-timestamp>.md.

stdout  → injected into Claude's context (distillation instruction at count=10)
stderr  → shown to user as notification
"""
import sys
import json
import re
from pathlib import Path

CR_DIR = Path("cr")
COUNT_FILE = CR_DIR / "raw_count"


def is_cr_archive_command(command: str) -> bool:
    return bool(re.search(r"cr[/\\]cr\.\d{14}\.md", command))


def read_count() -> int:
    try:
        return int(COUNT_FILE.read_text().strip()) if COUNT_FILE.exists() else 0
    except Exception:
        return 0


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not is_cr_archive_command(command):
        sys.exit(0)

    CR_DIR.mkdir(exist_ok=True)

    count = read_count() + 1
    print(f"[CR Hook] CR 已归档，当前计数: {count}/10", file=sys.stderr, flush=True)

    if count >= 10:
        COUNT_FILE.write_text("0")
        last_10 = sorted(CR_DIR.glob("cr.*.md"))[-10:]
        file_list = "\n".join(f"  - cr/{f.name}" for f in last_10)
        print("[CR Hook] 计数达到 10，已重置为 0，触发汇总任务。", file=sys.stderr, flush=True)
        print(
            "[系统提示] CR 归档计数已达 10 个。请在执行 git commit 之前完成以下操作：\n"
            f"1. 读取以下最近 10 个 CR 文件：\n{file_list}\n"
            "2. 将这 10 个 CR 的核心内容总结后，以新段落形式追加到 CR.md（**应用** 段落）\n"
            "3. 若新内容与旧摘要矛盾，以新内容为准，替换旧内容\n"
            "4. 将 cr/raw_count 重置确认后再继续执行 git commit",
            flush=True,
        )
    else:
        COUNT_FILE.write_text(str(count))


if __name__ == "__main__":
    main()
