"""check_project.sh / render.sh 的共用工具：调用 npx、解析 compositions、切换画幅。"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

LIB = Path(__file__).resolve().parent
sys.path.insert(0, str(LIB.parent))
from lib.render_ts import render_job_ts  # noqa: E402
from lib.job import normalize_job  # noqa: E402

SIZES = {"landscape": None, "portrait": None}


def run(cmd, cwd, log_path, timeout=3600):
    t0 = time.time()
    p = subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"$ {' '.join(map(str, cmd))}\n{p.stdout}\n{p.stderr}\n[exit {p.returncode}]\n")
    return p, int((time.time() - t0) * 1000)


def npx():
    return shutil.which("npx") or "npx"


def parse_compositions(out):
    """remotion compositions 输出：`Main  30  1920x1080  1726 (57.53 sec)`。"""
    res = {}
    for m in re.finditer(r"^\s*(\S+)\s+(\d+)\s+(\d+)x(\d+)\s+(\d+)", out, re.M):
        res[m.group(1)] = {"fps": int(m.group(2)), "width": int(m.group(3)), "height": int(m.group(4)), "frames": int(m.group(5))}
    return res


def cover_presets(project):
    p = Path(project) / "src/layout/presets.ts"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    out = {}
    m = re.search(r"COVER_PRESETS\s*=\s*\{(.*?)\}\s*as const", t, re.S)
    if m:
        for a in ("landscape", "portrait"):
            mm = re.search(a + r"\s*:\s*\[(.*?)\]\s*(?:,|$)", m.group(1) + ",", re.S)
            if mm:
                out[a] = [(int(w.replace("_", "")), int(h.replace("_", ""))) for w, h in re.findall(r"\[\s*([\d_]+)\s*,\s*([\d_]+)\s*\]", mm.group(1))]
    return out or {"landscape": [(1920, 1080)], "portrait": [(1080, 1440)]}


class AspectSwitch:
    """临时改写 src/data/job.ts 以切换画幅（--aspect both 用），退出时恢复。"""

    def __init__(self, project, job, aspect):
        self.p = Path(project) / "src/data/job.ts"
        self.job, self.aspect = job, aspect
        self.orig = None

    def __enter__(self):
        if self.job.get("aspect") != self.aspect:
            self.orig = self.p.read_text(encoding="utf-8") if self.p.exists() else None
            self.p.write_text(render_job_ts(normalize_job({**self.job, "aspect": self.aspect, "width": None, "height": None})), encoding="utf-8")
        return self

    def __exit__(self, *a):
        if self.orig is not None:
            self.p.write_text(self.orig, encoding="utf-8")


def probe_duration(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return float(json.loads(p.stdout)["format"]["duration"])
    except Exception:
        return None
