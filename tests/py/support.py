"""测试公共支撑：定位技能包、按需导入被测模块、调用 CLI。
被测对象缺失时一律以 self.fail()（FAIL，红灯）报告，而不是 ImportError（ERROR）。"""
import importlib, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = TESTS_DIR.parent
DEFAULT_SKILL_REL = Path(".agents/skills/remotion-infographic-video")  # v1.11 A-21；相对仓库根 / 相对 tests/ 为 ../.agents/skills/...
SKILL_DIR = Path(os.environ.get("SKILL_DIR", REPO_DIR / DEFAULT_SKILL_REL)).resolve()
SCRIPTS = SKILL_DIR / "scripts"
FIXTURES = TESTS_DIR / "fixtures"
FAKE_KEY = "FAKEKEY-tdd-9f8e7d6c5b4a-DO-NOT-LEAK"
REQ_IDS = [f"F-{i:02d}" for i in range(1, 18)] + [f"NF-{i:02d}" for i in range(1, 9)]

def covers(case_id, *reqs):
    """标注用例 ID 与覆盖的需求编号（tools/trace.py 静态扫描此装饰器生成追溯矩阵）。"""
    def deco(fn):
        fn.case_id, fn.covers = case_id, reqs
        fn.__doc__ = f"[{case_id}] {' '.join(reqs)} " + (fn.__doc__ or "")
        return fn
    return deco

class SkillTestCase(unittest.TestCase):
    maxDiff = None

    def require_path(self, rel):
        p = SKILL_DIR / rel
        if not p.exists():
            self.fail(f"未实现：缺少 {p}")
        return p

    def lib(self, name):
        self.require_path("scripts/lib")
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        try:
            return importlib.import_module(f"lib.{name}")
        except ImportError as e:
            self.fail(f"未实现：无法导入 scripts/lib/{name}.py（{e}）")

    def attr(self, mod, name):
        if not hasattr(mod, name):
            self.fail(f"未实现：{mod.__name__}.{name}")
        return getattr(mod, name)

    def cli(self, script, *args, cwd=None, skill_dir=None, env=None, timeout=600):
        sd = Path(skill_dir) if skill_dir else SKILL_DIR
        path = sd / "scripts" / script
        if not path.exists():
            self.fail(f"未实现：缺少 {path}")
        cmd = (["bash", str(path)] if script.endswith(".sh") else [sys.executable, str(path)]) + [str(a) for a in args]
        e = {k: v for k, v in os.environ.items() if k != "DOUBAO_TTS_API_KEY"}
        e.update(env or {})
        return subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout)

    def summary(self, proc):
        """§4.0：stdout 最后一行为 JSON 摘要。"""
        lines = [l for l in proc.stdout.strip().splitlines() if l.strip()]
        self.assertTrue(lines, f"stdout 为空；stderr={proc.stderr[-500:]}")
        try:
            return json.loads(lines[-1])
        except json.JSONDecodeError:
            self.fail(f"stdout 最后一行不是 JSON：{lines[-1][:200]}")

    def copy_skill(self, key=FAKE_KEY, with_env=True):
        """把技能包复制到临时目录（L4 复制即用），可写入假 Key。"""
        self.require_path("SKILL.md")
        tmp = Path(tempfile.mkdtemp(prefix="skill-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        dst = tmp / SKILL_DIR.name
        shutil.copytree(SKILL_DIR, dst, ignore=shutil.ignore_patterns(".env", "node_modules", ".git"))
        if with_env:
            (dst / ".env").write_text(f"DOUBAO_TTS_API_KEY={key}\n" if key is not None else "", encoding="utf-8")
        return dst

    def tmpdir(self):
        d = Path(tempfile.mkdtemp(prefix="tdd-"))
        self.addCleanup(shutil.rmtree, d, True)
        return d

def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def which_or_fail(tc, name):
    if not shutil.which(name):
        tc.fail(f"环境缺少命令 {name}")

def _find_fn(tc, name):
    """架构只给了函数名、未固定所在模块：在 scripts/lib/*.py 与 scripts/*.py 中查找。"""
    tc.require_path("scripts")
    import importlib.util
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    cands = sorted((SCRIPTS / "lib").glob("*.py")) + sorted(SCRIPTS.glob("*.py"))
    for p in cands:
        modname = ("lib." if p.parent.name == "lib" else "") + p.stem
        try:
            m = importlib.import_module(modname)
        except Exception:
            continue
        if hasattr(m, name):
            return getattr(m, name)
    tc.fail(f"未实现：scripts/ 下找不到函数 {name}")

SkillTestCase.fn = _find_fn

def _libfn(tc, module, name):
    """按架构 v1.2 §7.5 固定的模块路径取函数/类。"""
    return tc.attr(tc.lib(module), name)

SkillTestCase.libfn = _libfn

# 被测实现内部抛出的非断言异常（如签名不符导致 TypeError）记为 FAIL 并注明“实现异常”；
# 测试代码自身的异常仍保留为 ERROR，便于区分“实现不合规”与“测试写错”。
import functools, re, traceback as _tb

def _wrap_impl_errors(fn):
    @functools.wraps(fn)
    def inner(self, *a, **k):
        try:
            return fn(self, *a, **k)
        except (AssertionError, unittest.SkipTest):
            raise
        except Exception as e:
            frames = _tb.extract_tb(e.__traceback__)
            if frames and any(str(SKILL_DIR) in f.filename for f in frames):
                self.fail(f"实现异常（不符合架构接口）：{type(e).__name__}: {e}\n" + "".join(_tb.format_list(frames[-3:])))
            if isinstance(e, TypeError) and re.search(r"positional argument|keyword argument|required .*argument", str(e)):
                self.fail(f"实现签名与架构 §7.5 不符：{e}")
            if isinstance(e, FileNotFoundError) and str(getattr(e, "filename", "")).startswith(tempfile.gettempdir()):
                self.fail(f"实现未产出预期文件：{e.filename}")
            raise
    return inner

def _init_subclass(cls, **kw):
    for name, val in list(vars(cls).items()):
        if name.startswith("test") and callable(val):
            w = _wrap_impl_errors(val)
            for attr in ("case_id", "covers"):
                if hasattr(val, attr): setattr(w, attr, getattr(val, attr))
            setattr(cls, name, w)

SkillTestCase.__init_subclass__ = classmethod(_init_subclass)
