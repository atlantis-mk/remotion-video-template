"""L2 契约：lib/tts_pipeline.run_tts + 测试替身（F-05、NF-07、F-17、NF-02）；签名按架构 v1.2 §7.5（only: set、max_attempts=3）"""
import json
from pathlib import Path
from py.support import SkillTestCase, covers, FAKE_KEY

LINES = [{"id": f"{i:02d}", "section": "S01" if i < 3 else "S02", "text": f"第{i}句测试文本。", "context": [],
          "speech_rate": 0, "silence_ms": 300} for i in range(1, 5)]

class CountingClient:
    """包装 FakeTtsClient：记录每句调用次数，可让指定句前 n 次抛 TtsTransientError。"""
    def __init__(self, inner, errors, fail_map=None, auth_fail=False):
        self.inner, self.errors, self.fail_map, self.auth_fail = inner, errors, dict(fail_map or {}), auth_fail
        self.calls = []
    def synthesize(self, text, **kw):
        self.calls.append(text)
        if self.auth_fail:
            raise self.errors.TtsAuthError(f"401 bad key {FAKE_KEY}")
        if self.fail_map.get(text, 0) > 0:
            self.fail_map[text] -= 1
            raise self.errors.TtsTransientError("503")
        return self.inner.synthesize(text, **kw)

class TestRunTts(SkillTestCase):
    def setup_deps(self, **kw):
        tc = self.lib("tts_client"); au = self.lib("audio"); log = self.lib("log")
        Fake = self.attr(tc, "FakeTtsClient"); FakeAudio = self.attr(au, "FakeAudioTool")
        errs = tc if hasattr(tc, "TtsTransientError") else self.lib("errors")
        client = CountingClient(Fake(), errs, **kw)
        return client, FakeAudio(), log.Redactor(secrets=[FAKE_KEY]), errs

    def call(self, client, audio, red, out, lines=LINES, **kw):
        run_tts = self.libfn("tts_pipeline", "run_tts")
        return run_tts(lines, client=client, audio=audio, out_dir=out, speaker="zh_male_m191_uranus_bigtts",
                       max_attempts=3, sleeper=lambda s: None, redactor=red, **kw)

    @covers("C-TTS-01", "F-05")
    def test_outputs_and_fields(self):
        """产出 full.mp3、timeline.json、subtitles.json；timeline 每句 9 字段（v1.9 含 speech_end_s）齐全且连续"""
        c, a, r, _ = self.setup_deps(); out = self.tmpdir()
        self.call(c, a, r, out)
        for f in ("full.mp3", "timeline.json", "subtitles.json"):
            self.assertTrue((out / f).exists(), f)
        tl = json.loads((out / "timeline.json").read_text())
        self.assertEqual(len(tl["lines"]), 4)
        for l in tl["lines"]:
            for k in ("id", "text", "context", "silence_ms", "speech_rate", "start", "speech_end_s", "end", "duration_s"):
                self.assertIn(k, l)
        self.assertEqual(tl["lines"][0]["start"], 0)
        for l in tl["lines"]: self.assertGreater(l["duration_s"], 0, l)   # RV-2(e)
        for x, y in zip(tl["lines"], tl["lines"][1:]):
            self.assertAlmostEqual(x["end"], y["start"], delta=0.001)

    @covers("C-TTS-02", "F-05", "NF-07")
    def test_retry_then_success(self):
        """单句前 2 次瞬时失败 → 第 3 次（总尝试上限）成功；该句共 3 次尝试，其余句各 1 次"""
        c, a, r, _ = self.setup_deps(fail_map={LINES[1]["text"]: 2}); out = self.tmpdir()
        self.call(c, a, r, out)
        self.assertEqual(c.calls.count(LINES[1]["text"]), 3)
        for l in (LINES[0], LINES[2], LINES[3]):
            self.assertEqual(c.calls.count(l["text"]), 1)

    @covers("C-TTS-03", "F-05", "NF-07")
    def test_retry_exhausted(self):
        """每句总尝试恰好 3 次后停止（首发 + 2 次重试，Q-17）；耗尽后不生成 full.mp3 半成品，并以“外部服务失败”报错（退出码 6 语义）"""
        c, a, r, errs = self.setup_deps(fail_map={LINES[2]["text"]: 99}); out = self.tmpdir()
        with self.assertRaises(Exception):
            self.call(c, a, r, out)
        self.assertEqual(c.calls.count(LINES[2]["text"]), 3)
        self.assertFalse((out / "full.mp3").exists())

    @covers("C-TTS-04", "NF-07", "F-05")
    def test_only_resynthesize_failed_line(self):
        """第一次跑完后，用 only={'03'} 重跑：只调用第 03 句；未改动句走 parts/ 缓存不再调用"""
        c, a, r, _ = self.setup_deps(); out = self.tmpdir()
        self.call(c, a, r, out)
        c.calls.clear()
        self.call(c, a, r, out, only={"03"})
        self.assertEqual(c.calls, [LINES[2]["text"]])
        c.calls.clear()
        self.call(c, a, r, out)
        self.assertEqual(c.calls, [], "parts/ 文本哈希一致的句应跳过")

    @covers("C-TTS-05", "F-17", "NF-02")
    def test_auth_error_no_retry_no_leak(self):
        """鉴权失败立即停止、不重试；异常消息与产物不含 Key"""
        c, a, r, errs = self.setup_deps(auth_fail=True); out = self.tmpdir()
        with self.assertRaises(errs.TtsAuthError) as cm:
            self.call(c, a, r, out)
        self.assertEqual(len(c.calls), 1)
        self.assertNotIn(FAKE_KEY, str(cm.exception))
        for p in Path(out).rglob("*"):
            if p.is_file():
                self.assertNotIn(FAKE_KEY.encode(), p.read_bytes(), p)

    @covers("C-TTS-06", "F-06", "F-05")
    def test_no_trailing_silence_appended(self):
        """full.mp3 时长 = Σ(句音频) + Σ(silence_ms)，不额外追加尾部静音"""
        c, a, r, _ = self.setup_deps(); out = self.tmpdir()
        self.call(c, a, r, out)
        tl = json.loads((out / "timeline.json").read_text())
        self.assertAlmostEqual(tl["lines"][-1]["end"], tl["audio_seconds"], delta=0.001)

    @covers("C-TTS-07", "F-05", "F-06")
    def test_fake_tts_rule(self):
        """FakeTtsClient（Q-19、R-03、V9-1）：产出 PCM WAV（24 kHz 单声道 16-bit，样本数 = round(220ms×有效字数×24000)），落盘 parts/NN.wav；timeline 每句 speech_end_s − start ≈ 字数×0.22、end − speech_end_s ≈ silence_ms/1000、end − start ≈ duration_s（均 ±1ms）"""
        import wave
        fake = self.attr(self.lib("tts_client"), "FakeTtsClient")()
        res = fake.synthesize("一二三，四五 六。", speaker="s", context=[], speech_rate=0)
        fmt = res["format"] if isinstance(res, dict) else getattr(res, "format", None)
        data = res["audio"] if isinstance(res, dict) else getattr(res, "audio", b"")
        self.assertEqual(fmt, "wav", "R-03：FakeTts 必须产出 WAV"); self.assertEqual(bytes(data[:4]), b"RIFF")
        c, a, r, _ = self.setup_deps(); out = self.tmpdir()
        lines = [{"id": "01", "section": "S01", "text": "一二三，四五 六。", "context": [], "speech_rate": 0, "silence_ms": 300},
                 {"id": "02", "section": "S01", "text": "AI芯片！", "context": [], "speech_rate": 0, "silence_ms": 100}]
        self.call(c, a, r, out, lines=lines)
        tl = json.loads((out / "timeline.json").read_text())
        for ln, n, sil in zip(tl["lines"], (6, 4), (0.3, 0.1)):
            self.assertIn("speech_end_s", ln, "V9-1：speech_end_s 必填")
            self.assertAlmostEqual(ln["speech_end_s"] - ln["start"], n * 0.22, delta=0.001, msg=ln)
            self.assertAlmostEqual(ln["end"] - ln["speech_end_s"], sil, delta=0.001, msg=ln)
            self.assertAlmostEqual(ln["end"] - ln["start"], ln["duration_s"], delta=0.001, msg=ln)
            wp = out / "parts" / f"{ln['id']}.wav"
            self.assertTrue(wp.exists(), f"缺 {wp}（R-03：按 SynthResult.format 落盘 parts/NN.wav）")
            with wave.open(str(wp)) as w:
                self.assertEqual((w.getframerate(), w.getnchannels(), w.getsampwidth()), (24000, 1, 2))
                self.assertEqual(w.getnframes(), round(n * 0.22 * 24000))

    @covers("C-TTS-10", "F-05", "F-06")
    def test_full_mp3_matches_last_end(self):
        """R-03③ / Q-08：run_tts(FakeTtsClient, FfmpegAudioTool) 真实编码后，ffprobe(full.mp3) 与 timeline 末句 end 之差 ≤50ms"""
        import shutil, subprocess
        if not shutil.which("ffprobe"): self.fail("测试环境缺 ffprobe")
        tc = self.lib("tts_client"); au = self.lib("audio"); log = self.lib("log")
        c = self.attr(tc, "FakeTtsClient")(); a = self.attr(au, "FfmpegAudioTool")(); out = self.tmpdir()
        self.call(c, a, log.Redactor(secrets=[FAKE_KEY]), out)
        tl = json.loads((out / "timeline.json").read_text())
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / "full.mp3")], capture_output=True, text=True)
        self.assertLessEqual(abs(float(p.stdout.strip()) - tl["lines"][-1]["end"]), 0.050)

    @covers("C-TTS-11", "F-04", "F-05")
    def test_empty_line_rejected_before_tts(self):
        """RV-2(b)：稿件含空句 → tts_doubao.py 退出 5，stdout 末行 errors[0].kind == "empty_line"，不产出文件；
        进程内把 DoubaoHttpClient 换成计数的 FakeTtsClient 后再跑同一 CLI main，FakeTts 构造与调用次数均为 0"""
        import importlib.util, io, contextlib, sys
        sd = self.copy_skill(); d = self.tmpdir(); s = d / "script.md"
        s.write_text("# t\n## S01 a\n- [01] 正常一句。\n- [05] ……\n", encoding="utf-8")
        out = d / "voice"
        p = self.cli("tts_doubao.py", s, "--out-dir", out, "--skill-dir", sd, skill_dir=sd)
        self.assertEqual(p.returncode, 5, p.stdout + p.stderr)
        last = json.loads(p.stdout.strip().splitlines()[-1]); self.assertEqual(last["errors"][0]["kind"], "empty_line")
        self.assertFalse(out.exists() and any(out.rglob("*")), "空句时不得产出任何配音文件")
        # 进程内计数（测试侧替身，Q-11：不在 CLI 上加 fake 开关）
        tc = self.lib("tts_client"); Fake = self.attr(tc, "FakeTtsClient"); n = {"init": 0, "call": 0}
        class Counting(Fake):
            def __init__(self, *a, **k): n["init"] += 1; super().__init__()
            def synthesize(self, *a, **k): n["call"] += 1; return super().synthesize(*a, **k)
        orig = getattr(tc, "DoubaoHttpClient", None); tc.DoubaoHttpClient = Counting
        try:
            spec = importlib.util.spec_from_file_location("tts_doubao_under_test", sd / "scripts/tts_doubao.py")
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = mod.main([str(s), "--out-dir", str(d / "voice2"), "--skill-dir", str(sd)])
        finally:
            if orig is not None: tc.DoubaoHttpClient = orig
        self.assertEqual(rc, 5); self.assertEqual(n, {"init": 0, "call": 0})

    @covers("C-TTS-12", "F-05")
    def test_fake_duration_for_floor(self):
        """RV-2(c)(d)：FakeTtsClient().duration_for("") == duration_for("。") == 0.220（防御性兜底）；duration_for("你好") == 0.440"""
        f = self.attr(self.lib("tts_client"), "FakeTtsClient")()
        self.assertAlmostEqual(f.duration_for(""), 0.220, places=6)
        self.assertAlmostEqual(f.duration_for("。"), 0.220, places=6)
        self.assertAlmostEqual(f.duration_for("你好"), 0.440, places=6)

    @covers("C-TTS-08", "F-05")
    def test_max_attempts_upper_bound(self):
        """max_attempts 上限 3：传 4 → 抛参数错误（不得放宽到 4 次）"""
        c, a, r, _ = self.setup_deps(); out = self.tmpdir()
        run_tts = self.libfn("tts_pipeline", "run_tts")
        with self.assertRaises((ValueError, Exception)):
            run_tts(LINES, client=c, audio=a, out_dir=out, speaker="s", max_attempts=4, sleeper=lambda s: None, redactor=r)
        self.assertEqual(c.calls, [])
