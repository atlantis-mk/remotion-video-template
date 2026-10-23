"""L3 离线集成补充：自检失败报告与调用上限（F-11）、图层白名单检查（F-08）、同工程横竖切换（F-10）、
改 tokens 后画面配色像素级变化（NF-06）、默认画幅（F-10）。基于 assets/example + timeline.fixture.json，不调用豆包。"""
import hashlib, json, re, shutil, subprocess
from pathlib import Path
from py.support import SkillTestCase, covers, SKILL_DIR, load_json

def sh(cmd, cwd=None, timeout=1800):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)

def mean_rgb(png):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(png), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    b = p.stdout; n = len(b) // 3
    return tuple(sum(b[i::3]) / n for i in range(3))

def silent_mp3(tc, path, seconds):
    """v1.11：同长静音 mp3。MP3 按帧（48 kHz 下 1152 样本 = 24 ms）编码并补齐，anullsrc -t 直接给时长会多出 ≤2 帧
    （24 kHz 实测 57.600 vs 57.548）。改为 48 kHz，生成后用 ffprobe 实测，按 24 ms 步长裁短 -t，直到实测与 audio_seconds 差 ≤12 ms
    （半个 MP3 帧，远小于 1 视频帧 33 ms）；做不到则测试数据本身判 FAIL。实现侧 ≤1 帧容差不变。"""
    t = float(seconds)
    for _ in range(6):
        sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{t:.3f}", str(path)])
        got = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout.strip() or "nan")
        if abs(got - seconds) <= 0.012: return got
        t -= 0.024 if got > seconds else -0.024
    tc.fail(f"测试数据：静音 mp3 实测 {got}s 与 audio_seconds={seconds}s 差 >12 ms")

class TestChecksAndStyle(SkillTestCase):
    def job(self, slug, aspect):
        w, h = (1920, 1080) if aspect == "landscape" else (1080, 1440)   # v1.3：竖屏 3:4
        (slug / "job.json").write_text(json.dumps({"topic": "t", "slug": slug.name, "aspect": aspect, "width": w, "height": h, "fps": 30,
                                                   "created_at": "2026-10-22T00:00:00+08:00"}))

    def example_project(self, sd, aspect="landscape"):
        """用 example 的 timeline.fixture.json + 同长静音 mp3 建完整工程（scaffold → 场景 → build_timeline → npm ci）。"""
        ex = sd / "assets/example"
        if not ex.exists(): self.fail(f"未实现：缺少 {ex}")
        slug = self.tmpdir() / "demo"; (slug / "voice").mkdir(parents=True); self.job(slug, aspect)
        fx = load_json(ex / "timeline.fixture.json"); shutil.copy(ex / "timeline.fixture.json", slug / "voice/timeline.json")
        silent_mp3(self, slug / "voice/full.mp3", fx["audio_seconds"])
        shutil.copy(ex / "storyboard.json", slug / "storyboard.json")
        man = ex / "assets-manifest.json"
        (slug / "assets-manifest.json").write_text(man.read_text() if man.exists() else '{"version": 1, "assets": []}')
        p = self.cli("scaffold_project.py", "--job", slug / "job.json", "--out", slug / "project", skill_dir=sd); self.assertEqual(p.returncode, 0, p.stderr)
        sc = slug / "project/src/scenes"; sc.mkdir(parents=True, exist_ok=True)
        for f in (ex / "scenes").glob("*.tsx"): shutil.copy(f, sc / f.name)
        subs = slug / "voice/subtitles.json"
        if not subs.exists():
            subs.write_text(json.dumps({"engine": "fake", "speaker": "s", "cues": [
                {"id": f"c{l['id']}", "line_id": l["id"], "text": l["text"], "start": l["start"], "end": l["end"]} for l in fx["lines"]]}, ensure_ascii=False))
        p = self.cli("build_timeline.py", "--timeline", slug / "voice/timeline.json", "--storyboard", slug / "storyboard.json", "--subtitles", subs,
                     "--manifest", slug / "assets-manifest.json", "--project", slug / "project", skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = sh(["npm", "ci", "--no-audit", "--no-fund"], cwd=slug / "project"); self.assertEqual(p.returncode, 0, p.stderr[-500:])
        return slug

    def check(self, sd, slug, aspect="landscape"):
        return self.cli("check_project.sh", slug, "--aspect", aspect, skill_dir=sd, timeout=3600)

    def report(self, slug):
        return load_json(slug / "check/report.json")

    @covers("I-CK-01", "F-11")
    def test_check_project_reports_failure(self):
        """注入 TS 错误 → 退出 7；report.json（Q-10）ok=false、failed_step="tsc"、log_path 为存在的绝对路径；report 通过 check-report.schema.json"""
        sd = self.copy_skill(); slug = self.example_project(sd)
        (slug / "project/src/Broken.ts").write_text("const x: number = 'not a number';\nexport default x;\n")
        self.assertEqual(self.check(sd, slug).returncode, 7)
        rep = self.report(slug)
        self.assertIs(rep["ok"], False); self.assertEqual(rep["failed_step"], "tsc"); self.assertEqual(rep["attempt"], 1)
        self.assertTrue(Path(rep["log_path"]).is_absolute() and Path(rep["log_path"]).exists(), rep)
        errs = self.libfn("schema_check", "validate")(rep, load_json(sd / "assets/schemas/check-report.schema.json"))
        self.assertEqual(errs, [])

    @covers("I-CK-03", "F-11", "NF-07")
    def test_check_project_attempt_limit(self):
        """Q-06 / R-08：check_project.sh 总调用 ≤3。连续 3 次失败后修好错误，第 4 次调用仍退出 7，stdout 末行 JSON errors[0].kind == max_attempts_exceeded（attempts=3），stderr 含“上限”；attempts.json 记录 n=1..3"""
        sd = self.copy_skill(); slug = self.example_project(sd)
        bad = slug / "project/src/Broken.ts"; bad.write_text("const x: number = 'x';\nexport default x;\n")
        for i in range(3):
            self.assertEqual(self.check(sd, slug).returncode, 7)
            self.assertEqual(self.report(slug)["attempt"], i + 1)
        att = load_json(slug / "check/attempts.json")
        self.assertEqual([a["n"] for a in att[:3]], [1, 2, 3]); self.assertTrue(all(a["ok"] is False for a in att[:3]))
        bad.unlink()
        p = self.check(sd, slug); self.assertEqual(p.returncode, 7)
        lines = [l for l in p.stdout.strip().splitlines() if l.strip()]
        self.assertTrue(lines, "R-08：stdout 最后一行应为 JSON")
        try: last = json.loads(lines[-1])
        except json.JSONDecodeError: self.fail(f"stdout 最后一行不是 JSON：{lines[-1][:200]}")
        self.assertEqual(last["errors"][0]["kind"], "max_attempts_exceeded")   # 主断言（R-08）
        self.assertEqual(last["errors"][0].get("attempts"), 3)
        self.assertIn("上限", p.stderr)   # 辅助断言

    @covers("I-CK-05", "F-08", "F-09")
    def test_extra_data_layer_rejected(self):
        """Q-13② / R-09：在 src/Main.tsx 的 {/* @test-inject:layers */} 锚点处注入 data-layer="endcard" → 自检失败 failed_step='safe_area'"""
        sd = self.copy_skill(); slug = self.example_project(sd)
        main = slug / "project/src/Main.tsx"
        if not main.exists(): self.fail(f"缺 {main}")
        t = main.read_text(); anchor = "{/* @test-inject:layers */}"
        self.assertEqual(t.count(anchor), 1, "R-09：Main.tsx 中注入锚点须恰好 1 处")
        main.write_text(t.replace(anchor, anchor + '<div data-layer="endcard" style={{position:"absolute"}}/>'))
        self.assertEqual(self.check(sd, slug).returncode, 7); self.assertEqual(self.report(slug)["failed_step"], "safe_area")

    @covers("I-CK-02", "F-10")
    def test_same_project_both_aspects(self):
        """同一工程 check_project.sh --aspect both：横、竖各生成每段抽帧且安全区检测通过（report ok）"""
        sd = self.copy_skill(); slug = self.example_project(sd)
        p = self.check(sd, slug, "both"); self.assertEqual(p.returncode, 0, (p.stdout + p.stderr)[-800:])
        sb = load_json(slug / "storyboard.json")
        for a in ("landscape", "portrait"):
            for s in sb["sections"]:
                self.assertTrue((slug / f"check/frames/{a}-{s['id']}.png").exists(), (a, s["id"]))
        self.assertIs(self.report(slug)["ok"], True)

    def s03_mid(self, slug):
        ts = (slug / "project/src/data/timeline.ts").read_text()
        m = re.search(r"id:\s*['\"]S03['\"][^}]*?from:\s*(\d+)[^}]*?to:\s*(\d+)", ts, re.S)
        self.assertIsNotNone(m, "timeline.ts 中找不到 S03 区间"); return (int(m.group(1)) + int(m.group(2))) // 2

    def still(self, slug, frame, out):
        p = sh(["npx", "remotion", "still", "src/index.ts", "Main", str(out), f"--frame={frame}"], cwd=slug / "project")
        self.assertEqual(p.returncode, 0, p.stderr[-500:]); return out

    @covers("I-NF6-01", "NF-06", "F-09")
    def test_change_tokens_changes_pixels(self):
        """Q-23：只改 tokens.json（colors.bg→#3A0000、colors.gold→#00E5FF）重新生成工程：S03 中点帧 SHA256 改变且全帧平均 R 升高 ≥8；
        tokens.ts 随之变化、validate.py tokens 通过、SKILL.md 无 diff"""
        sd = self.copy_skill(); skill_before = (sd / "SKILL.md").read_bytes()
        a = self.example_project(sd); fa = self.still(a, self.s03_mid(a), a / "before.png")
        tj = sd / "assets/tokens.json"; tok = json.loads(tj.read_text())
        self.assertIn("bg", tok.get("colors", {})); self.assertIn("gold", tok["colors"])
        tok["colors"]["bg"] = "#3A0000"; tok["colors"]["gold"] = "#00E5FF"; tj.write_text(json.dumps(tok, ensure_ascii=False, indent=2))
        b = self.example_project(sd); fb = self.still(b, self.s03_mid(b), b / "after.png")
        self.assertNotEqual(hashlib.sha256(fa.read_bytes()).hexdigest(), hashlib.sha256(fb.read_bytes()).hexdigest())
        self.assertGreaterEqual(mean_rgb(fb)[0] - mean_rgb(fa)[0], 8)
        ts = (b / "project/src/theme/tokens.ts").read_text().upper()
        self.assertIn("#3A0000", ts); self.assertIn("#00E5FF", ts)
        self.assertEqual(self.cli("validate.py", "tokens", "--json", tj, "--ts", b / "project/src/theme/tokens.ts", skill_dir=sd).returncode, 0)
        self.assertEqual((sd / "SKILL.md").read_bytes(), skill_before)

    @covers("I-JOB-01", "F-10")
    def test_default_landscape_job(self):
        """Q-21 / R-07：job.json 缺 aspect → scaffold 回写 aspect=landscape、width=1920、height=1080；竖屏回写 1080×1440；src/data/job.ts 不含像素数字（1080|1440|1920）"""
        sd = self.copy_skill(); d = self.tmpdir()
        (d / "job.json").write_text(json.dumps({"topic": "t", "slug": "t", "fps": 30, "created_at": "2026-10-22T00:00:00+08:00"}))
        p = self.cli("scaffold_project.py", "--job", d / "job.json", "--out", d / "project", skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(load_json(d / "job.json").get("aspect"), "landscape")
        jt = (d / "project/src/data/job.ts").read_text()
        self.assertIn("landscape", jt)
        j = load_json(d / "job.json"); self.assertEqual((j.get("width"), j.get("height")), (1920, 1080))
        self.assertIsNone(re.search(r"1080|1440|1920", jt), "R-07：job.ts 不得含像素数字")
        d2 = self.tmpdir()
        (d2 / "job.json").write_text(json.dumps({"topic": "t", "slug": "t", "aspect": "portrait", "fps": 30, "created_at": "2026-10-22T00:00:00+08:00"}))
        p = self.cli("scaffold_project.py", "--job", d2 / "job.json", "--out", d2 / "project", skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        j2 = load_json(d2 / "job.json"); self.assertEqual((j2.get("aspect"), j2.get("width"), j2.get("height")), ("portrait", 1080, 1440))
        self.assertIsNone(re.search(r"1080|1440|1920", (d2 / "project/src/data/job.ts").read_text()))
