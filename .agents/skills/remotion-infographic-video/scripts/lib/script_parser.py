"""script.md → 句列表（纯函数），以及数字归一化（F-04、NF-03）。"""
import re
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

DEFAULT_RATE, DEFAULT_PAUSE = 0, 300
SEC_RE = re.compile(r"^##\s+(S\d{2})\b\s*(.*)$")
LINE_RE = re.compile(r"^\s*[-*]\s*\[(\d{2,3})\]\s*(.*?)\s*(?:\{([^{}]*)\})?\s*$")


class ScriptParseError(ValueError):
    kind = "bad_script"
    line_id = None


class ScriptError(ScriptParseError):
    """带分类的稿件错误（v1.7）：kind="empty_line" 时 line_id 为空句 id。"""

    def __init__(self, message, kind="bad_script", line_id=None):
        super().__init__(message)
        self.kind, self.line_id = kind, line_id


def effective_chars(text: str) -> int:
    """有效字数：去掉空白与标点（Unicode P*/Z*/C* 类及常见符号）后的字符数。"""
    import unicodedata
    return sum(1 for ch in text if not ch.isspace() and unicodedata.category(ch)[0] not in "PZC")


def parse(text: str) -> List[dict]:
    lines, seen, section, title = [], set(), None, ""
    for n, raw in enumerate(text.splitlines(), 1):
        m = SEC_RE.match(raw.strip())
        if m:
            section, title = m.group(1), m.group(2).strip()
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        lid, body, meta = m.group(1), m.group(2).strip(), m.group(3)
        if section is None:
            raise ScriptParseError(f"第 {n} 行：句 [{lid}] 不在任何 ## Sxx 段下")
        if lid in seen:
            raise ScriptParseError(f"第 {n} 行：重复句 id [{lid}]")
        if not body or effective_chars(body) == 0:
            raise ScriptError(f"第 {n} 行：句 [{lid}] 去掉空白与标点后没有内容（空句）", kind="empty_line", line_id=lid)
        seen.add(lid)
        ctx, rate, pause = [], DEFAULT_RATE, DEFAULT_PAUSE
        if meta:
            for part in meta.split("|"):
                if ":" not in part and "：" not in part:
                    continue
                k, v = re.split(r"[:：]", part, maxsplit=1)
                k, v = k.strip().lower(), v.strip()
                try:
                    if k == "context":
                        ctx = [c.strip() for c in re.split(r"[;；]", v) if c.strip()]
                    elif k in ("rate", "speech_rate"):
                        rate = int(v)
                    elif k in ("pause", "silence_ms"):
                        pause = int(v)
                except ValueError:
                    raise ScriptParseError(f"第 {n} 行：{k} 取值非法：{v}")
        lines.append({"id": lid, "section": section, "section_title": title, "text": body,
                      "context": ctx, "speech_rate": rate, "silence_ms": pause})
    if not lines:
        raise ScriptParseError("稿件中没有任何句（格式：- [01] 文本 {context: … | rate: 0 | pause: 300}）")
    return lines


from .sources import normalize_number, extract_numbers  # noqa: E402,F401
