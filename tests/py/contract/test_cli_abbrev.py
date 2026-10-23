"""L2 契约：所有 CLI 脚本禁用参数前缀缩写（架构 v1.10 §4.0：argparse allow_abbrev=False，子命令同样适用）。
每条用例：除被测参数外其余必需参数都给全，只把某个长参数写成它的前缀缩写 → 必须退出 2，且 stderr 指出该缩写参数（排除“因缺必需参数而退出 2”的假阳性）。"""
import json
from py.support import SkillTestCase, covers, FIXTURES

class TestCliNoAbbrev(SkillTestCase):
    def must_reject(self, script, *args, abbr, **kw):
        p = self.cli(script, *args, **kw)
        self.assertEqual(p.returncode, 2, f"{script} 接受了缩写 {abbr}：退出 {p.returncode}\n{(p.stdout + p.stderr)[-400:]}")
        self.assertIn(abbr, p.stderr, f"{script}：退出 2 但 stderr 未指出 {abbr}（可能是别的用法错误）")

    @covers("C-ABR-01", "F-05")
    def test_tts_doubao(self):
        """tts_doubao.py：--dry（--dry-run 的前缀）、--max（--max-attempts）→ 2"""
        sd = self.copy_skill(); s = self.require_path("assets/example/script.md"); o = self.tmpdir()
        self.must_reject("tts_doubao.py", s, "--out-dir", o, "--dry", abbr="--dry", skill_dir=sd)
        self.must_reject("tts_doubao.py", s, "--out-dir", o, "--dry-run", "--max", "3", abbr="--max", skill_dir=sd)

    @covers("C-ABR-02", "F-17")
    def test_check_env(self):
        """check_env.py：--skill（--skill-dir 的前缀）、--no-cmd（--no-cmd-check）→ 2"""
        sd = self.copy_skill()
        self.must_reject("check_env.py", "--skill", sd, abbr="--skill", skill_dir=sd)
        self.must_reject("check_env.py", "--skill-dir", sd, "--no-cmd", abbr="--no-cmd", skill_dir=sd)

    @covers("C-ABR-03", "F-08")
    def test_fetch_asset(self):
        """fetch_asset.py add：--source-n（--source-name 的前缀）→ 2；prune：--story（--storyboard）→ 2"""
        d = self.tmpdir()
        self.must_reject("fetch_asset.py", "add", "--manifest", d / "m.json", "--id", "A01", "--file", FIXTURES / "img_2000x1200.png",
                         "--content", "c", "--ai-generated", "--license", "AI 生成", "--source-n", "AI 生成", "--dest", d / "media", abbr="--source-n")
        self.must_reject("fetch_asset.py", "prune", "--manifest", d / "m.json", "--story", d / "sb.json", abbr="--story")

    @covers("C-ABR-04", "F-09", "F-10")
    def test_scaffold_project(self):
        """scaffold_project.py：--for（--force 的前缀）→ 2"""
        sd = self.copy_skill(); d = self.tmpdir()
        (d / "job.json").write_text(json.dumps({"topic": "t", "slug": "t", "fps": 30, "created_at": "2026-10-22T00:00:00+08:00"}))
        self.must_reject("scaffold_project.py", "--job", d / "job.json", "--out", d / "project", "--for", abbr="--for", skill_dir=sd)

    @covers("C-ABR-05", "F-06", "F-07")
    def test_build_timeline(self):
        """build_timeline.py：--time（--timeline 的前缀）→ 2（其余必需参数给全）"""
        d = self.tmpdir()
        self.must_reject("build_timeline.py", "--time", FIXTURES / "mcp_timeline_good.json", "--storyboard", d / "sb.json",
                         "--project", d / "project", abbr="--time")

    @covers("C-ABR-06", "F-12", "NF-02")
    def test_validate(self):
        """validate.py 子命令同样禁用缩写：storyboard --time（--timeline）、tokens --js（--json）、video --vid（--video）→ 2"""
        d = self.tmpdir()
        self.must_reject("validate.py", "storyboard", d / "sb.json", "--time", d / "tl.json", abbr="--time")
        self.must_reject("validate.py", "tokens", "--ts", d / "tokens.ts", "--js", d / "t.json", abbr="--js")
        self.must_reject("validate.py", "video", d, "--vid", d / "v.mp4", abbr="--vid")

    @covers("C-ABR-07", "F-11")
    def test_check_project(self):
        """check_project.sh：--asp（--aspect 的前缀）、--determ（--determinism）→ 2"""
        d = self.tmpdir()
        self.must_reject("check_project.sh", d, "--asp", "landscape", abbr="--asp")
        self.must_reject("check_project.sh", d, "--determ", abbr="--determ")

    @covers("C-ABR-08", "F-12")
    def test_render(self):
        """render.sh：--covers（--covers-only 的前缀）、--video（--video-only）→ 2"""
        d = self.tmpdir()
        self.must_reject("render.sh", d, "--covers", abbr="--covers")
        self.must_reject("render.sh", d, "--video", abbr="--video")
