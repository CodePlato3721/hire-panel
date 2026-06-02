#!/usr/bin/env python3
"""
PostToolUse hook on Write: triggered when a CR archive file cr/cr.<timestamp>.md is written.
stderr -> user notification; stdout -> injected to Claude as context.
"""
import sys
import json
import re
from pathlib import Path

CR_DIR = Path("cr")
COUNT_FILE = CR_DIR / ".cr.count"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") != "Write":
        sys.exit(0)

    fp = data.get("tool_input", {}).get("file_path", "")
    if not re.search(r"[/\\]cr[/\\]cr\.\d{14}\.md$", fp):
        sys.exit(0)

    CR_DIR.mkdir(exist_ok=True)

    try:
        count = int(COUNT_FILE.read_text().strip()) if COUNT_FILE.exists() else 0
    except Exception:
        count = 0

    count += 1
    print(f"[CR Hook] CR 已归档，当前计数: {count}/10", file=sys.stderr, flush=True)

    if count >= 10:
        COUNT_FILE.write_text("0")
        cr_files = sorted(CR_DIR.glob("cr.*.md"))
        last_10 = cr_files[-10:]
        file_list = "\n".join(f"  - cr/{f.name}" for f in last_10)
        print("[CR Hook] 计数达到 10，已重置为 0，触发汇总任务。", file=sys.stderr, flush=True)
        print(
            "[系统提示] CR 归档计数已达 10 个。请在执行 git commit 之前完成以下操作：\n"
            f"1. 读取以下最近 10 个 CR 文件：\n{file_list}\n"
            "2. 将这 10 个 CR 的核心内容总结后，以新段落形式追加到 CR.md\n"
            "3. 在 CR.md 的 **引用** 段落追加上述 10 个文件名\n"
            "4. 完成后再继续执行 git commit",
            flush=True,
        )
    else:
        COUNT_FILE.write_text(str(count))


if __name__ == "__main__":
    main()
