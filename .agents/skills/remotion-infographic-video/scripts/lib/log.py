"""结构化日志与脱敏（架构 §6.5、§7.5：Redactor 在 lib/log.py）。"""
import sys
from typing import Iterable


class Redactor:
    """把 Key 原文替换为 ***。secrets 可为 str 或带 reveal() 的 Secret。"""

    def __init__(self, secrets: Iterable = ()):
        vals = set()
        for s in secrets or ():
            v = s.reveal() if hasattr(s, "reveal") else str(s)
            if v:
                vals.add(v)
        self.secrets = sorted(vals, key=len, reverse=True)

    def redact(self, text) -> str:
        t = str(text)
        for s in self.secrets:
            t = t.replace(s, "***")
        return t


class Logger:
    def __init__(self, redactor=None, path=None):
        self.r = redactor or Redactor()
        self.path = path

    def __call__(self, msg):
        m = self.r.redact(msg)
        print(m, file=sys.stderr)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(m + "\n")
