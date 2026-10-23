"""L2 契约：CLI 退出码与 stdout JSON 摘要（§4.0），各脚本接口（F-04/05/07/08/09/13/15/16/17、NF-02/03/04/07）"""
import json, shutil
from pathlib import Path
from py.support import SkillTestCase, covers, FAKE_KEY, FIXTURES, SKILL_DIR

PLATS = ["douyin", "bilibili", "xiaohongshu", "channels", "youtube"]   # v1.4 default_targets

PY_CLIS = ["check_env.py", "tts_doubao.py", "scaffold_project.py", "build_timeline.py", "fetch_asset.py", "validate.py"]

class TestCliContracts(SkillTestCase):
    @covers("C-CLI-01", "F-11", "NF-01")
    def test_help_and_noninteractive(self):
        """所有 CLI 支持 --help 且退出 0；stdin 关闭时不阻塞（无交互）"""
        for s in PY_CLIS + ["check_project.sh", "render.sh"]:
            p = self.cli(s, "--help")
            self.assertEqual(p.returncode, 0, f"{s}: {p.stderr[-300:]}")

    @covers("C-ENV-01", "F-17")
    def test_check_env_missing(self):
        """.env 缺失 → 退出 3，errors[0].kind=missing_env，含绝对 env_path 与 var"""
        sd = self.copy_skill(with_env=False)
        p = self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd)
        self.assertEqual(p.returncode, 3)
        s = self.summary(p)
        self.assertFalse(s["ok"]); self.assertEqual(s["code"], 3)
        e = s["errors"][0]
        self.assertEqual(e["kind"], "missing_env"); self.assertEqual(e["var"], "DOUBAO_TTS_API_KEY")
        self.assertEqual(Path(e["env_path"]), (sd / ".env").resolve())

    @covers("C-ENV-02", "F-17")
    def test_check_env_empty(self):
        """Key 为空 → 退出 3，kind=empty_key"""
        sd = self.copy_skill(key="")
        p = self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd)
        self.assertEqual(p.returncode, 3); self.assertEqual(self.summary(p)["errors"][0]["kind"], "empty_key")

    @covers("C-ENV-03", "F-17", "NF-02")
    def test_check_env_ok_no_leak(self):
        """有效 Key → 退出 0；stdout/stderr 不含 Key、不含其长度或前缀"""
        sd = self.copy_skill()
        p = self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        s = self.summary(p); self.assertTrue(s["ok"])
        out = p.stdout + p.stderr
        self.assertNotIn(FAKE_KEY, out); self.assertNotIn(FAKE_KEY[:8], out)

    @covers("C-ENV-04", "F-17")
    def test_check_env_rerun_after_fill(self):
        """先缺失(3) → 写入 Key 后重跑 → 0（对应“填好了”后重新读取）"""
        sd = self.copy_skill(with_env=False)
        self.assertEqual(self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd).returncode, 3)
        (sd / ".env").write_text(f"DOUBAO_TTS_API_KEY={FAKE_KEY}\n")
        self.assertEqual(self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd).returncode, 0)

    @covers("C-ENV-05", "F-17")
    def test_tts_refuses_without_key(self):
        """缺 Key 时 tts_doubao.py 退出 3，且不产出任何音频/时间轴"""
        sd = self.copy_skill(with_env=False); out = self.tmpdir() / "voice"
        script = self.require_path("assets/example/script.md")
        p = self.cli("tts_doubao.py", script, "--out-dir", out, skill_dir=sd)
        self.assertEqual(p.returncode, 3)
        self.assertFalse((out / "full.mp3").exists()); self.assertFalse((out / "timeline.json").exists())

    @covers("C-ENV-06", "F-17", "NF-02")
    def test_tts_dry_run_masks_key(self):
        """--dry-run 输出鉴权说明但不含 Key 明文"""
        sd = self.copy_skill(); out = self.tmpdir() / "voice"
        p = self.cli("tts_doubao.py", self.require_path("assets/example/script.md"), "--out-dir", out, "--dry-run", skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn(FAKE_KEY, p.stdout + p.stderr)
        self.assertIn("not shown", p.stdout + p.stderr)

    @covers("C-SRC-01", "F-04", "NF-03")
    def test_validate_sources(self):
        """示例 script/sources 通过(0)；删掉一条来源 → 退出 5"""
        ex = self.require_path("assets/example")
        p = self.cli("validate.py", "sources", ex / "script.md", ex / "sources.md")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        d = self.tmpdir()
        (d / "script.md").write_text("# t\n## S01 a\n- [01] 半年融资一千五百亿。\n", encoding="utf-8")
        (d / "sources.md").write_text("# 来源\n\n```json\n[]\n```\n", encoding="utf-8")
        p = self.cli("validate.py", "sources", d / "script.md", d / "sources.md")
        self.assertEqual(p.returncode, 5)

    @covers("C-SB-01", "F-07")
    def test_validate_storyboard_coverage(self):
        """示例 storyboard 通过；有句未被任何镜覆盖 → 退出 5"""
        ex = self.require_path("assets/example")
        tl = ex / "timeline.fixture.json"
        p = self.cli("validate.py", "storyboard", ex / "storyboard.json", "--timeline", tl)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        sb = json.loads((ex / "storyboard.json").read_text())
        last = sb["sections"][-1]["shots"][-1]; dropped = last["line_ids"].pop()
        if not last["line_ids"]:
            sb["sections"][-1]["shots"].pop()
        d = self.tmpdir(); (d / "sb.json").write_text(json.dumps(sb))
        p = self.cli("validate.py", "storyboard", d / "sb.json", "--timeline", tl)
        self.assertEqual(p.returncode, 5, f"删掉句 {dropped} 的覆盖应失败")

    @covers("C-TL-01", "F-15", "F-05")
    def test_validate_timeline_mcp_fixture(self):
        """外部（MCP）工具产出的 timeline fixture 与脚本产出用同一 Schema：合法通过、非法失败"""
        good = FIXTURES / "mcp_timeline_good.json"; bad = FIXTURES / "mcp_timeline_bad.json"
        self.assertEqual(self.cli("validate.py", "timeline", good).returncode, 0)
        self.assertEqual(self.cli("validate.py", "timeline", bad).returncode, 5)

    @covers("C-AS-01", "F-08")
    def test_fetch_asset_unknown_license_rejected(self):
        """授权 unknown 的素材可登记但 usable=false、usage=rejected"""
        d = self.tmpdir(); man = d / "assets-manifest.json"
        p = self.cli("fetch_asset.py", "add", "--manifest", man, "--id", "A01", "--file", FIXTURES / "img_2000x1200.png",
                     "--content", "测试图", "--source-url", "https://example.com/a", "--source-name", "Example", "--license", "unknown",
                     "--aspect", "landscape", "--dest", d / "media")
        self.assertEqual(p.returncode, 0, p.stderr)
        e = [x for x in self._entries(man) if x["id"] == "A01"][0]
        self.assertFalse(e["usable"]); self.assertEqual(e["usage"], "rejected")

    def _entries(self, man):
        """Q-03：manifest 顶层只能是 {"version":1,"assets":[...]}"""
        data = json.loads(Path(man).read_text())
        self.assertIsInstance(data, dict, "assets-manifest.json 顶层必须是对象"); self.assertEqual(data.get("version"), 1)
        return data["assets"]

    @covers("C-AS-02", "F-08")
    def test_fetch_asset_usage_by_size(self):
        """横屏画布：短边 1200≥1080 → fullscreen；短边 600 → card-only；已登记字段齐全"""
        d = self.tmpdir(); man = d / "assets-manifest.json"
        for aid, f in (("A01", "img_2000x1200.png"), ("A02", "img_800x600.png")):
            p = self.cli("fetch_asset.py", "add", "--manifest", man, "--id", aid, "--file", FIXTURES / f, "--content", "c",
                         "--ai-generated", "--source-name", "AI 生成", "--license", "AI 生成", "--aspect", "landscape", "--dest", d / "media")
            self.assertEqual(p.returncode, 0, p.stderr)
        es = {e["id"]: e for e in self._entries(man)}
        self.assertEqual(es["A01"]["usage"], "fullscreen"); self.assertEqual(es["A02"]["usage"], "card-only")
        for e in es.values():
            for k in ("file", "content", "source", "source_name", "license", "needs_attribution", "opens", "usable"):
                self.assertIn(k, e)
            self.assertEqual(e["source"], "AI 生成")

    @covers("C-AS-03", "F-08")
    def test_fetch_asset_broken_file(self):
        """打不开的文件 → opens=false、usable=false"""
        d = self.tmpdir(); man = d / "assets-manifest.json"; bad = d / "broken.png"; bad.write_bytes(b"garbage")
        self.cli("fetch_asset.py", "add", "--manifest", man, "--id", "A09", "--file", bad, "--content", "c",
                 "--ai-generated", "--source-name", "AI 生成", "--license", "AI 生成", "--aspect", "landscape", "--dest", d / "media")
        e = [x for x in self._entries(man) if x["id"] == "A09"][0]
        self.assertFalse(e["opens"]); self.assertFalse(e["usable"])

    @covers("C-AS-04", "F-08", "NF-04")
    def test_credits_diff_cli(self):
        """credits-diff（Q-04，v1.3）：shot-badges.json / “素材署名：”段 [id] / deliverable.credits 三处齐全且无链接 → 0；任一处缺（简介按平台逐个，缺平台目录视为该平台全缺）、或任一平台 title/description、credits 含 URL → 7（v1.4）"""
        def run(slug): return self.cli("fetch_asset.py", "credits-diff", "--manifest", slug / "assets-manifest.json", "--slug-dir", slug)
        slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
        p = run(slug); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        # (a) 角标数据缺
        s1 = self.tmpdir() / "a"; shutil.copytree(FIXTURES / "credits_slug", s1)
        (s1 / "project/src/data/shot-badges.json").write_text("[]"); self.assertEqual(run(s1).returncode, 7)
        # (b) 简介署名段缺
        s2 = self.tmpdir() / "b"; shutil.copytree(FIXTURES / "credits_slug", s2)
        (s2 / "publish/bilibili/description.txt").write_text("简介正文，没有署名段。\n", encoding="utf-8"); self.assertEqual(run(s2).returncode, 7)
        s2b = self.tmpdir() / "b2"; shutil.copytree(FIXTURES / "credits_slug", s2b)
        shutil.rmtree(s2b / "publish/channels"); self.assertEqual(run(s2b).returncode, 7, "缺某平台目录 = 该平台署名全部缺失")
        # (c) deliverable.credits 缺
        s3 = self.tmpdir() / "c"; shutil.copytree(FIXTURES / "credits_slug", s3)
        d = json.loads((s3 / "deliverable.json").read_text()); d["credits"] = []
        (s3 / "deliverable.json").write_text(json.dumps(d, ensure_ascii=False)); self.assertEqual(run(s3).returncode, 7)
        # v1.3 U-3：三处齐全但 description 全文或 credits 任一字段含链接 → 7
        s4 = self.tmpdir() / "d"; shutil.copytree(FIXTURES / "credits_slug", s4)
        f4 = s4 / "publish/youtube/description.txt"; f4.write_text(f4.read_text() + "更多见 https://example.com\n", encoding="utf-8")
        self.assertEqual(run(s4).returncode, 7)
        s4b = self.tmpdir() / "d2"; shutil.copytree(FIXTURES / "credits_slug", s4b)
        (s4b / "publish/douyin/title.txt").write_text("署名测试 www.example.com", encoding="utf-8"); self.assertEqual(run(s4b).returncode, 7)
        s5 = self.tmpdir() / "e"; shutil.copytree(FIXTURES / "credits_slug", s5)
        d = json.loads((s5 / "deliverable.json").read_text()); d["credits"][0]["source_name"] = "commons.wikimedia.org"
        (s5 / "deliverable.json").write_text(json.dumps(d, ensure_ascii=False)); self.assertEqual(run(s5).returncode, 7)

    @covers("C-AS-05", "F-08", "NF-04")
    def test_prune(self):
        """fetch_asset.py prune（Q-04）：未被任何镜头 asset_ids 引用的条目置 usable=false；被引用的保持不变"""
        slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
        man = json.loads((slug / "assets-manifest.json").read_text())
        man["assets"].append({"id": "A04", "file": "media/a04.png", "kind": "image", "content": "未使用", "source": "https://x/y",
                              "license": "CC BY 4.0", "needs_attribution": True, "author": "王五", "source_name": "Y", "opens": True, "usage": "fullscreen", "usable": True})
        (slug / "assets-manifest.json").write_text(json.dumps(man, ensure_ascii=False))
        p = self.cli("fetch_asset.py", "prune", "--manifest", slug / "assets-manifest.json", "--storyboard", slug / "storyboard.json")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        es = {e["id"]: e for e in self._entries(slug / "assets-manifest.json")}
        self.assertFalse(es["A04"]["usable"]); self.assertTrue(es["A01"]["usable"]); self.assertTrue(es["A02"]["usable"])
        self.assertEqual(self.cli("fetch_asset.py", "credits-diff", "--manifest", slug / "assets-manifest.json", "--slug-dir", slug).returncode, 0)

    @covers("C-AS-06", "F-08")
    def test_no_render_md(self):
        """Q-03：不生成 assets-manifest.md，fetch_asset.py 没有 render-md 子命令（调用返回 2）"""
        self.assertEqual(self.cli("fetch_asset.py", "render-md", "--manifest", FIXTURES / "credits_slug/assets-manifest.json").returncode, 2)

    @covers("C-SCF-01", "F-09", "F-14")
    def test_scaffold_contract(self):
        """scaffold：生成工程含 AGENTS.md、src/theme/tokens.ts、src/data/job.ts、.gitignore(.env)；目录已存在且无 --force → 退出 2"""
        d = self.tmpdir(); job = d / "job.json"
        job.write_text(json.dumps({"topic": "t", "slug": "t", "aspect": "landscape", "width": 1920, "height": 1080, "fps": 30,
                                   "created_at": "2026-10-22T00:00:00+08:00"}))
        p = self.cli("scaffold_project.py", "--job", job, "--out", d / "project")
        self.assertEqual(p.returncode, 0, p.stderr)
        for f in ("AGENTS.md", "src/theme/tokens.ts", "src/data/job.ts", "package.json", "src/layout/presets.ts"):
            self.assertTrue((d / "project" / f).exists(), f)
        self.assertIn(".env", (d / "project" / ".gitignore").read_text().split())
        self.assertEqual(self.cli("scaffold_project.py", "--job", job, "--out", d / "project").returncode, 2)
        self.assertEqual(self.cli("validate.py", "tokens", "--json", SKILL_DIR / "assets/tokens.json",
                                  "--ts", d / "project/src/theme/tokens.ts").returncode, 0)

    @covers("C-TOK-01", "F-09", "NF-06")
    def test_validate_tokens_detects_mismatch(self):
        """tokens.ts 被手改与 tokens.json 不一致 → validate.py tokens 非 0（7）"""
        d = self.tmpdir(); job = d / "job.json"
        job.write_text(json.dumps({"topic": "t", "slug": "t", "aspect": "landscape", "width": 1920, "height": 1080, "fps": 30, "created_at": "2026-10-22T00:00:00+08:00"}))
        self.cli("scaffold_project.py", "--job", job, "--out", d / "p")
        self.require_path("assets/tokens.json"); ts = d / "p/src/theme/tokens.ts"
        if not ts.exists(): self.fail("scaffold 未生成 tokens.ts")
        ts.write_text(ts.read_text().replace("#070A0F", "#000000").replace("#070a0f", "#000000"))
        self.assertEqual(self.cli("validate.py", "tokens", "--json", SKILL_DIR / "assets/tokens.json", "--ts", ts).returncode, 7)

    @covers("C-PUB-01", "F-13", "F-08")
    def test_validate_publish_cli(self):
        """validate.py publish（v1.4）：合规 → 0；在每个平台的 description.txt 末尾补“素材署名：”段（幂等，每份恰好 1 个，行格式 - [id] 作者 · 来源名称 · 许可，无链接）；
        publish/check.json 通过 publish-check.schema.json，targets 与 platforms 为默认 5 个平台"""
        slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
        for pid in PLATS: (slug / f"publish/{pid}/description.txt").write_text("简介正文。\n", encoding="utf-8")
        p = self.cli("validate.py", "publish", slug); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.cli("validate.py", "publish", slug)
        for pid in PLATS:
            t = (slug / f"publish/{pid}/description.txt").read_text()
            self.assertEqual(t.count("素材署名："), 1, pid)
            self.assertRegex(t, r"(?m)^素材署名：\s*$"); self.assertRegex(t, r"(?m)^- \[A01\] 张三 · Wikimedia Commons · CC BY 4\.0\s*$")
            self.assertNotRegex(t, r"(?i)https?://|www\.|wikimedia\.org")
        chk = json.loads((slug / "publish/check.json").read_text())
        from py.support import load_json
        errs = self.libfn("schema_check", "validate")(chk, load_json(self.require_path("assets/schemas/publish-check.schema.json")))
        self.assertEqual(errs, [])
        self.assertIs(chk["ok"], True); self.assertEqual(sorted(chk["targets"]), sorted(PLATS))
        self.assertEqual(sorted(x["id"] for x in chk["platforms"]), sorted(PLATS))
        for x in chk["platforms"]:
            self.assertEqual(x["dir"], f"publish/{x['id']}")
            self.assertEqual(x["description"]["credits_missing"], [])
            self.assertIn("tags", x); self.assertIn(x["tags"]["rule"], ("platform", "nonempty_only"))   # v1.5
            self.assertEqual(x["tags"]["rule"], "nonempty_only" if x["id"] in ("xiaohongshu", "channels") else "platform")
        self.assertNotIn("tags", chk.get("shared", {}), "v1.5：去掉 shared.tags")

    @covers("C-PUB-02", "F-13")
    def test_validate_publish_cli_platform_rules(self):
        """逐平台判定：31 字标题写入 xiaohongshu/ → 7；同样写入 youtube/ → 0；B 站简介含署名段总长 250 → 7；
        只有 unofficial 不满足（视频号标题 4 字 <6）→ 0 且 check.json 中 channels.title.severity=warning"""
        def fresh():
            s = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", s); return s
        s1 = fresh(); (s1 / "publish/xiaohongshu/title.txt").write_text("字" * 31, encoding="utf-8")
        self.assertEqual(self.cli("validate.py", "publish", s1).returncode, 7)
        s1b = fresh(); (s1b / "publish/youtube/title.txt").write_text("字" * 31, encoding="utf-8")
        p = self.cli("validate.py", "publish", s1b); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        s2 = fresh(); f2 = s2 / "publish/bilibili/description.txt"; body = f2.read_text()
        f2.write_text("字" * (250 - len(body)) + body, encoding="utf-8")
        self.assertEqual(self.cli("validate.py", "publish", s2).returncode, 7, "署名段计入简介长度，总长 250 应超 B 站上限")
        s3 = fresh(); (s3 / "publish/channels/title.txt").write_text("一分钟看", encoding="utf-8")
        p = self.cli("validate.py", "publish", s3); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        chk = json.loads((s3 / "publish/check.json").read_text())
        ch = [x for x in chk["platforms"] if x["id"] == "channels"][0]
        self.assertEqual((ch["title"]["severity"], ch["title"]["status"]), ("warning", "unofficial")); self.assertTrue(ch["warnings"])
        self.assertIs(chk["ok"], True)

    @covers("C-PUB-05", "F-13", "NF-02")
    def test_validate_publish_cli_tags(self):
        """v1.5：B 站 tags 逗号连接总长 200 → 7；抖音 6 个标签 → 0 且 check.json 记 douyin 告警；任一平台 tags 含链接 → 7；缺 publish/<p>/tags.txt → 7"""
        def fresh():
            s = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", s); return s
        s1 = fresh(); (s1 / "publish/bilibili/tags.txt").write_text("字" * 99 + "\n" + "字" * 100, encoding="utf-8")
        self.assertEqual(self.cli("validate.py", "publish", s1).returncode, 7)
        s2 = fresh(); (s2 / "publish/douyin/tags.txt").write_text("\n".join(f"t{i}" for i in range(6)), encoding="utf-8")
        p = self.cli("validate.py", "publish", s2); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        dy = [x for x in json.loads((s2 / "publish/check.json").read_text())["platforms"] if x["id"] == "douyin"][0]
        self.assertEqual(dy["tags"]["severity"], "warning"); self.assertEqual(dy["tags"]["items"], 6)
        s3 = fresh(); (s3 / "publish/xiaohongshu/tags.txt").write_text("AI\nwww.example.com", encoding="utf-8")
        self.assertEqual(self.cli("validate.py", "publish", s3).returncode, 7)
        s4 = fresh(); (s4 / "publish/channels/tags.txt").unlink()
        self.assertEqual(self.cli("validate.py", "publish", s4).returncode, 7)

    @covers("C-PUB-03", "F-13", "NF-02")
    def test_validate_publish_cli_url(self):
        """任一平台 description.txt 或 title.txt 含链接 → validate.py publish 退出 7（v1.4）"""
        for rel, text in (("bilibili/description.txt", "简介，见 www.example.com\n"), ("youtube/title.txt", "看 https://a.com")):
            slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
            (slug / "publish" / rel).write_text(text, encoding="utf-8")
            self.assertEqual(self.cli("validate.py", "publish", slug).returncode, 7, rel)

    @covers("C-PUB-04", "F-13")
    def test_validate_publish_cli_job_platforms(self):
        """job.json.platforms 指定 ["bilibili"] 时只校验 bilibili：其他平台目录缺失也通过，check.json.targets == ["bilibili"]；未知平台 id → 非 0"""
        slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
        job = json.loads((slug / "job.json").read_text()); job["platforms"] = ["bilibili"]; (slug / "job.json").write_text(json.dumps(job, ensure_ascii=False))
        for pid in PLATS:
            if pid != "bilibili": shutil.rmtree(slug / "publish" / pid)
        p = self.cli("validate.py", "publish", slug); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads((slug / "publish/check.json").read_text())["targets"], ["bilibili"])
        job["platforms"] = ["kuaishou"]; (slug / "job.json").write_text(json.dumps(job, ensure_ascii=False))
        self.assertNotEqual(self.cli("validate.py", "publish", slug).returncode, 0)

    @covers("C-DLV-01", "F-16")
    def test_deliverable_fields(self):
        """validate.py deliverable 产出 deliverable.json，字段齐全（v1.4/v1.5：publish 按平台组织标题、简介、标签，替代顶层 title/description/tags）；credits 来自 manifest 需署名且可用项，字段为 {id, author, source_name, license}，不含 URL（v1.3）。缺 out/video.mp4 仍退出 0：摘要可先于成片（duration_s 可为 null，notes 提示缺成片）；成片存在性由 F-12 validate.py video / render 验收，本 fixture 故意无成片"""
        slug = self.tmpdir() / "demo"; shutil.copytree(FIXTURES / "credits_slug", slug)
        p = self.cli("validate.py", "deliverable", slug); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        d = json.loads((slug / "deliverable.json").read_text())
        for k in ("video", "duration_s", "aspect", "width", "height", "covers", "publish", "credits", "out_dir", "notes"):
            self.assertIn(k, d)
        for k in ("title", "description", "tags"):
            self.assertNotIn(k, d)   # v1.4 标题/简介、v1.5 标签均改放 publish.<platform>
        self.assertEqual(sorted(d["publish"]), sorted(PLATS), "publish 的键 = targets")
        for pid, v in d["publish"].items():
            self.assertEqual(set(v), {"title", "description", "tags", "title_path", "description_path", "tags_path", "warnings"}, pid)
            self.assertEqual(v["title_path"], f"publish/{pid}/title.txt"); self.assertIn("素材署名：", v["description"])
            self.assertEqual(v["tags_path"], f"publish/{pid}/tags.txt"); self.assertIsInstance(v["tags"], list); self.assertTrue(v["tags"], pid)
        self.assertEqual({c["id"] for c in d["credits"]}, {"A01"})
        for c in d["credits"]:
            self.assertEqual(set(c), {"id", "author", "source_name", "license"})
            for k in c: self.assertTrue(c[k], k)
        self.assertNotRegex(json.dumps(d["credits"], ensure_ascii=False), r"(?i)https?://|www\.|\.(com|cn|net|org|io|tv)\b")
        self.assertEqual(d["credits"][0]["source_name"], "Wikimedia Commons")

    def _leak_report(self, p):
        """validate.py leak 报告 {ok, real_key, hits}：取 stdout 末行 JSON 的顶层或 outputs"""
        lines = [l for l in p.stdout.strip().splitlines() if l.strip()]
        if not lines: self.fail("validate.py leak 无 stdout JSON")
        try: j = json.loads(lines[-1])
        except json.JSONDecodeError: self.fail(f"stdout 末行不是 JSON：{lines[-1][:120]}")
        r = j if "hits" in j else j.get("outputs", {})
        for k in ("real_key", "hits"):
            if k not in r: self.fail(f"leak 报告缺 {k}")
        return r

    @covers("C-LEAK-01", "NF-02", "F-17")
    def test_validate_leak(self):
        """RV-3：技能包 .env 写入真实 Key 样本，同值写入日志第 3 行 → 退出 7，hits == [{file, line:3, which:"real"}]（只报文件、行号、类别），
        stdout/stderr 全文不含该值，.env 本身不算命中；干净 → 0 且 real_key="checked"；测试假 Key 经 --extra-secret-file 传入，命中报 which="fake" """
        import uuid
        real = f"sk-real-{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"; fake = f"TEST-{uuid.uuid4()}"
        sd = self.copy_skill(key=real); self.assertIn(real, (sd / ".env").read_text())
        slug = self.tmpdir() / "demo"; (slug / "voice").mkdir(parents=True); log = slug / "voice/tts.log"
        sf = self.tmpdir() / "fake_key.txt"; sf.write_text(fake)
        log.write_text("line1\nline2\nline3\n")
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", sf, skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr); r = self._leak_report(p)
        self.assertEqual((r["real_key"], r["hits"]), ("checked", []))
        log.write_text(f"line1\nline2\nX-Api-Key: {real}\n")
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", sf, skill_dir=sd)
        self.assertEqual(p.returncode, 7); r = self._leak_report(p)
        self.assertEqual(len(r["hits"]), 1, r["hits"]); h = r["hits"][0]
        self.assertEqual(set(h), {"file", "line", "which"}); self.assertEqual((h["line"], h["which"]), (3, "real"))
        self.assertEqual(Path(h["file"]).resolve(), log.resolve())
        self.assertNotIn(".env", [Path(x["file"]).name for x in r["hits"]])
        blob = p.stdout + p.stderr
        self.assertNotIn(real, blob)
        for frag in (real[:12], real[-12:]): self.assertNotIn(frag, blob, "不得输出 Key 前后缀")
        log.write_text(f"a\n{fake}\n")
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", sf, skill_dir=sd)
        self.assertEqual(p.returncode, 7); r = self._leak_report(p)
        self.assertEqual([(x["line"], x["which"]) for x in r["hits"]], [(2, "fake")]); self.assertNotIn(fake, p.stdout + p.stderr)

    def _leak_env(self):
        sd = self.copy_skill(); slug = self.tmpdir() / "demo"; (slug / "voice").mkdir(parents=True)
        (slug / "voice/tts.log").write_text("ok\n"); return sd, slug

    @covers("C-LEAK-03", "NF-02")
    def test_leak_missing_secret_file_exit2(self):
        """V9-3：--extra-secret-file 指向不存在的文件 → 退出 2（修正调用）；--extra-secret-file 与 --scan 可重复传入，全部合法时 → 0"""
        sd, slug = self._leak_env(); d = self.tmpdir()
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", d / "nope.txt", skill_dir=sd)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        f1 = d / "k1.txt"; f1.write_text("TEST-11111111-1111-4111-8111-111111111111"); f2 = d / "k2.txt"; f2.write_text("TEST-22222222-2222-4222-8222-222222222222")
        s1 = d / "a.jsonl"; s1.write_text("{}\n"); s2 = d / "b.log"; s2.write_text("x\n")
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", f1, "--extra-secret-file", f2,
                     "--scan", s1, "--scan", s2, skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        s2.write_text("x\nTEST-22222222-2222-4222-8222-222222222222\n")   # 第 2 个密钥出现在第 2 个 --scan 文件 → 两次重复参数都生效
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", f1, "--extra-secret-file", f2,
                     "--scan", s1, "--scan", s2, skill_dir=sd)
        self.assertEqual(p.returncode, 7, p.stdout + p.stderr)

    @covers("C-LEAK-04", "NF-02")
    def test_leak_missing_scan_exit2(self):
        """V9-3：--scan 指定的文件不存在 → 退出 2（不得静默跳过）"""
        sd, slug = self._leak_env()
        p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--scan", self.tmpdir() / "missing.jsonl", skill_dir=sd)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)

    @covers("C-LEAK-05", "NF-02")
    def test_leak_bad_secret_content_exit5(self):
        """V9-3：--extra-secret-file 可读但为空（含只有空白）或非 UTF-8 → 退出 5"""
        sd, slug = self._leak_env(); d = self.tmpdir()
        for name, data in (("empty.txt", b""), ("blank.txt", b"  \n"), ("latin.txt", b"\xff\xfe\xfa bad")):
            f = d / name; f.write_bytes(data)
            p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, "--extra-secret-file", f, skill_dir=sd)
            self.assertEqual(p.returncode, 5, (name, p.stdout + p.stderr))

    @covers("C-LEAK-06", "NF-02")
    def test_leak_bad_args_exit2(self):
        """V9-3 + v1.10 §4.0（allow_abbrev=False）：参数拼错（--extra-secrets-file / --scna / --skilldir）、前缀缩写（--extra-secret / --extra / --sca / --skill）、缺 slug、slug 不存在 → 一律退出 2；缩写时 stderr 指出该参数"""
        sd, slug = self._leak_env(); f = self.tmpdir() / "k.txt"; f.write_text("TEST-x")
        for args in (["--extra-secret", f], ["--extra", f], ["--sca", f], ["--skill", sd]):
            p = self.cli("validate.py", "leak", slug, *args, skill_dir=sd); self.assertEqual(p.returncode, 2, (args, p.stdout + p.stderr))
            self.assertIn(str(args[0]), p.stderr, args)
        for args in (["--extra-secrets-file", f], ["--scna", f], ["--skilldir", sd]):
            p = self.cli("validate.py", "leak", slug, *args, skill_dir=sd); self.assertEqual(p.returncode, 2, (args, p.stderr))
        self.assertEqual(self.cli("validate.py", "leak", "--skill-dir", sd, skill_dir=sd).returncode, 2)
        self.assertEqual(self.cli("validate.py", "leak", self.tmpdir() / "no-slug", "--skill-dir", sd, skill_dir=sd).returncode, 2)

    @covers("C-LEAK-02", "NF-02", "F-17")
    def test_validate_leak_env_absent(self):
        """RV-3：技能包 .env 不存在或 Key 为空 → real_key="absent"，不判失败（退出 0），且不读环境变量里的 Key"""
        import os
        for mode in ("missing", "empty"):
            sd = self.copy_skill(with_env=False); envp = sd / ".env"
            if envp.exists(): envp.unlink()
            if mode == "empty": envp.write_text("DOUBAO_TTS_API_KEY=\n")
            slug = self.tmpdir() / "demo"; (slug / "voice").mkdir(parents=True); (slug / "voice/tts.log").write_text("x\nENVKEY-abc123\n")
            p = self.cli("validate.py", "leak", slug, "--skill-dir", sd, skill_dir=sd,
                         env=dict(os.environ, DOUBAO_TTS_API_KEY="ENVKEY-abc123"))
            self.assertEqual(p.returncode, 0, (mode, p.stdout + p.stderr)); r = self._leak_report(p)
            self.assertEqual((r["real_key"], r["hits"]), ("absent", []), mode)

    @covers("C-TTS-09", "F-05")
    def test_tts_cli_max_attempts(self):
        """tts_doubao.py --max-attempts 上限 3（Q-17）：传 4 → 退出 2；旧参数 --retries 不再接受（退出 2）"""
        sd = self.copy_skill(); s = self.require_path("assets/example/script.md")
        self.assertEqual(self.cli("tts_doubao.py", s, "--out-dir", self.tmpdir(), "--max-attempts", "4", "--dry-run", skill_dir=sd).returncode, 2)
        self.assertEqual(self.cli("tts_doubao.py", s, "--out-dir", self.tmpdir(), "--retries", "3", "--dry-run", skill_dir=sd).returncode, 2)
        self.assertEqual(self.cli("tts_doubao.py", s, "--out-dir", self.tmpdir(), "--max-attempts", "3", "--dry-run", skill_dir=sd).returncode, 0)

    @covers("C-AS-07", "F-08")
    def test_fetch_asset_author_source_name(self):
        """v1.3：add 用 --author 与 --source-name 记录 author、source_name（source 仍留 URL）；旧参数 --attribution 退出 2"""
        d = self.tmpdir(); man = d / "assets-manifest.json"
        p = self.cli("fetch_asset.py", "add", "--manifest", man, "--id", "A05", "--file", FIXTURES / "img_2000x1200.png", "--content", "c",
                     "--source-url", "https://commons.wikimedia.org/wiki/File:X.png", "--license", "CC BY 4.0",
                     "--source-name", "Wikimedia Commons", "--author", "张三", "--aspect", "landscape", "--dest", d / "media")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        e = [x for x in self._entries(man) if x["id"] == "A05"][0]
        self.assertEqual((e["author"], e["source_name"]), ("张三", "Wikimedia Commons"))
        self.assertTrue(e["source"].startswith("https://")); self.assertNotIn("attribution", e)
        p = self.cli("fetch_asset.py", "add", "--manifest", man, "--id", "A06", "--file", FIXTURES / "img_2000x1200.png", "--content", "c",
                     "--source-url", "https://x.org/y", "--license", "CC BY 4.0", "--attribution", "李四", "--aspect", "landscape", "--dest", d / "media")
        self.assertEqual(p.returncode, 2)
