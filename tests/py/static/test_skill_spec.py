"""L4 静态规范检查（F-01、F-02、F-06、F-09、F-10、F-13、F-14、F-15、F-17、NF-01、NF-02、NF-05、NF-08；含 v1.11 A-28 仓库根 AGENTS.md）"""
import json, re, shutil, subprocess, tempfile
from pathlib import Path
from py.support import SkillTestCase, covers, SKILL_DIR, FAKE_KEY, REPO_DIR

SKILL_FILES = ["SKILL.md", ".env.example", ".gitignore",
    "scripts/tts_doubao.py", "scripts/scaffold_project.py", "scripts/build_timeline.py", "scripts/fetch_asset.py",
    "scripts/check_project.sh", "scripts/render.sh",
    *[f"references/{n}.md" for n in ("STYLE", "MOTION", "COMPONENTS", "LAYOUT", "VOICE", "SCRIPT", "ASSETS", "PUBLISH")],
    "assets/project-template", "assets/fonts", "assets/tokens.json", "assets/example", "assets/schemas"]
COLOR = re.compile(r"#[0-9A-Fa-f]{6}\b")
UPLOAD = re.compile(r"(upload|publish_video|douyin\.com|open\.douyin|bilibili\.com/x/|member\.bilibili|xiaohongshu\.com/api|channels\.weixin|youtube\.com/upload|googleapis\.com/upload)", re.I)

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, text)

def simple_yaml(fm):
    out = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m: out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out

def rg(pattern, path, *extra):
    if not shutil.which("rg"):
        raise AssertionError("环境缺少 rg")
    p = subprocess.run(["rg", "-n", *extra, pattern, str(path)], capture_output=True, text=True)
    return p.stdout.strip()


CANVAS = {1080, 1440, 1920}
_NUM = re.compile(r"(?<![\w.])(0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|(?:\d[\d_]*)?\.?\d[\d_]*(?:[eE][+-]?\d+)?)n?(?![\w])")
def _val(tok):
    t = tok.replace("_", "")
    try:
        if t[:2].lower() == "0x": return int(t, 16)
        if t[:2].lower() == "0o": return int(t, 8)
        if t[:2].lower() == "0b": return int(t, 2)
        return float(t)
    except ValueError: return None
def canvas_literals(line):
    """返回该行中值等于 1080/1440/1920 的数字字面量（含分隔符、进制、小数/指数）与“字面量 * 字面量”乘积"""
    out = []
    for m in _NUM.finditer(line):
        v = _val(m.group(1))
        if v is not None and v in CANVAS: out.append(m.group(0))
    for m in re.finditer(r"(?<![\w.])([0-9][0-9_.xXa-fA-FoObBeE]*)\s*\*\s*([0-9][0-9_.xXa-fA-FoObBeE]*)(?![\w.])", line):
        a, b = _val(m.group(1)), _val(m.group(2))
        if a is not None and b is not None and a * b in CANVAS: out.append(m.group(0))
    for m in re.finditer(r"(?<!\d)(1080|1440|1920)(?!\d)", line):   # 字符串、注释、拼接中的裸数字
        if m.group(1) not in out: out.append(m.group(1))
    return out

JSON_BLOCK = re.compile(r"^```json[ \t]*\n(.*?)^```", re.S | re.M)
def only_json_block(tc, rel):
    """R-06：rel 中恰好一个 ```json 代码块；取它 json.loads（失败 → FAIL）"""
    t = tc.require_path(rel).read_text(encoding="utf-8")
    blocks = JSON_BLOCK.findall(t)
    if len(blocks) != 1: tc.fail(f"{rel} 应恰好 1 个 ```json 块，实际 {len(blocks)} 个")
    try: return t, json.loads(blocks[0])
    except json.JSONDecodeError as e: tc.fail(f"{rel} 的 json 块无法解析：{e}")

class TestSkillSpec(SkillTestCase):
    def skill_md(self):
        return self.require_path("SKILL.md").read_text(encoding="utf-8")

    @covers("S-SK-01", "F-01")
    def test_layout_files_exist(self):
        """PRD 3.2 / 架构 v1.11：技能包内目录结构全部存在（技能根 = .agents/skills/remotion-infographic-video/）"""
        missing = [f for f in SKILL_FILES if not (SKILL_DIR / f).exists()]
        self.assertEqual(missing, [], f"缺少：{missing}")

    @covers("S-SK-02", "F-01")
    def test_skills_ref_validate(self):
        """skills-ref validate 通过（Q-16）：CLI 名 skills-ref 或 agentskills（PyPI skills-ref==0.1.1）均可，找不到 CLI 时调 skills_ref.validate()；先运行 tools/install_skills_ref.sh 安装到 tests/.venv"""
        self.require_path("SKILL.md")
        venv_bin = Path(__file__).resolve().parents[2] / ".venv" / "bin"
        for name in ("skills-ref", "agentskills"):
            exe = shutil.which(name) or (str(venv_bin / name) if (venv_bin / name).exists() else None)
            if exe:
                p = subprocess.run([exe, "validate", str(SKILL_DIR)], capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr); return
        py = venv_bin / "python"
        if py.exists():
            code = "import sys,pathlib,skills_ref as s; r=s.validate(pathlib.Path(sys.argv[1])); sys.exit(1 if r else 0)"
            p = subprocess.run([str(py), "-c", code, str(SKILL_DIR)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr); return
        self.fail("未安装 skills-ref：请先运行 bash tests/tools/install_skills_ref.sh（PyPI skills-ref==0.1.1，Python ≥3.11）")

    @covers("S-SK-03", "F-01")
    def test_frontmatter_name_description(self):
        """name 小写/数字/连字符 ≤64 且 = 目录名；description ≤1024 且含“开始制作”“口播”“横屏”“竖屏”"""
        fm, _ = frontmatter(self.skill_md()); self.assertIsNotNone(fm, "缺 YAML 前置元数据")
        y = simple_yaml(fm)
        self.assertRegex(y.get("name", ""), r"^[a-z0-9]+(-[a-z0-9]+)*$"); self.assertLessEqual(len(y["name"]), 64)
        self.assertEqual(y["name"], SKILL_DIR.name)
        d = y.get("description", ""); self.assertTrue(d); self.assertLessEqual(len(d), 1024)
        for kw in ("开始制作", "口播", "横屏", "竖屏"):
            self.assertIn(kw, d)

    @covers("S-SK-04", "F-01", "NF-08")
    def test_skill_md_lines(self):
        """SKILL.md < 500 行"""
        self.assertLess(len(self.skill_md().splitlines()), 500)

    @covers("S-SK-05", "F-01")
    def test_references_one_level_and_exist(self):
        """SKILL.md 中所有相对文件引用为一层深（目录/文件），且文件存在"""
        _, body = frontmatter(self.skill_md())
        refs = set(re.findall(r"\]\(([^)#\s]+)\)", body)) | set(re.findall(r"`((?:scripts|references|assets)/[^`\s]+)`", body))
        refs = {r for r in refs if not re.match(r"^[a-z]+://", r)}
        self.assertTrue(refs, "SKILL.md 未引用任何 references/ 或 scripts/ 文件")
        for r in refs:
            parts = Path(r.rstrip("/")).parts
            self.assertFalse(r.startswith("/") or ".." in parts, r)
            self.assertLessEqual(len(parts), 2, f"引用超过一层深：{r}")
            self.assertTrue((SKILL_DIR / r).exists(), f"引用不存在：{r}")
        self.assertNotIn("scripts/lib/", body)

    @covers("S-SK-06", "F-02")
    def test_skill_md_tokens(self):
        """SKILL.md 正文（去前置元数据）< 5000 tokens（Q-07）：tiktoken cl100k_base；无法导入时用上界估算 CJK字符×2 + 其他字符÷3"""
        _, body = frontmatter(self.skill_md())
        try:
            import tiktoken; n = len(tiktoken.get_encoding("cl100k_base").encode(body))
        except Exception:
            cjk = len(re.findall(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]", body))
            n = cjk * 2 + (len(body) - cjk) / 3
        self.assertLess(n, 5000)

    @covers("S-SK-07", "F-02")
    def test_no_values_in_skill_md(self):
        """SKILL.md 除 #070A0F 外不得出现任何 #[0-9A-Fa-f]{3,8} 色值及 rgb(/hsl(（Q-07）；不含组件 props 定义、TTS 参数"""
        t = self.skill_md()
        colors = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{3,8}\b", t)}
        self.assertTrue(colors <= {"#070A0F"}, colors)
        self.assertNotRegex(t, r"(?i)\b(rgba?|hsla?)\(")
        for bad in (r"loudnorm=", r"seed-tts-2\.0", r"damping\s*[:=]\s*\d", r"stiffness\s*[:=]\s*\d", r"React\.FC<"):
            self.assertNotRegex(t, bad)

    @covers("S-SK-08", "F-15")
    def test_skill_md_mcp_statement(self):
        """SKILL.md 写明：有同等输入输出的 MCP 配音工具可用，否则运行 scripts/tts_doubao.py，两者 timeline 用同一 Schema"""
        t = self.skill_md()
        self.assertIn("MCP", t); self.assertIn("tts_doubao.py", t); self.assertIn("timeline.json", t)
        self.assertRegex(t, r"(同一|同一份).{0,20}Schema|schemas/")

    @covers("S-SK-09", "F-03", "F-16", "F-17")
    def test_skill_md_required_sections(self):
        """SKILL.md 含：只问选题（默认横屏 1920×1080）、前置 .env 检查、固定步骤 0–9、禁止事项（不发布/不泄露 Key）、交付清单"""
        t = self.skill_md()
        for s in ("选题", ".env", "DOUBAO_TTS_API_KEY", "交付", "不发布"):
            self.assertIn(s, t)
        self.assertRegex(t, r"1920\s*[×x]\s*1080"); self.assertRegex(t, r"1080\s*[×x]\s*1440")  # v1.3 竖屏 3:4
        for n in range(0, 10):
            self.assertRegex(t, rf"(^|\n)\s*(#+\s*)?(步骤\s*)?{n}[\.、．:：)]", f"缺步骤 {n}")

    @covers("S-SK-10", "NF-08")
    def test_references_line_limit(self):
        """references/ 每个文件 ≤ 300 行"""
        ref = self.require_path("references")
        files = list(ref.glob("*.md")); self.assertEqual(len(files), 8, [f.name for f in files])
        for f in files:
            self.assertLessEqual(len(f.read_text(encoding="utf-8").splitlines()), 300, f.name)

    @covers("S-ENV-01", "F-17", "NF-02")
    def test_env_example_and_gitignore(self):
        """.env.example 含 DOUBAO_TTS_API_KEY= 且值为空；.gitignore 含 .env；技能包不分发 .env"""
        ex = self.require_path(".env.example").read_text()
        self.assertRegex(ex, r"(?m)^DOUBAO_TTS_API_KEY=\s*$")
        self.assertIn("DOUBAO_SPEAKER", ex)
        self.assertIn(".env", [l.strip() for l in self.require_path(".gitignore").read_text().splitlines()])

    @covers("S-ENV-02", "F-17", "NF-02")
    def test_git_check_ignore(self):
        """在技能包 git 仓库中：git check-ignore .env 命中；git ls-files 不含 .env"""
        sd = self.copy_skill()
        run = lambda *a: subprocess.run(["git", *a], cwd=sd, capture_output=True, text=True)
        run("init", "-q"); run("add", "-A")
        self.assertEqual(run("check-ignore", ".env").returncode, 0)
        self.assertNotIn(".env", run("ls-files").stdout.split())

    @covers("S-ENV-03", "F-17")
    def test_key_only_from_dotenv(self):
        """脚本不从进程环境变量读取 Key（禁止 os.environ/getenv 读 DOUBAO_TTS_API_KEY）"""
        self.require_path("scripts")
        self.assertEqual(rg(r"(environ|getenv)[^\n]*DOUBAO_TTS_API_KEY", SKILL_DIR / "scripts"), "")

    @covers("S-PUB-01", "F-13", "NF-02")
    def test_no_upload_calls(self):
        """scripts/ 与 project-template 不含任何平台上传/发布接口"""
        self.require_path("scripts")
        hits = rg(UPLOAD.pattern, SKILL_DIR / "scripts", "-i") + rg(UPLOAD.pattern, self.require_path("assets/project-template/src"), "-i")
        self.assertEqual(hits, "")

    @covers("S-AUTO-01", "NF-01")
    def test_no_interactive_input(self):
        """scripts/ 中无交互读取（input()、read -p、sys.stdin.readline）"""
        self.require_path("scripts")
        self.assertEqual(rg(r"\binput\(|read\s+-p|stdin\.readline", SKILL_DIR / "scripts"), "")

    @covers("S-DUR-01", "F-06")
    def test_no_hardcoded_duration(self):
        """project-template 中 durationInFrames= 只取计算值 TOTAL_FRAMES/变量，不含数字字面量；无 CREDITS 帧/尾静音参数"""
        src = self.require_path("assets/project-template/src")
        self.assertEqual(rg(r"durationInFrames=\{?\s*\d", src), "")
        self.assertEqual(rg(r"CREDITS|tail[_-]?silence|pad[_-]?silence", src, "-i"), "")
        self.assertEqual(rg(r"tail[_-]?silence|apad|pad[_-]?silence", SKILL_DIR / "scripts", "-i"), "")

    @covers("S-LAY-01", "F-10")
    def test_no_hardcoded_canvas(self):
        """画布尺寸 1080/1440/1920 只允许出现在 src/layout/presets.ts（v1.3）。v1.11：豁免只针对这一个文件（Python 遍历，不再依赖 rg glob）；
        其他文件中任何写法都判失败——十进制、数字分隔符（1_920）、小数/指数（1920.0、1.92e3）、十六进制/八进制/二进制（0x780）、
        字符串内数字、两个数字字面量相乘（960 * 2、192*10）；presets.ts 自身须用普通十进制写出 1920、1080、1440（不得用分隔符等变形），且无 9:16 竖屏"""
        src = self.require_path("assets/project-template/src")
        pre = src / "layout/presets.ts"; self.assertTrue(pre.exists())
        hits = []
        for f in sorted(src.rglob("*")):
            if not f.is_file() or f.suffix not in (".ts", ".tsx", ".js", ".jsx", ".json", ".css") or f.resolve() == pre.resolve(): continue
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                bad = canvas_literals(line)
                if bad: hits.append(f"{f.relative_to(src)}:{i}: {bad}")
        self.assertEqual(hits, [], "presets.ts 以外出现画布尺寸")
        pt = pre.read_text(encoding="utf-8")
        for n in ("1920", "1080", "1440"):
            self.assertRegex(pt, rf"(?<![\w.]){n}(?![\w.])", f"presets.ts 须用普通十进制写出 {n}")
        self.assertEqual(re.findall(r"\b\d+(?:_\d+)+\b", pt), [], "presets.ts 不得用数字分隔符等变形写尺寸")
        self.assertNotRegex(pt, r"width:\s*1080\s*,\s*height:\s*1920")

    @covers("S-DET-01", "NF-05")
    def test_no_math_random(self):
        """project-template 与 example/scenes 中不出现 Math.random / Date.now"""
        for p in ("assets/project-template/src", "assets/example/scenes"):
            self.assertEqual(rg(r"Math\.random|Date\.now\(", self.require_path(p)), "")

    @covers("S-LAY-02", "F-09")
    def test_three_layers_only(self):
        """project-template 只有 Background/HUD/Subtitle 三层：rg Credits src/ 无结果（PRD F-09 原文；v1.4 删除 Q-13④ 的大小写不敏感扩展）"""
        src = self.require_path("assets/project-template/src")
        self.assertEqual(rg("Credits", src), "")
        for layer in ("BackgroundLayer", "HUDLayer", "SubtitleLayer"):
            self.assertTrue(rg(layer, src), layer)

    @covers("S-CMP-01", "F-09")
    def test_component_registry_14(self):
        """components/ 含架构 §4.12 清单列出的全部组件文件（清单实际列了 15 个名字，见歧义 Q-05）"""
        comp = self.require_path("assets/project-template/src/components")
        names = ["GlassPanel", "Split", "Shot", "SectionTransition", "SlamTitle", "ImpactShake", "KeywordPulse", "StepList",
                 "NumberRoll", "CompareBars", "SourceBadge", "IllustrativeTag", "MediaCard", "FollowCTA", "HoldFade"]
        missing = [n for n in names if not list(comp.rglob(f"{n}.tsx"))]
        self.assertEqual(missing, [])

    @covers("S-VER-01", "F-09")
    def test_remotion_version_locked(self):
        """project-template/package.json 锁定 remotion 4.0.537，devDeps 含 typescript、vitest、ajv"""
        pkg = json.loads(self.require_path("assets/project-template/package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        self.assertEqual(deps.get("remotion"), "4.0.537")
        for k in ("typescript", "vitest", "ajv"):
            self.assertIn(k, pkg.get("devDependencies", {}))

    @covers("S-FNT-01", "F-09")
    def test_fonts_ofl(self):
        """assets/fonts 含 NotoSansSC Regular/Bold、JetBrainsMono 及 OFL 许可文本"""
        f = self.require_path("assets/fonts"); names = " ".join(p.name for p in f.rglob("*"))
        for k in ("NotoSansSC", "JetBrainsMono", "OFL"):
            self.assertIn(k.lower(), names.lower())

    @covers("S-EX-01", "F-07", "F-09")
    def test_example_files(self):
        """assets/example 含 script.md、sources.md、storyboard.json、timeline.fixture.json、scenes/"""
        ex = self.require_path("assets/example")
        for f in ("script.md", "sources.md", "storyboard.json", "timeline.fixture.json", "scenes"):
            self.assertTrue((ex / f).exists(), f)

    @covers("S-CPY-01", "F-01", "F-17")
    def test_copy_and_run_without_install(self):
        """复制即用：复制到临时目录 + 假 Key，不执行任何 pip/uv 安装即可跑 check_env.py 与 tts_doubao.py --dry-run"""
        sd = self.copy_skill()
        self.assertEqual(self.cli("check_env.py", "--skill-dir", sd, skill_dir=sd).returncode, 0)
        p = self.cli("tts_doubao.py", sd / "assets/example/script.md", "--out-dir", self.tmpdir(), "--dry-run", skill_dir=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(rg(r"^\s*(import|from)\s+(requests|jsonschema|pydantic|yaml|numpy)\b", sd / "scripts"), "")

    @covers("S-PUB-02", "F-13")
    def test_publish_md_platform_table(self):
        """R-06：PUBLISH.md 恰好一个 json 块，顶层 {version:1, default_targets, platforms:{<id>: rule}}，通过 assets/schemas/platforms.schema.json；
        不再出现 title_max_chars；恰好 5 个平台；default_targets 为全部 5 个（v1.4）；写明封面尺寸 1920×1080 / 1080×1440"""
        t, table = only_json_block(self, "references/PUBLISH.md")
        self.assertIsInstance(table, dict); self.assertEqual(table.get("version"), 1)
        self.assertIsInstance(table.get("platforms"), dict, "R-06：platforms 为以平台 id 为键的对象")
        self.assertNotIn("title_max_chars", t, "R-06：title_max_chars 已废弃")
        errs = self.libfn("schema_check", "validate")(table, json.loads(self.require_path("assets/schemas/platforms.schema.json").read_text()))
        self.assertEqual(errs, [])
        ids = list(table["platforms"])
        self.assertEqual(sorted(ids), sorted(["douyin", "bilibili", "xiaohongshu", "channels", "youtube"]))
        self.assertEqual(table.get("default_targets"), ["douyin", "bilibili", "xiaohongshu", "channels", "youtube"])   # v1.4 A-25
        self.assertRegex(t, r"1920\s*[×x]\s*1080"); self.assertRegex(t, r"1080\s*[×x]\s*1440")
        self.assertNotRegex(t, r"1080\s*[×x]\s*1920", "v1.3：竖屏封面只出 1080×1440")

    @covers("S-PUB-03", "F-13")
    def test_publish_md_platform_values(self):
        """平台规范表数值与 arch-QA v1.3 §U-2 一致：官方——B 站标题 <80、简介 <250；小红书标题 20、简介 1000（cjk1_ascii_half）；YouTube 标题 100、简介 5000（utf8_bytes）；非官方——抖音 30/1000、视频号 6–16/1000；标签（v1.5）——B 站逗号连接 <200、YouTube ≤500（youtube_tags）官方，抖音 ≤5 个非官方，小红书/视频号无规则"""
        t, table = only_json_block(self, "references/PUBLISH.md")
        P = table.get("platforms") if isinstance(table, dict) else None
        if not isinstance(P, dict): self.fail("R-06：platforms 应为以平台 id 为键的对象")
        P = {k: dict(v, id=k) for k, v in P.items()}
        def lim(rule, strict_key=True):  # 返回“允许的最大值”
            return rule["max"] - 1 if rule.get("strict_less_than") else rule["max"]
        self.assertEqual((lim(P["bilibili"]["title"]), P["bilibili"]["title"]["status"]), (79, "official"))
        self.assertEqual((lim(P["bilibili"]["description"]), P["bilibili"]["description"]["status"]), (249, "official"))
        self.assertEqual((P["xiaohongshu"]["title"]["max"], P["xiaohongshu"]["title"]["count"], P["xiaohongshu"]["title"]["status"]), (20, "cjk1_ascii_half", "official"))
        self.assertEqual((P["xiaohongshu"]["description"]["max"], P["xiaohongshu"]["description"]["status"]), (1000, "official"))
        self.assertEqual((P["youtube"]["title"]["max"], P["youtube"]["title"]["status"]), (100, "official"))
        self.assertEqual((P["youtube"]["description"]["max"], P["youtube"]["description"]["count"], P["youtube"]["description"]["status"]), (5000, "utf8_bytes", "official"))
        self.assertEqual((P["douyin"]["title"]["max"], P["douyin"]["title"]["status"]), (30, "unofficial"))
        self.assertEqual((P["channels"]["title"].get("min"), P["channels"]["title"]["max"], P["channels"]["title"]["status"]), (6, 16, "unofficial"))
        # v1.5 标签规则
        bt = P["bilibili"].get("tags") or {}; yt = P["youtube"].get("tags") or {}; dt = P["douyin"].get("tags") or {}
        self.assertEqual((bt.get("joined_max"), bt.get("join"), bt.get("strict_less_than"), bt.get("status")), (200, ",", True, "official"))
        self.assertEqual((yt.get("joined_max"), yt.get("join"), yt.get("count"), yt.get("status")), (500, ",", "youtube_tags", "official"))
        self.assertEqual((dt.get("max_items"), dt.get("status")), (5, "unofficial"))
        self.assertNotIn("tags", P["xiaohongshu"]); self.assertNotIn("tags", P["channels"])
        self.assertNotRegex(t, r"5\s*[–~-]\s*10\s*个", "v1.5 取消全局“标签 5–10 个”")
        for p in P.values():
            for part in ("title", "description", "tags"):
                if part in p: self.assertTrue(p[part].get("source"), (p["id"], part))

    @covers("S-NF6-01", "NF-06")
    def test_skill_md_has_no_tokens(self):
        """SKILL.md 不含 tokens.json 中的任何色值（除 #070A0F），保证改 tokens 不需改 SKILL.md"""
        tokens = self.require_path("assets/tokens.json").read_text()
        colors = {c.upper() for c in COLOR.findall(tokens)} - {"#070A0F"}
        t = self.skill_md().upper()
        self.assertEqual([c for c in colors if c in t], [])

    @covers("S-LAY-04", "F-10")
    def test_layout_md_json_block(self):
        """R-06：LAYOUT.md 恰好一个 json 块，且恰为 {version:1, portrait_keywords:["竖屏"], landscape_keywords:["横屏"]}"""
        _, d = only_json_block(self, "references/LAYOUT.md")
        self.assertEqual(d, {"version": 1, "portrait_keywords": ["竖屏"], "landscape_keywords": ["横屏"]})

    @covers("S-LAY-05", "F-08", "F-09")
    def test_main_tsx_inject_anchor(self):
        """R-09：模板 src/Main.tsx 中注入锚点 {/* @test-inject:layers */} 恰好出现 1 次（供 I-CK-05 使用）"""
        t = self.require_path("assets/project-template/src/Main.tsx").read_text(encoding="utf-8")
        self.assertEqual(t.count("{/* @test-inject:layers */}"), 1)

    @covers("S-LAY-03", "F-08", "F-09")
    def test_data_layer_values(self):
        """Q-13②：project-template 中 data-layer 只取 background|scene|hud|subtitle，且四个值都出现；SourceBadge 带 data-role=source-badge"""
        src = self.require_path("assets/project-template/src")
        vals = set(re.findall(r'data-layer\s*=\s*["\'{]+\s*["\']?([A-Za-z_-]+)', rg(r"data-layer", src)))
        self.assertEqual(vals, {"background", "scene", "hud", "subtitle"})
        self.assertTrue(rg(r'data-role\s*=\s*["\']source-badge', src))

    @covers("S-SCH-01", "F-11", "F-08")
    def test_v12_schemas_exist(self):
        """v1.2 新增/调整的 Schema 齐全：check-report、assets-manifest（对象顶层）、timeline、storyboard、subtitles"""
        for n in ("check-report", "assets-manifest", "timeline", "storyboard", "subtitles", "platforms", "publish-check"):
            self.require_path(f"assets/schemas/{n}.schema.json")


    @covers("S-REPO-01", "F-01", "F-14")
    def test_repo_agents_md_exists(self):
        """A-28：交付仓库根必须有静态 AGENTS.md（与 <slug>/project/AGENTS.md 分工；真源在仓库根，不是 AGENTS.md.tmpl）"""
        p = REPO_DIR / "AGENTS.md"
        self.assertTrue(p.is_file(), f"未实现：缺少仓库根 {p}（架构 v1.11 §2.0 / A-28）")

    @covers("S-REPO-02", "F-01", "F-14")
    def test_repo_agents_md_required_sections(self):
        """A-28 / §2.0：仓库根 AGENTS.md 须含项目说明、技能路径、使用步骤、环境前提、开发自检、与工程内 AGENTS.md 的区分"""
        p = REPO_DIR / "AGENTS.md"
        if not p.is_file():
            self.fail(f"未实现：缺少仓库根 {p}")
        text = p.read_text(encoding="utf-8")
        # 1 项目是什么
        self.assertRegex(text, r"Remotion")
        self.assertTrue("信息图" in text or "口播" in text, "须说明信息图/口播视频模板")
        self.assertRegex(text, r"(?i)Agent\s*Skill|技能")
        # 2 技能位置
        self.assertIn(".agents/skills/remotion-infographic-video/", text)
        # 3 使用步骤
        for s in (".env.example", ".env", "DOUBAO_TTS_API_KEY", "开始制作", "选题", "竖屏"):
            self.assertIn(s, text, f"使用步骤缺「{s}」")
        # 4 环境前提
        self.assertRegex(text, r"Node\s*18")
        self.assertRegex(text, r"Python\s*3")
        self.assertIn("ffmpeg", text)
        # 5 开发/自检
        self.assertIn("tests/", text)
        self.assertTrue("skills-ref" in text or "agentskills" in text, "须提及 skills-ref 或 agentskills validate")
        # 6 两份 AGENTS.md 区分
        self.assertRegex(text, r"(project/AGENTS\.md|<slug>.{0,20}AGENTS\.md|工程内.{0,10}AGENTS)")
        self.assertRegex(text, r"(仓库根|本仓|本模板).{0,30}AGENTS")
