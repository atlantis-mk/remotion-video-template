"""L1 单元：lib/render_ts.py、lib/render_md.py、lib/job.py（F-06、F-09、F-10、F-14、NF-06）；签名按架构 v1.2 §7.5"""
import json, re
from py.support import SkillTestCase, covers, load_json

PORTRAIT_WORDS = ["竖屏"]      # v1.3 U-1（用户已决定）：只认这两个词
LANDSCAPE_WORDS = ["横屏"]
PLATFORM_NAMES = ["抖音", "视频号", "小红书", "快手", "B站", "TikTok", "YouTube Shorts", "Instagram Reels"]

def layout_keywords(tc):
    """LAYOUT.md 机读块 {"portrait_keywords":["竖屏"],"landscape_keywords":["横屏"]}，返回 resolve_aspect 所需的 kw。"""
    t = tc.require_path("references/LAYOUT.md").read_text(encoding="utf-8")
    blocks = re.findall(r"^```json[ \t]*\n(.*?)^```", t, re.S | re.M)   # R-06：恰好一个 json 块
    if len(blocks) != 1: tc.fail(f"references/LAYOUT.md 应恰好 1 个 json 块，实际 {len(blocks)} 个")
    try: d = json.loads(blocks[0])
    except json.JSONDecodeError as e: tc.fail(f"LAYOUT.md json 块无法解析：{e}")
    if not isinstance(d, dict) or "portrait_keywords" not in d or "landscape_keywords" not in d:
        tc.fail("LAYOUT.md json 块缺 portrait_keywords / landscape_keywords")
    return d

def kw_arg(d):
    return {"portrait": d["portrait_keywords"], "landscape": d["landscape_keywords"]}

class TestRenderers(SkillTestCase):
    @covers("U-RD-01", "F-09", "NF-06")
    def test_render_tokens_ts_contains_all_colors(self):
        """render_tokens_ts：tokens.json 中每个色值都出现在输出中；改一个色值输出随之改变"""
        f = self.libfn("render_ts", "render_tokens_ts")
        tokens = load_json(self.require_path("assets/tokens.json"))
        ts = f(tokens)
        colors = {c.lower() for c in re.findall(r"#[0-9A-Fa-f]{6}", json.dumps(tokens))}
        self.assertIn("#070a0f", colors)
        for c in colors:
            self.assertIn(c, ts.lower())
        t2 = json.loads(json.dumps(tokens).replace("#070A0F", "#010203").replace("#070a0f", "#010203"))
        self.assertIn("#010203", f(t2).lower()); self.assertNotIn("#070a0f", f(t2).lower())

    @covers("U-RD-02", "F-14")
    def test_render_agents_md_sections(self):
        """render_agents_md(ctx)：含安装/预览/渲染/自检命令和两条约定"""
        f = self.libfn("render_md", "render_agents_md")
        md = f({"slug": "demo", "skill_dir": "/work/.agents/skills/remotion-infographic-video", "project_dir": "/work/demo/project"})
        for s in ("npm ci", "npx remotion studio", "render.sh", "npm run check", ".env"):
            self.assertIn(s, md)
        self.assertRegex(md, r"风格以技能包\s*references\s*为准")
        self.assertIn("不提交密钥", md)

    @covers("U-RD-03", "F-06")
    def test_render_timeline_ts_total_frames_computed(self):
        """render_timeline_ts：TOTAL_FRAMES = sec_to_frame(audio_seconds)，最后一段 to == TOTAL_FRAMES；无 CREDITS"""
        f = self.libfn("render_ts", "render_timeline_ts")
        tl = {"audio_seconds": 10.02, "lines": [
            {"id": "01", "section": "S01", "start": 0, "end": 4.0, "duration_s": 4.0},
            {"id": "02", "section": "S02", "start": 4.0, "end": 10.02, "duration_s": 6.02}]}
        sb = {"version": 1, "aspect": "landscape", "sections": [
            {"id": "S01", "title": "a", "palette": {"a": "gold", "b": "blue"}, "transition": "wipe",
             "shots": [{"shot_no": 1, "line_ids": ["01"], "description": "d", "component": "SlamTitle", "entrance": "push"}]},
            {"id": "S02", "title": "b", "palette": {"a": "green", "b": "blue"}, "transition": "zoom",
             "shots": [{"shot_no": 2, "line_ids": ["02"], "description": "d", "component": "GlassPanel", "entrance": "rise"}]}]}
        ts = f(tl, sb, fps=30)
        self.assertRegex(ts, r"TOTAL_FRAMES\s*=\s*301\b"); self.assertRegex(ts, r"FPS\s*=\s*30\b")
        self.assertNotRegex(ts, r"(?i)credits")
        self.assertIn(301, [int(x) for x in re.findall(r"\bto:\s*(\d+)", ts)])

    @covers("U-RD-04", "F-10")
    def test_layout_keyword_table(self):
        """LAYOUT.md 关键词表恰好为 {portrait_keywords:["竖屏"], landscape_keywords:["横屏"]}（v1.3 U-1，不含平台名）"""
        d = layout_keywords(self)
        self.assertEqual(d.get("version"), 1); self.assertEqual(d.get("portrait_keywords"), PORTRAIT_WORDS); self.assertEqual(d.get("landscape_keywords"), LANDSCAPE_WORDS)

    @covers("U-RD-05", "F-10")
    def test_resolve_aspect_words(self):
        """resolve_aspect(topic, kw)：只含“竖屏”→portrait；只含“横屏”或都没有→landscape"""
        f = self.libfn("job", "resolve_aspect"); kw = kw_arg(layout_keywords(self))
        self.assertEqual(f("DeepSeek 估值，竖屏", kw), "portrait")
        self.assertEqual(f("聊聊英伟达财报，横屏", kw), "landscape")
        self.assertEqual(f("DeepSeek 为什么值五千亿", kw), "landscape")

    @covers("U-RD-06", "F-10")
    def test_resolve_aspect_platform_names_ignored(self):
        """只提平台名（抖音/视频号/小红书/快手/B站/TikTok…）→ landscape；“竖版”“9:16”等非关键词也不切竖屏"""
        f = self.libfn("job", "resolve_aspect"); kw = kw_arg(layout_keywords(self))
        for w in PLATFORM_NAMES + ["竖版", "9:16"]:
            self.assertEqual(f(f"做一条{w}：AI 芯片", kw), "landscape", w)
        self.assertEqual(f("做一条抖音，竖屏：AI 芯片", kw), "portrait")

    @covers("U-RD-07", "F-10")
    def test_resolve_aspect_last_word_wins(self):
        """“横屏”“竖屏”同时出现时取最后出现的那个（A-23）"""
        f = self.libfn("job", "resolve_aspect"); kw = kw_arg(layout_keywords(self))
        self.assertEqual(f("先做横屏，再改成竖屏", kw), "portrait")
        self.assertEqual(f("竖屏不好看，还是横屏", kw), "landscape")
