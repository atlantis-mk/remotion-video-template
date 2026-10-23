"""CLI 公共：JSON 摘要最后一行输出（§4.0）、原子写文件。"""
import json, os, sys, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]


def summary(ok, code=0, outputs=None, errors=None, redactor=None):
    s = json.dumps({"ok": ok, "code": code, "outputs": outputs or {}, "errors": errors or []}, ensure_ascii=False, default=str)
    if redactor:
        s = redactor.redact(s)
    sys.stdout.write(s + "\n")
    sys.stdout.flush()
    return code


def atomic_write(path, data, mode="w"):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb" if "b" in mode else "w", **({} if "b" in mode else {"encoding": "utf-8"})) as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def write_json(path, obj):
    atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
