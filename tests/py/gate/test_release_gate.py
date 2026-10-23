"""L0 门禁工具：tests/tools/release_gate.py 与 run_all.sh 的 SKIP 规则（架构 v1.7 §7.3.1 / QA RV-1）；
v1.11 默认 SKILL_DIR 路径（A-21）。这些用例校验测试侧工具本身，不依赖技能包实现，因此对空技能包也应通过。"""
import hashlib, importlib.util, json, os, shutil, subprocess, tempfile, types, unittest
from pathlib import Path
from py.support import covers, TESTS_DIR, REPO_DIR, DEFAULT_SKILL_REL

spec = importlib.util.spec_from_file_location("release_gate", TESTS_DIR / "tools/release_gate.py")
rg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rg)
IDS = sorted(p.stem for p in (TESTS_DIR / "agent-eval/cases").glob("AE-*.json"))
OK_EV = types.SimpleNamespace(evaluate=lambda cid, d: [])

class TestReleaseGate(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="gate-")); self.addCleanup(shutil.rmtree, self.root, True)
        self.sd = self.root / "skill"; self.sd.mkdir(); (self.sd / "SKILL.md").write_text("---\nname: x\n---\nbody\n")
        self.sha = hashlib.sha256((self.sd / "SKILL.md").read_bytes()).hexdigest()
        self.ar = self.root / "archive"

    def put(self, cid, run="20261023-000000", **over):
        d = self.ar / cid / run; d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}.jsonl").write_text('{"turn":1,"role":"user","content":"x","ts":"2026-10-23T00:00:00+08:00"}\n')
        (d / f"{cid}.meta.json").write_text("{}")
        v = {"case_id": cid, "result": "PASS", "skill_md_sha256": self.sha, "judged_by": "human", "judged_at": "2026-10-23T00:00:00+08:00"}
        v.update(over); v = {k: x for k, x in v.items() if x is not None}
        (d / f"{cid}.verdict.json").write_text(json.dumps(v)); return d

    @covers("G-REL-01", "F-16")
    def test_all_15_pass(self):
        """cases/ 下恰有 AE-01～AE-15 共 15 个；15 份有效 PASS 存档 → 全部 OK，无缺失"""
        self.assertEqual(IDS, [f"AE-{i:02d}" for i in range(1, 16)])
        for c in IDS: self.put(c)
        ok, bad = rg.check_archive(self.sd, self.ar, ev=OK_EV)
        self.assertEqual((sorted(ok), bad), (IDS, {}))

    @covers("G-REL-02", "F-16")
    def test_missing_and_cli_exit(self):
        """缺 1 份 → 列出该 case_id；release_gate.py --archive-only 对空 archive 退出非 0 并列出全部 15 个 case_id"""
        for c in IDS[1:]: self.put(c)
        ok, bad = rg.check_archive(self.sd, self.ar, ev=OK_EV)
        self.assertEqual(list(bad), [IDS[0]]); self.assertIn("MISSING", bad[IDS[0]][0])
        p = subprocess.run(["python3", str(TESTS_DIR / "tools/release_gate.py"), "--archive-only", "--skill-dir", self.sd, "--archive", self.root / "empty"],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        for c in IDS: self.assertIn(c, p.stdout)

    @covers("G-REL-03", "F-16")
    def test_sha_mismatch_invalid(self):
        """skill_md_sha256 与当前 SKILL.md 不一致 → 视为失效；改 SKILL.md 后旧存档全部失效"""
        for c in IDS: self.put(c)
        (self.sd / "SKILL.md").write_text("changed\n")
        ok, bad = rg.check_archive(self.sd, self.ar, ev=OK_EV)
        self.assertEqual(ok, []); self.assertEqual(sorted(bad), IDS)
        self.assertTrue(all("skill_md_sha256" in " ".join(r) for r in bad.values()))

    @covers("G-REL-04", "F-16")
    def test_verdict_format_strict(self):
        """result=FAIL、多余/缺失字段、judged_by 非 auto|human、judged_at 非 ISO8601、缺 jsonl 或 meta.json → 均失效"""
        variants = [dict(result="FAIL"), dict(extra=1), dict(judged_at=None), dict(judged_by="robot"), dict(judged_at="昨天"), dict(case_id="AE-99")]
        for v in variants:
            shutil.rmtree(self.ar, True); self.put("AE-01", **v)
            _, bad = rg.check_archive(self.sd, self.ar, ev=OK_EV); self.assertIn("AE-01", bad, v)
        for suf in (".jsonl", ".meta.json"):
            shutil.rmtree(self.ar, True); d = self.put("AE-01"); (d / f"AE-01{suf}").unlink()
            _, bad = rg.check_archive(self.sd, self.ar, ev=OK_EV); self.assertIn("AE-01", bad, suf)

    @covers("G-REL-05", "F-16")
    def test_rejudge_and_multiple_runs(self):
        """evaluate.py 复判不通过 → 失效（即使 verdict 写 PASS）；同一用例一份 FAIL + 一份有效 PASS → OK；默认用真实 evaluate.py 复判伪造的空记录 → 失效"""
        self.put("AE-01")
        bad_ev = types.SimpleNamespace(evaluate=lambda cid, d: ["问号数不符"])
        _, bad = rg.check_archive(self.sd, self.ar, ev=bad_ev); self.assertIn("evaluate 复判", " ".join(bad["AE-01"]))
        _, bad = rg.check_archive(self.sd, self.ar); self.assertIn("AE-01", bad)   # 真实复判：meta 为空 → 失效
        self.put("AE-02", run="r1", result="FAIL"); self.put("AE-02", run="r2")
        ok, _ = rg.check_archive(self.sd, self.ar, ev=OK_EV); self.assertIn("AE-02", ok)

    @covers("G-REL-06", "F-16")
    def test_run_all_skip_rules(self):
        """run_all.sh：L1–L4 出现 SKIP → 退出非 0（SKIP 按 FAIL 计）；L5 的 SKIP 不计失败；release 子命令调用 release_gate.py"""
        cp = self.root / "tests"
        shutil.copytree(TESTS_DIR, cp, ignore=shutil.ignore_patterns("node_modules", ".venv", "__pycache__", "transcripts", "archive"))
        for l in ("unit", "contract", "static", "integration", "agent_eval", "gate"):
            for f in (cp / "py" / l).glob("test_*.py"): f.unlink()
        (cp / "py/unit/test_zz.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_s(self): self.skipTest('dep missing')\n")
        p = subprocess.run(["bash", str(cp / "run_all.sh"), "unit"], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0, p.stdout[-500:])
        (cp / "py/unit/test_zz.py").rename(cp / "py/agent_eval/test_zz.py")
        p = subprocess.run(["bash", str(cp / "run_all.sh"), "agent"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout[-500:])
        self.assertRegex((TESTS_DIR / "run_all.sh").read_text(), r"release\)[^;]*tools/release_gate\.py")

    @covers("G-PATH-01", "F-01")
    def test_default_skill_dir_path(self):
        """v1.11 A-21：默认 SKILL_DIR = 仓库根/.agents/skills/remotion-infographic-video（相对 tests/ 为 ../.agents/skills/remotion-infographic-video）"""
        self.assertEqual(DEFAULT_SKILL_REL.as_posix(), ".agents/skills/remotion-infographic-video")
        expected = (REPO_DIR / DEFAULT_SKILL_REL).resolve()
        rel_from_tests = Path(os.path.relpath(expected, TESTS_DIR))
        self.assertEqual(rel_from_tests.as_posix(), "../.agents/skills/remotion-infographic-video")
        # 各入口注释/默认值与公式一致（不依赖环境变量当前是否覆盖）
        for f, needle in [
            (TESTS_DIR / "run_all.sh", "../.agents/skills/remotion-infographic-video"),
            (TESTS_DIR / "tools/release_gate.py", '.agents/skills/remotion-infographic-video'),
            (TESTS_DIR / "agent-eval/run_case.py", '.agents/skills/remotion-infographic-video'),
            (TESTS_DIR / "ts/helpers.ts", "'.agents', 'skills', 'remotion-infographic-video'"),
            (TESTS_DIR / "py/support.py", "DEFAULT_SKILL_REL"),
        ]:
            self.assertIn(needle, f.read_text(encoding="utf-8"), f"路径默认值未同步：{f}")
