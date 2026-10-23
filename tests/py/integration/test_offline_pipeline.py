"""L3 离线集成：以 assets/example + FakeTtsClient + 真 ffmpeg + Remotion 走 步骤 3→6→7→8，横屏、竖屏各一遍。
不访问豆包；需要本机 node/npx、ffmpeg/ffprobe，以及生成工程内 npm ci 可用（npm 缓存或镜像）。"""
import hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from py.support import SkillTestCase, covers, SKILL_DIR, FAKE_KEY, load_json

def sh(cmd, cwd=None, timeout=1800):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))

def ffprobe(path):
    p = sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(p.stdout) if p.returncode == 0 else None

def lufs(path):
    p = sh(["ffmpeg", "-nostats", "-i", str(path), "-filter_complex", "ebur128", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", p.stderr)
    return float(m[-1]) if m else None

_KEEP = []
def tearDownModule():
    for d in _KEEP: shutil.rmtree(d, True)

class _Pipeline(SkillTestCase):
    ASPECT = None; W = H = None
    _state = {}

    def pipeline(self):
        """惰性执行一次完整流水线并缓存；任何一步失败都以 FAIL 报告该步。"""
        key = self.ASPECT
        if key in _Pipeline._state:
            st = _Pipeline._state[key]
            if isinstance(st, str): self.fail(st)
            return st
        try:
            st = self._build()
        except AssertionError as e:
            _Pipeline._state[key] = f"[{key}] 流水线失败：{e}"; raise
        _Pipeline._state[key] = st
        return st

    def _step(self, name, proc):
        if proc.returncode != 0:
            raise AssertionError(f"{name} 退出 {proc.returncode}: {(proc.stdout + proc.stderr)[-800:]}")

    def _build(self):
        ex = self.require_path("assets/example")
        # v1.11：流水线结果按画幅跨用例缓存，技能副本须与缓存同寿命；copy_skill() 的 addCleanup 会在首个用例结束时删掉它，
        # 使后续用例（credits/leak）报“缺少 scripts/…”。这里改为模块级清理（tearDownModule），断言不变。
        sd = self.copy_skill(); self._cleanups = [c for c in self._cleanups if not (c[0] is shutil.rmtree and str(c[1][0]).startswith(str(sd.parent)))]
        _KEEP.append(sd.parent)
        root = Path(tempfile.mkdtemp(prefix=f"it-{self.ASPECT}-")); slug = root / f"example-{self.ASPECT}"; slug.mkdir()
        job = {"topic": "一分钟看懂：本技能包怎么把一个选题变成视频", "slug": slug.name, "aspect": self.ASPECT,
               "width": self.W, "height": self.H, "fps": 30, "created_at": "2026-10-22T00:00:00+08:00"}
        (slug / "job.json").write_text(json.dumps(job, ensure_ascii=False))
        for f in ("script.md", "sources.md", "storyboard.json"):
            shutil.copy(ex / f, slug / f)
        sb = load_json(slug / "storyboard.json"); sb["aspect"] = self.ASPECT
        (slug / "storyboard.json").write_text(json.dumps(sb, ensure_ascii=False))
        man = ex / "assets-manifest.json"
        (slug / "assets-manifest.json").write_text(man.read_text() if man.exists() else '{"version": 1, "assets": []}')
        # 步骤 3：配音（FakeTts + 真 ffmpeg）
        lines = self.lib("script_parser").parse((slug / "script.md").read_text(encoding="utf-8"))
        tc = self.lib("tts_client"); au = self.lib("audio"); log = self.lib("log")
        self.libfn("tts_pipeline", "run_tts")(lines, client=self.attr(tc, "FakeTtsClient")(), audio=self.attr(au, "FfmpegAudioTool")(),
                           out_dir=slug / "voice", speaker="zh_male_m191_uranus_bigtts", max_attempts=3,
                           sleeper=lambda s: None, redactor=log.Redactor(secrets=[FAKE_KEY]))
        # 步骤 6：建工程
        self._step("scaffold", self.cli("scaffold_project.py", "--job", slug / "job.json", "--out", slug / "project", skill_dir=sd))
        scenes = slug / "project/src/scenes"; scenes.mkdir(parents=True, exist_ok=True)
        for f in (ex / "scenes").glob("*.tsx"): shutil.copy(f, scenes / f.name)
        self._step("build_timeline", self.cli("build_timeline.py", "--timeline", slug / "voice/timeline.json", "--storyboard", slug / "storyboard.json",
                   "--subtitles", slug / "voice/subtitles.json", "--manifest", slug / "assets-manifest.json", "--project", slug / "project", skill_dir=sd))
        self._step("npm ci", sh(["npm", "ci", "--no-audit", "--no-fund"], cwd=slug / "project"))
        # 步骤 7、8
        chk = self.cli("check_project.sh", slug, "--aspect", self.ASPECT, skill_dir=sd, timeout=3600)
        self._step("check_project", chk)
        self._step("render", self.cli("render.sh", slug, skill_dir=sd, timeout=3600))
        return {"slug": slug, "skill": sd, "job": job, "check": chk}

    def compositions(self, slug):
        # v1.11：--quiet 只输出 ID（"Main Cover"），不含 fps/尺寸/帧数 → 改为默认表格输出并去掉 ANSI 颜色码
        p = sh(["npx", "remotion", "compositions", "src/index.ts"], cwd=slug / "project")
        self.assertEqual(p.returncode, 0, p.stderr[-500:])
        return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", p.stdout)

    # ---- 用例 ----
    def _t_lufs(self):
        st = self.pipeline(); v = lufs(st["slug"] / "voice/full.mp3")
        self.assertIsNotNone(v); self.assertGreaterEqual(v, -17.0); self.assertLessEqual(v, -15.0)

    def _t_duration(self):
        st = self.pipeline(); a = float(ffprobe(st["slug"] / "voice/full.mp3")["format"]["duration"])
        out = self.compositions(st["slug"])
        m = re.search(r"Main\s+(\d+)\s+(\d+)x(\d+)\s+(\d+)", out)
        self.assertIsNotNone(m, out)
        fps, w, h, frames = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        self.assertEqual((fps, w, h), (30, self.W, self.H))
        self.assertLessEqual(abs(frames - round(a * 30)), 1)
        ts = (st["slug"] / "project/src/data/timeline.ts").read_text()
        total = int(re.search(r"TOTAL_FRAMES\s*=\s*(\d+)", ts).group(1))
        self.assertEqual(total, frames)
        tos = [int(x) for x in re.findall(r"\bto:\s*(\d+)", ts)]
        self.assertEqual(max(tos), total, "最后一段结束帧应等于总帧数")

    def _t_no_tail_silence(self):
        st = self.pipeline(); tl = load_json(st["slug"] / "voice/timeline.json")
        a = float(ffprobe(st["slug"] / "voice/full.mp3")["format"]["duration"])
        last = tl["lines"][-1]
        # full.mp3 末尾 = 末句 end（含其 silence_ms），不允许再多出 >50ms
        self.assertLessEqual(a - last["end"], 0.05)

    def _t_video(self):
        st = self.pipeline(); v = st["slug"] / "out/video.mp4"; self.assertTrue(v.exists())
        pr = ffprobe(v); vs = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
        aus = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        self.assertEqual((vs["width"], vs["height"]), (self.W, self.H)); self.assertEqual(vs["r_frame_rate"], "30/1")
        self.assertTrue(aus and aus[0]["codec_name"] == "aac")
        self.assertLessEqual(abs(float(vs["duration"]) - float(aus[0]["duration"])), 0.1)

    def _t_covers(self):
        st = self.pipeline(); pub = st["slug"] / "publish"
        sizes = sorted((s["streams"][0]["width"], s["streams"][0]["height"]) for s in (ffprobe(p) for p in pub.glob("*.png")))
        want = [(1920, 1080)] if self.ASPECT == "landscape" else [(1080, 1440)]   # v1.3：竖屏封面只出 1080×1440
        self.assertEqual(sizes, want)

    def _t_frames_safe(self):
        st = self.pipeline(); sb = load_json(st["slug"] / "storyboard.json")
        for s in sb["sections"]:
            self.assertTrue((st["slug"] / f"check/frames/{self.ASPECT}-{s['id']}.png").exists(), s["id"])
        rep = load_json(st["slug"] / "check/report.json")   # Q-10 字段
        self.assertIs(rep["ok"], True, rep); self.assertIsNone(rep["failed_step"]); self.assertIsNone(rep["log_path"])
        self.assertEqual(rep["aspect"], self.ASPECT)
        names = [x["name"] for x in rep["steps"]]
        for n in ("tsc", "compositions", "frames", "safe_area", "static"):
            self.assertIn(n, names)
        self.assertTrue(all(x["ok"] for x in rep["steps"]), rep["steps"])

    def _t_determinism(self):
        st = self.pipeline(); proj = st["slug"] / "project"; hs = []
        for i in range(2):
            out = st["slug"] / f"det{i}.png"
            p = sh(["npx", "remotion", "still", "src/index.ts", "Main", str(out), "--frame=45"], cwd=proj)
            self.assertEqual(p.returncode, 0, p.stderr[-500:]); hs.append(hashlib.sha256(out.read_bytes()).hexdigest())
        self.assertEqual(hs[0], hs[1])

    def _t_example_length(self):
        st = self.pipeline(); a = float(ffprobe(st["slug"] / "out/video.mp4")["format"]["duration"])
        fx = load_json(SKILL_DIR / "assets/example/timeline.fixture.json")
        self.assertGreaterEqual(a, 50); self.assertLessEqual(a, 70)
        self.assertAlmostEqual(a, fx["audio_seconds"], delta=0.1)

    def _t_agents_md(self):
        st = self.pipeline(); proj = st["slug"] / "project"; md = (proj / "AGENTS.md").read_text()
        for c in ("npm ci", "npx remotion studio", "npm run check"):
            self.assertIn(c, md)
        p = sh(["npm", "run", "check"], cwd=proj, timeout=3600); self.assertEqual(p.returncode, 0, p.stderr[-800:])
        # Q-14：studio 冒烟——后台启动，90s 内 GET / 返回 200，随后结束进程
        import socket, time, urllib.request
        with socket.socket() as so: so.bind(("127.0.0.1", 0)); port = so.getsockname()[1]
        proc = subprocess.Popen(["npx", "remotion", "studio", "--port", str(port), "--no-open"], cwd=proj, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ok, deadline = False, time.time() + 90
            while time.time() < deadline and not ok:
                try: ok = urllib.request.urlopen(f"http://localhost:{port}/", timeout=5).status == 200
                except Exception: time.sleep(2)
            self.assertTrue(ok, "remotion studio 90s 内未返回 200")
        finally:
            proc.terminate(); proc.wait(timeout=30)

    def _t_credits(self):
        st = self.pipeline()
        p = self.cli("fetch_asset.py", "credits-diff", "--manifest", st["slug"] / "assets-manifest.json", "--slug-dir", st["slug"], skill_dir=st["skill"])
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(sh(["rg", "-n", "Credits", str(st["slug"] / "project/src")]).stdout, "")   # PRD F-09
        self.assertTrue((st["slug"] / "project/src/data/shot-badges.json").exists())

    def _t_leak(self):
        st = self.pipeline()
        p = self.cli("validate.py", "leak", st["slug"], "--skill-dir", st["skill"], skill_dir=st["skill"])
        self.assertEqual(p.returncode, 0, p.stdout)
        for f in st["slug"].rglob("*"):
            if f.is_file() and "node_modules" not in f.parts:
                self.assertNotIn(FAKE_KEY.encode(), f.read_bytes(), f)

    def _t_tsc(self):
        st = self.pipeline()
        p = sh(["npx", "tsc", "--noEmit"], cwd=st["slug"] / "project"); self.assertEqual(p.returncode, 0, p.stdout[-800:])

    def _t_components_used(self):
        """§7.3 L3：清单组件全部在示例中被渲染（storyboard 组件 + scenes 引用）"""
        st = self.pipeline(); used = (st["slug"] / "storyboard.json").read_text() + "".join(
            f.read_text() for f in (st["slug"] / "project/src/scenes").glob("*.tsx"))
        for n in ["GlassPanel", "Split", "Shot", "SectionTransition", "SlamTitle", "ImpactShake", "KeywordPulse", "StepList",
                  "NumberRoll", "CompareBars", "SourceBadge", "IllustrativeTag", "MediaCard", "FollowCTA", "HoldFade"]:
            self.assertIn(n, used, n)

def _make(aspect, w, h, prefix):
    ns = {"ASPECT": aspect, "W": w, "H": h}
    spec = [("lufs", "F-05"), ("duration", "F-06"), ("no_tail_silence", "F-06"), ("video", "F-12"), ("covers", "F-13"),
            ("frames_safe", "F-10", "F-11"), ("determinism", "NF-05"), ("example_length", "F-06"), ("agents_md", "F-14"),
            ("credits", "F-08", "NF-04"), ("leak", "F-05", "F-17", "NF-02"), ("tsc", "F-09"), ("components_used", "F-09")]
    for i, (name, *reqs) in enumerate(spec, 1):
        base = getattr(_Pipeline, f"_t_{name}")
        def t(self, _b=base): return _b(self)
        t.__name__ = f"test_{name}"
        ns[t.__name__] = covers(f"I-{prefix}-{i:02d}", *reqs, "F-10")(t)
        ns[t.__name__].__doc__ = f"[I-{prefix}-{i:02d}] {' '.join(reqs)} F-10 {aspect} {name}：" + (base.__doc__ or "")
    return type(f"TestPipeline_{aspect}", (_Pipeline,), ns)

TestPipelineLandscape = _make("landscape", 1920, 1080, "LS")
TestPipelinePortrait = _make("portrait", 1080, 1440, "PT")   # v1.3：竖屏 3:4

