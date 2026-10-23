"""L1 单元：lib/timeline.py（F-05、F-06）；签名按架构 v1.2 §7.5"""
import json
from py.support import SkillTestCase, covers, load_json

def line(i, sec, rate=0, pause=300):
    return {"id": f"{i:02d}", "section": sec, "text": f"第{i}句。", "context": [], "speech_rate": rate, "silence_ms": pause}

class TestTimeline(SkillTestCase):
    def f(self, name): return self.libfn("timeline", name)

    @covers("U-TL-01", "F-05")
    def test_build_lines_continuous(self):
        """build_timeline_lines(lines, durations_s)：首句从 0、首尾相接、end 含 silence_ms、duration_s=end-start、3 位小数、保留 id/section"""
        lines = [line(1, "S01", pause=300), line(2, "S01", pause=500), line(3, "S02", pause=100)]
        out = self.f("build_timeline_lines")(lines, [1.2345, 2.0, 0.5])
        self.assertEqual([l["id"] for l in out], ["01", "02", "03"]); self.assertEqual(out[2]["section"], "S02")
        self.assertEqual(out[0]["start"], 0)
        for a, b in zip(out, out[1:]):
            self.assertAlmostEqual(b["start"], a["end"], delta=0.001)
        for l in out:
            self.assertAlmostEqual(l["end"] - l["start"], l["duration_s"], delta=0.001)
            self.assertEqual(round(l["end"], 3), l["end"])
        self.assertAlmostEqual(out[0]["end"], 1.2345 + 0.3, delta=0.001)
        self.assertAlmostEqual(out[-1]["end"], 1.2345 + 0.3 + 2.0 + 0.5 + 0.5 + 0.1, delta=0.002)

    @covers("U-TL-02", "F-05")
    def test_validate_continuity_rejects_overlap_and_gap(self):
        """validate_continuity 返回错误列表（空=通过；v1.9 样例补 speech_end_s=end、silence_ms=0）：重叠、空隙、首句非 0、duration 不符、末句超出音频均不通过"""
        v = self.f("validate_continuity")
        ok = [{"start": 0, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 1}, {"start": 1, "speech_end_s": 2.5, "silence_ms": 0, "end": 2.5, "duration_s": 1.5}]
        self.assertEqual(v(ok, 2.5), [])
        self.assertEqual(v([{"start": 0, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 1}, {"start": 1.0005, "speech_end_s": 2, "silence_ms": 0, "end": 2, "duration_s": 0.9995}], 2), [])  # 1ms 容差内
        bad = [
            ([{"start": 0, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 1}, {"start": 0.9, "speech_end_s": 2, "silence_ms": 0, "end": 2, "duration_s": 1.1}], 10),
            ([{"start": 0, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 1}, {"start": 1.1, "speech_end_s": 2, "silence_ms": 0, "end": 2, "duration_s": 0.9}], 10),
            ([{"start": 0.2, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 0.8}], 10),
            ([{"start": 0, "speech_end_s": 1, "silence_ms": 0, "end": 1, "duration_s": 0.7}], 10),
            ([{"start": 0, "speech_end_s": 3, "silence_ms": 0, "end": 3, "duration_s": 3}], 2.5),
        ]
        for b, a in bad:
            r = v(b, a); self.assertIsInstance(r, list); self.assertTrue(r, b)

    @covers("U-TL-03", "F-06")
    def test_clamp_to_audio(self):
        """末句 end 超出 ffprobe 时长时钳位到 audio_seconds（参考项目 134.419 > 133.608）"""
        out = self.f("clamp_to_audio")([{"start": 0, "speech_end_s": 100.0, "silence_ms": 0, "end": 100.0, "duration_s": 100.0}, {"start": 100.0, "speech_end_s": 134.419, "silence_ms": 0, "end": 134.419, "duration_s": 34.419}], 133.608)
        self.assertEqual(out[-1]["end"], 133.608)
        self.assertAlmostEqual(out[-1]["duration_s"], 33.608, places=3)

    @covers("U-TL-04", "F-06")
    def test_sec_to_frame(self):
        """sec_to_frame = floor(s*fps+0.5)（四舍五入，非银行家舍入）"""
        f = self.f("sec_to_frame")
        self.assertEqual(f(133.608, 30), 4008); self.assertEqual(f(0, 30), 0)
        self.assertEqual(f(1.0166, 30), 30); self.assertEqual(f(60.02, 30), 1801)
        self.assertEqual(f(1.25, 2), 3)   # 2.5 → 3（Python round 会得 2）
        self.assertEqual(f(0.75, 2), 2)   # 1.5 → 2
        self.assertEqual(f(133.608), 4008)  # fps 默认 30

    @covers("U-TL-05", "F-05")
    def test_split_cues(self):
        """split_cues(line)：按标点切分并按字数比例分配，cue 在句区间内、连续、id 唯一"""
        cues = self.f("split_cues")({"id": "01", "section": "S01", "text": "半年融资一千五百亿，估值五千亿。", "start": 2.0, "speech_end_s": 6.0, "silence_ms": 0, "end": 6.0, "duration_s": 4.0})
        self.assertGreaterEqual(len(cues), 2)
        self.assertEqual(cues[0]["start"], 2.0); self.assertAlmostEqual(cues[-1]["end"], 6.0, places=3)
        self.assertEqual(len({c["id"] for c in cues}), len(cues))
        for a, b in zip(cues, cues[1:]):
            self.assertAlmostEqual(a["end"], b["start"], places=3)
        self.assertTrue(all(c["line_id"] == "01" for c in cues))

    # ---- v1.9 V9-1：speech_end_s 必填；句后停顿计入本句区间 ----
    def _tl(self, lines, audio=None):
        return {"version": 1, "engine": "fake", "speaker": "s", "fps": 30,
                "audio_seconds": audio if audio is not None else lines[-1]["end"], "lines": lines}

    def _ln(self, i, start, speech, end, sil_ms):
        return {"id": f"{i:02d}", "section": "S01", "text": f"第{i}句。", "context": [], "speech_rate": 0,
                "silence_ms": sil_ms, "start": start, "speech_end_s": speech, "end": end, "duration_s": round(end - start, 3)}

    @covers("U-TL-06", "F-05")
    def test_schema_requires_speech_end(self):
        """V9-1：timeline.schema.json 中 lines.items.required 含 speech_end_s，缺失 → Schema 校验失败；speech_end_s 为 number 且 >0；duration_s exclusiveMinimum 0"""
        sch = load_json(self.require_path("assets/schemas/timeline.schema.json")); v = self.libfn("schema_check", "validate")
        good = [self._ln(1, 0, 1.0, 1.3, 300), self._ln(2, 1.3, 2.0, 2.0, 0)]
        item = sch["properties"]["lines"]["items"]
        self.assertIn("speech_end_s", item.get("required", []))
        self.assertEqual(item["properties"]["speech_end_s"].get("exclusiveMinimum"), 0)
        self.assertEqual(item["properties"]["duration_s"].get("exclusiveMinimum"), 0)
        bad = json.loads(json.dumps(good)); del bad[0]["speech_end_s"]
        self.assertTrue(v(self._tl(bad), sch), "缺 speech_end_s 应校验失败")

    @covers("U-TL-07", "F-05")
    def test_continuity_speech_end_after_end(self):
        """V9-1：validate_continuity 对 speech_end_s > end（及 speech_end_s ≤ start）报错；合规样例通过"""
        v = self.f("validate_continuity")
        ok = [self._ln(1, 0, 1.0, 1.3, 300), self._ln(2, 1.3, 2.0, 2.2, 200)]
        self.assertEqual(v(ok, 2.2), [])
        b1 = [self._ln(1, 0, 1.5, 1.3, 300), self._ln(2, 1.3, 2.0, 2.2, 200)]
        self.assertTrue(v(b1, 2.2), "speech_end_s > end 应报错")
        b2 = [self._ln(1, 0, 0, 0.3, 300)]
        self.assertTrue(v(b2, 0.3), "speech_end_s ≤ start 应报错")

    @covers("U-TL-08", "F-05")
    def test_continuity_silence_mismatch(self):
        """V9-1：非末句 end − speech_end_s 与 silence_ms/1000 不符（超出 1ms）→ 报错；恰好相等通过"""
        v = self.f("validate_continuity")
        bad = [self._ln(1, 0, 1.0, 1.5, 300), self._ln(2, 1.5, 2.0, 2.2, 200)]   # 0.5 ≠ 0.3
        self.assertTrue(v(bad, 2.2))
        bad2 = [self._ln(1, 0, 1.0, 1.302, 300), self._ln(2, 1.302, 2.0, 2.2, 200)]   # 差 2ms
        self.assertTrue(v(bad2, 2.2))

    @covers("U-TL-09", "F-06")
    def test_clamp_last_line_speech_end(self):
        """V9-1：clamp_to_audio 钳位末句后 end == audio_seconds、duration_s = end − start、speech_end_s = min(speech_end_s, end) ≤ end，且 validate_continuity 通过"""
        lines = [self._ln(1, 0, 1.0, 1.3, 300), self._ln(2, 1.3, 2.5, 2.8, 300)]
        out = self.f("clamp_to_audio")(json.loads(json.dumps(lines)), 2.4)
        last = out[-1]
        self.assertEqual(last["end"], 2.4); self.assertAlmostEqual(last["duration_s"], 2.4 - 1.3, places=3)
        self.assertLessEqual(last["speech_end_s"], last["end"]); self.assertEqual(last["speech_end_s"], 2.4)
        out2 = self.f("clamp_to_audio")(json.loads(json.dumps(lines)), 2.6)   # 只截掉部分停顿
        self.assertEqual(out2[-1]["speech_end_s"], 2.5); self.assertLessEqual(out2[-1]["end"] - out2[-1]["speech_end_s"], 0.3 + 0.001)
        self.assertEqual(self.f("validate_continuity")(out2, 2.6), [])

    @covers("U-TL-10", "F-05")
    def test_split_cues_end_at_speech_end(self):
        """V9-1：字幕只在 [start, speech_end_s] 显示：split_cues 首个 cue start = start，最后一个 cue end = speech_end_s，所有 cue 不进入停顿"""
        ln = {"id": "01", "section": "S01", "text": "半年融资一千五百亿，估值五千亿。", "start": 2.0, "speech_end_s": 5.5, "end": 6.0, "duration_s": 4.0, "silence_ms": 500}
        cues = self.f("split_cues")(ln)
        self.assertEqual(cues[0]["start"], 2.0); self.assertAlmostEqual(cues[-1]["end"], 5.5, places=3)
        self.assertTrue(all(c["end"] <= 5.5 + 0.001 for c in cues))
