"""L1 单元：lib/verify.py —— verify_video、validate_publish（按平台规范表）、count_text、find_urls（F-12、F-13、NF-02）
签名按架构 v1.4 §7.5：validate_publish(publish_dir, job, rules: dict[平台, 规则], targets) -> PublishCheck（逐平台，每套只用本平台规则）；
count_text(s, mode)；resolve_targets(job, default_targets)。交付物 publish/<platform>/title.txt、description.txt、tags.txt（v1.5：tags.txt 按平台），封面各平台共用；count_tags(tags, rule)。"""
import shutil
from py.support import SkillTestCase, covers, FIXTURES

def probe(w=1920, h=1080, rate="30/1", vdur="60.000", adur="60.010", acodec="aac"):
    s = [{"codec_type": "video", "codec_name": "h264", "width": w, "height": h, "r_frame_rate": rate, "duration": vdur}]
    if acodec:
        s.append({"codec_type": "audio", "codec_name": acodec, "duration": adur})
    return {"streams": s, "format": {"duration": vdur}}

LS = {"aspect": "landscape", "width": 1920, "height": 1080, "fps": 30}
PT = {"aspect": "portrait", "width": 1080, "height": 1440, "fps": 30}   # v1.3：竖屏 3:4

# 平台规范表（arch-QA v1.3 §U-2），作为 rules 注入；PUBLISH.md 中的同一份表由 S-PUB-02/03 校验
RULES = [
    {"id": "douyin", "title": {"max": 30, "count": "grapheme", "status": "unofficial", "source": "s"},
     "description": {"max": 1000, "count": "grapheme", "status": "unofficial", "source": "s"},
     "tags": {"max_items": 5, "status": "unofficial", "source": "s"}},
    {"id": "bilibili", "title": {"max": 80, "strict_less_than": True, "count": "grapheme", "status": "official", "source": "s"},
     "description": {"max": 249, "count": "grapheme", "status": "official", "source": "s"},   # <250 即 ≤249（description 无 strict 字段）
     "tags": {"joined_max": 200, "join": ",", "strict_less_than": True, "count": "grapheme", "status": "official", "source": "s"}},
    {"id": "xiaohongshu", "title": {"max": 20, "count": "cjk1_ascii_half", "status": "official", "source": "s"},
     "description": {"max": 1000, "count": "cjk1_ascii_half", "status": "official", "source": "s"}},
    {"id": "channels", "title": {"max": 16, "min": 6, "count": "grapheme", "status": "unofficial", "source": "s"},
     "description": {"max": 1000, "count": "grapheme", "status": "unofficial", "source": "s"}},
    {"id": "youtube", "title": {"max": 100, "count": "grapheme", "status": "official", "source": "s"},
     "description": {"max": 5000, "count": "utf8_bytes", "status": "official", "source": "s"},
     "tags": {"joined_max": 500, "join": ",", "count": "youtube_tags", "status": "official", "source": "s"}},
]   # xiaohongshu、channels 无 tags 规则 → 只查非空与无链接（v1.5）
RULES = {r["id"]: r for r in RULES}   # v1.4：rules 为 dict[PlatformId, PlatformRule]
ALL = list(RULES)

def _g(o, k): return o[k] if isinstance(o, dict) else getattr(o, k)
def plat(r, pid):
    for x in _g(r, "platforms"):
        if _g(x, "id") == pid: return x
    raise AssertionError(f"PublishCheck.platforms 中没有 {pid}")
def errs(r, pid=None):
    ps = [plat(r, pid)] if pid else _g(r, "platforms")
    return [e for x in ps for e in _g(x, "errors")]
def warns(r, pid=None):
    ps = [plat(r, pid)] if pid else _g(r, "platforms")
    return [w for x in ps for w in _g(x, "warnings")]
def ok(r): return _g(r, "ok")

class TestValidators(SkillTestCase):
    @covers("U-VD-01", "F-12")
    def test_verify_video_ok(self):
        """分辨率=画幅（横 1920×1080 / 竖 1080×1440）、30fps、AAC、音视频差≤0.1s（含 0.100）→ []"""
        f = self.libfn("verify", "verify_video")
        self.assertEqual(f(probe(), LS, 60.0), [])
        self.assertEqual(f(probe(1080, 1440), PT, 60.0), [])
        self.assertEqual(f(probe(vdur="60.100"), LS, 60.0), [])

    @covers("U-VD-02", "F-12")
    def test_verify_video_failures(self):
        """分辨率错（含旧 9:16 1080×1920）、帧率错、无 AAC、时长差>0.1s 均返回非空错误列表"""
        f = self.libfn("verify", "verify_video")
        for p, j in ((probe(1080, 1920), PT), (probe(1080, 1440), LS), (probe(rate="25/1"), LS), (probe(rate="30000/1001"), LS),
                     (probe(acodec="mp3"), LS), (probe(acodec=None), LS), (probe(vdur="60.2"), LS), (probe(vdur="63.0"), LS)):
            r = f(p, j, 60.0); self.assertIsInstance(r, list); self.assertTrue(r, (p, j))

    def pub(self, title="一分钟看懂技能包", desc="简介正文。", tags=("AI", "科技", "信息图"), cover="landscape", per=None, tags_per=None, targets=ALL):
        """publish/<p>/title.txt、description.txt、tags.txt（per 覆盖 (title, desc)，tags_per 覆盖标签列表或原始文本）；封面共用"""
        d = self.tmpdir() / "publish"; d.mkdir()
        for pid in targets:
            t, ds = (per or {}).get(pid, (title, desc)); tg = (tags_per or {}).get(pid, tags)
            (d / pid).mkdir(); (d / pid / "title.txt").write_text(t, encoding="utf-8"); (d / pid / "description.txt").write_text(ds, encoding="utf-8")
            (d / pid / "tags.txt").write_text(tg if isinstance(tg, str) else "\n".join(tg), encoding="utf-8")
        src = "cover_1920x1080.png" if cover == "landscape" else "cover_1080x1440.png"
        shutil.copy(FIXTURES / "covers" / src, d / src)
        return d

    @covers("U-VD-03", "F-13")
    def test_validate_publish_basic(self):
        """合规（5 平台各一套 title/description/tags）→ ok 且无 error；任一平台标题/简介为空或缺文件失败；缺某平台 tags.txt 失败；封面尺寸与画幅不符失败（v1.5 无全局标签个数规则）"""
        f = self.libfn("verify", "validate_publish")
        r = f(self.pub(), LS, RULES, ALL); self.assertEqual(errs(r), []); self.assertIs(ok(r), True)
        self.assertEqual(sorted(_g(x, "id") for x in _g(r, "platforms")), sorted(ALL))
        self.assertEqual(errs(f(self.pub(cover="portrait"), PT, RULES, ALL)), [])
        self.assertEqual(errs(f(self.pub(tags=["AI"]), LS, RULES, ALL)), [], "v1.5 取消“5–10 个”：1 个标签在各平台都合规")
        d = self.pub(); (d / "bilibili" / "tags.txt").unlink(); self.assertTrue(errs(f(d, LS, RULES, ALL), "bilibili"))
        self.assertTrue(errs(f(self.pub(per={"bilibili": ("一分钟看懂", "")}), LS, RULES, ALL), "bilibili"))
        self.assertTrue(errs(f(self.pub(per={"youtube": ("  ", "简介")}), LS, RULES, ALL), "youtube"))
        d = self.pub(); (d / "channels" / "description.txt").unlink()
        self.assertTrue(errs(f(d, LS, RULES, ALL), "channels"), "缺平台文件应判该平台错误")
        self.assertIs(ok(f(self.pub(), PT, RULES, ALL)), False, "竖屏片缺 1080×1440 封面应失败")
        self.assertIs(ok(f(self.pub(cover="portrait"), LS, RULES, ALL)), False, "横屏片缺 1920×1080 封面应失败")

    @covers("U-VD-05", "F-13")
    def test_validate_publish_official_limits_fail(self):
        """各套只按本平台 official 规则：小红书标题 21（cjk1_ascii_half）；B 站标题 80（须 <80）、简介 250（须 ≤249）；YouTube 标题含 < >、简介 >5000 UTF-8 字节 → 本平台 error"""
        f = self.libfn("verify", "validate_publish")
        def one(pid, t="一分钟看懂技能包", d="简介正文。"):
            return f(self.pub(per={pid: (t, d)}, targets=[pid]), LS, RULES, [pid])
        self.assertEqual(errs(one("xiaohongshu", "字" * 20)), []); self.assertTrue(errs(one("xiaohongshu", "字" * 21), "xiaohongshu"))
        self.assertEqual(errs(one("xiaohongshu", "字" * 18 + "ABCD")), []); self.assertTrue(errs(one("xiaohongshu", "字" * 18 + "ABCDE")))
        self.assertEqual(errs(one("bilibili", "字" * 79)), []); self.assertTrue(errs(one("bilibili", "字" * 80)))
        self.assertEqual(errs(one("bilibili", d="字" * 249)), []); self.assertTrue(errs(one("bilibili", d="字" * 250)))
        self.assertTrue(errs(one("youtube", "AI <芯片>")))
        self.assertEqual(errs(one("youtube", d="字" * 1666)), []); self.assertTrue(errs(one("youtube", d="字" * 1667)))

    @covers("U-VD-08", "F-13")
    def test_validate_publish_per_platform_isolation(self):
        """v1.4：每套只用本平台规则——25 字标题放 youtube/ 通过，放 xiaohongshu/ 判 xiaohongshu 错误；其他平台不受牵连"""
        f = self.libfn("verify", "validate_publish"); t25 = "字" * 25
        r = f(self.pub(per={"youtube": (t25, "简介")}), LS, RULES, ALL)
        self.assertEqual(errs(r, "youtube"), []); self.assertEqual(errs(r), [])
        r = f(self.pub(per={"xiaohongshu": (t25, "简介")}), LS, RULES, ALL)
        self.assertTrue(errs(r, "xiaohongshu")); self.assertIs(ok(r), False)
        for pid in ("youtube", "bilibili", "douyin", "channels"):
            self.assertEqual(errs(r, pid), [], pid)

    @covers("U-VD-06", "F-13")
    def test_validate_publish_unofficial_only_warns(self):
        """unofficial 规则不满足 → 本平台只告警、ok 仍为 true：抖音标题 31；视频号标题 5（<6）或 17（>16）"""
        f = self.libfn("verify", "validate_publish")
        for title, pid in (("字" * 31, "douyin"), ("字" * 5, "channels"), ("字" * 17, "channels")):
            r = f(self.pub(per={pid: (title, "简介")}, targets=[pid]), LS, RULES, [pid])
            self.assertEqual(errs(r), [], (title, pid)); self.assertTrue(warns(r, pid), (title, pid)); self.assertIs(ok(r), True)
        r = f(self.pub(title="字" * 10, targets=["douyin", "channels"]), LS, RULES, ["douyin", "channels"]); self.assertEqual(warns(r), [])

    @covers("U-VD-09", "F-13", "F-08")
    def test_validate_publish_description_counts_credits(self):
        """简介长度包含“素材署名：”段：正文 240 字 + 署名段使 B 站简介超 249 → bilibili error"""
        f = self.libfn("verify", "validate_publish")
        credit = "\n素材署名：\n- [A01] 张三 · Wikimedia Commons · CC BY 4.0\n"
        r = f(self.pub(per={"bilibili": ("标题", "字" * 240 + credit)}, targets=["bilibili"]), LS, RULES, ["bilibili"])
        self.assertTrue(errs(r, "bilibili"))

    @covers("U-VD-07", "F-13", "F-08", "NF-02")
    def test_validate_publish_rejects_urls(self):
        """任一平台的 title.txt 或 description.txt 出现链接（https、www.、裸域名）→ 该平台 error（v1.4）"""
        f = self.libfn("verify", "validate_publish")
        for pid, t, d in (("bilibili", "标题", "详见 https://a.com/x"), ("douyin", "标题 www.example.com", "简介"),
                          ("youtube", "标题", "素材署名：\n- [A01] 张三 · commons.wikimedia.org · CC BY 4.0")):
            r = f(self.pub(per={pid: (t, d)}), LS, RULES, ALL); self.assertTrue(errs(r, pid), (pid, t, d)); self.assertIs(ok(r), False)

    @covers("U-VD-10", "F-13")
    def test_resolve_targets(self):
        """resolve_targets(job, default_targets)：job.platforms 优先（去重保序）；缺省用默认 5 个；未知平台 id → 报错"""
        f = self.libfn("verify", "resolve_targets")
        self.assertEqual(f({**LS}, ALL), ALL)
        self.assertEqual(f({**LS, "platforms": ["bilibili", "youtube", "bilibili"]}, ALL), ["bilibili", "youtube"])
        with self.assertRaises(Exception):
            f({**LS, "platforms": ["kuaishou"]}, ALL)

    @covers("U-VD-11", "F-13", "NF-02")
    def test_validate_publish_tags_per_platform(self):
        """v1.5 标签逐平台：B 站逗号连接 199 通过 / 200 失败；YouTube 500 通过 / 501 失败；抖音 6 个只告警且 ok=true；小红书 1 个通过、空文件失败；任一平台标签含 URL 失败"""
        f = self.libfn("verify", "validate_publish")
        def one(pid, tags): return f(self.pub(tags_per={pid: tags}, targets=[pid]), LS, RULES, [pid])
        b199 = ["字" * 99, "字" * 99]          # 99+1+99 = 199
        b200 = ["字" * 99, "字" * 100]         # 200
        self.assertEqual(errs(one("bilibili", b199)), []); self.assertTrue(errs(one("bilibili", b200), "bilibili"))
        y500 = ["a" * 249, "b" * 250]          # 249+1+250 = 500
        y501 = ["a" * 250, "b" * 250]
        self.assertEqual(errs(one("youtube", y500)), []); self.assertTrue(errs(one("youtube", y501), "youtube"))
        self.assertTrue(errs(one("youtube", ["a b" + "c" * 246, "d" * 250])), "含空格标签按 +2 计：249+2+1+250=502 应失败")
        r = one("douyin", [f"t{i}" for i in range(6)])
        self.assertEqual(errs(r), []); self.assertTrue(warns(r, "douyin")); self.assertIs(ok(r), True)
        self.assertEqual(warns(one("douyin", [f"t{i}" for i in range(5)])), [])
        self.assertEqual(errs(one("xiaohongshu", ["AI"])), []); self.assertTrue(errs(one("xiaohongshu", "")), "空 tags.txt 应失败")
        self.assertEqual(errs(one("channels", ["AI"])), []); self.assertTrue(errs(one("channels", "  \n")))
        for pid in ALL:
            self.assertTrue(errs(one(pid, ["AI", "www.example.com"]), pid), pid)

    @covers("U-VD-12", "F-13")
    def test_count_tags(self):
        """count_tags(tags, rule)：grapheme 模式 = Σ字素 + 连接符；youtube_tags 模式下含空格的标签另加 2（引号）"""
        f = self.libfn("verify", "count_tags")
        bili = RULES["bilibili"]["tags"]; yt = RULES["youtube"]["tags"]
        self.assertEqual(f(["AI", "芯片"], bili), 5); self.assertEqual(f(["一分钟"], bili), 3); self.assertEqual(f(["👨‍👩‍👧", "a"], bili), 3)
        self.assertEqual(f(["AI", "chip"], yt), 7); self.assertEqual(f(["AI chip", "x"], yt), 11)   # 7+2 + 1 + 1
        self.assertEqual(f(["a b", "c d"], yt), 11)   # (3+2)+1+(3+2)

    @covers("U-VD-04", "F-13")
    def test_count_text_modes(self):
        """count_text(s, mode) 三种模式（v1.3 U-2）：grapheme（NFC 后扩展字素簇）、cjk1_ascii_half（中文 1、ASCII 字母数字 0.5，总数向上取整）、utf8_bytes"""
        f = self.libfn("verify", "count_text")
        g = lambda s: f(s, "grapheme")
        self.assertEqual(g("一分钟看懂"), 5); self.assertEqual(g("AI 芯片"), 5); self.assertEqual(g("GPT-5"), 5)
        self.assertEqual(g("e\u0301"), 1); self.assertEqual(g("\U0001F468\u200D\U0001F469\u200D\U0001F467"), 1); self.assertEqual(g("🇨🇳"), 1); self.assertEqual(g("！？"), 2)
        h = lambda s: f(s, "cjk1_ascii_half")
        self.assertEqual(h("中文标题"), 4); self.assertEqual(h("AI芯片"), 3); self.assertEqual(h("GPT5"), 2); self.assertEqual(h("abc"), 2); self.assertEqual(h("芯片abc"), 4)
        b = lambda s: f(s, "utf8_bytes")
        self.assertEqual(b("中"), 3); self.assertEqual(b("a"), 1); self.assertEqual(b("😀"), 4); self.assertEqual(b("AI芯片"), 8)
