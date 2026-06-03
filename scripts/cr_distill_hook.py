#!/usr/bin/env python3
"""
PostToolUse hook on Bash/PowerShell.
Triggers when a CR is archived: detects Move-Item / mv commands that
write to cr/cr.<14-digit-timestamp>.md.

stdout  → injected into Claude's context (kept minimal to avoid context bloat)
stderr  → shown to user as notification

At count=10: spawns a fresh `claude -p` subprocess to distill CRs in an
isolated context, so the running conversation's token count is not affected.
"""
import sys
import json
import re
import subprocess
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


def distill_in_subprocess(file_list: list[Path]) -> None:
    file_refs = "\n".join(f"  - cr/{f.name}" for f in file_list)
    prompt = (
        "你是一个代码审查摘要助手。请完成以下任务：\n"
        f"1. 读取以下最近 10 个 CR 文件：\n{file_refs}\n"
        "2. 将这 10 个 CR 的核心内容总结后，以新段落形式追加到 CR.md（**应用** 段落）\n"
        "3. 若新内容与旧摘要矛盾，以新内容为准，替换旧内容\n"
        "4. 完成后输出：「CR 摘要已写入 CR.md」"
    )
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode == 0:
        print("[CR Hook] 摘要子进程完成，CR.md 已更新。", file=sys.stderr, flush=True)
    else:
        print(
            f"[CR Hook] 摘要子进程失败 (exit {result.returncode}):\n{result.stderr[:500]}",
            file=sys.stderr,
            flush=True,
        )


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
        print("[CR Hook] 计数达到 10，已重置为 0，正在后台蒸馏...", file=sys.stderr, flush=True)
        # Run distillation in a separate claude process to avoid injecting
        # 10 CR files worth of content into the current (already large) context.
        distill_in_subprocess(last_10)
        # Notify the running conversation with a single short line instead of
        # injecting the full task — prevents 1M context limit from being hit.
        print("[CR Hook] CR 摘要已在独立进程中完成并写入 CR.md，无需当前会话处理。", flush=True)
    else:
        COUNT_FILE.write_text(str(count))


if __name__ == "__main__":
    main()
