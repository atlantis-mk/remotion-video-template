"""L1 单元：lib/assets.py、lib/credits.py（F-08、NF-04）；签名按架构 v1.2 §7.5"""
import json, struct, zlib
from py.support import SkillTestCase, covers, FIXTURES, load_json

def png_bytes(w, h):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")

class TestAssets(SkillTestCase):
    def m(self): return self.lib("assets")

    @covers("U-AS-01", "F-08")
    def test_classify_usage(self):
        """打不开/授权不明→rejected；短边≥画布短边→fullscreen；否则 card-only"""
        f = self.attr(self.m(), "classify_usage")
        self.assertEqual(f(4000, 3000, 1920, 1080, True, True), "fullscreen")
        self.assertEqual(f(1080, 1080, 1920, 1080, True, True), "fullscreen")
        self.assertEqual(f(1920, 1079, 1920, 1080, True, True), "card-only")
        self.assertEqual(f(1200, 1600, 1080, 1440, True, True), "fullscreen")   # 竖屏 3:4 1080×1440（v1.3）
        self.assertEqual(f(1079, 1600, 1080, 1440, True, True), "card-only")
        self.assertEqual(f(4000, 3000, 1920, 1080, False, True), "rejected")
        self.assertEqual(f(4000, 3000, 1920, 1080, True, False), "rejected")

    @covers("U-AS-02", "F-08")
    def test_image_size_from_header(self):
        """PNG 头部解析宽高；非图片返回 None 或抛错"""
        f = self.attr(self.m(), "image_size_from_header")
        self.assertEqual(f(png_bytes(1234, 567)), (1234, 567))
        try:
            r = f(b"not an image")
        except Exception:
            r = None
        self.assertIsNone(r)

    # ---- credits_diff：lib/credits.py，(manifest, shot_badges, description_text, deliverable) -> {badge,description,deliverable: [缺失 id]}（Q-04）
    MANIFEST = {"version": 1, "assets": [
        {"id": "A01", "needs_attribution": True, "usable": True, "author": "张三", "source": "https://commons.wikimedia.org/x",
         "source_name": "Wikimedia Commons", "license": "CC BY 4.0"},
        {"id": "A02", "needs_attribution": False, "usable": True, "source": "AI 生成", "source_name": "AI 生成"},
        {"id": "A03", "needs_attribution": True, "usable": False, "author": "李四", "source": "https://x.org/y", "source_name": "X"}]}
    # U-3（v1.3 已决定）：三处只写 作者 · 来源名称 · 许可，不放链接
    DESC = "简介正文。\n\n素材署名：\n- [A01] 张三 · Wikimedia Commons · CC BY 4.0\n"
    BADGES = [{"shot_no": 1, "asset_id": "A01", "text": "张三 · Wikimedia Commons · CC BY 4.0"}]
    DLV = {"credits": [{"id": "A01", "author": "张三", "source_name": "Wikimedia Commons", "license": "CC BY 4.0"}]}

    # v1.4：credits_diff(manifest, shot_badges, descriptions: {platform: text}, deliverable) -> {badge:[ids], description:{platform:[ids]}, deliverable:[ids]}
    PLATS = ["douyin", "bilibili", "xiaohongshu", "channels", "youtube"]
    def descs(self, **over): return {p: over.get(p, self.DESC) for p in self.PLATS}

    @covers("U-AS-03", "F-08", "NF-04")
    def test_credits_diff_all_present(self):
        """需署名且 usable 的素材在 shot-badges / 每个平台简介的“素材署名：”段 / deliverable.credits 三处都有 → 全空；usable=false 与无需署名的不参与"""
        d = self.libfn("credits", "credits_diff")(self.MANIFEST, self.BADGES, self.descs(), self.DLV)
        self.assertEqual(d, {"badge": [], "description": {p: [] for p in self.PLATS}, "deliverable": []})

    @covers("U-AS-04", "F-08", "NF-04")
    def test_credits_diff_detects_each_missing(self):
        """任一处缺失 → 对应差集为 ["A01"]；简介按平台逐个比对，只缺 bilibili 时只有 bilibili 报缺"""
        f = self.libfn("credits", "credits_diff")
        self.assertEqual(f(self.MANIFEST, [], self.descs(), self.DLV)["badge"], ["A01"])
        r = f(self.MANIFEST, self.BADGES, self.descs(bilibili="简介正文。\n"), self.DLV)["description"]
        self.assertEqual(r["bilibili"], ["A01"]); self.assertEqual([p for p in self.PLATS if r[p]], ["bilibili"])
        self.assertEqual(f(self.MANIFEST, self.BADGES, self.descs(), {"credits": []})["deliverable"], ["A01"])

    @covers("U-AS-05", "F-08", "NF-04")
    def test_credits_diff_matches_by_id_in_section_only(self):
        """只按“素材署名：”段内的 [asset_id] 匹配：作者名写法不同仍通过；id 只出现在段落外不算"""
        f = self.libfn("credits", "credits_diff")
        alt = "简介。\n\n素材署名：\n- [A01] Zhang San · Wikimedia Commons · CC BY 4.0\n"
        self.assertEqual(f(self.MANIFEST, self.BADGES, self.descs(youtube=alt), self.DLV)["description"]["youtube"], [])
        self.assertEqual(f(self.MANIFEST, self.BADGES, self.descs(douyin="正文提到 [A01] 张三。\n"), self.DLV)["description"]["douyin"], ["A01"])

    @covers("U-AS-06", "F-08", "NF-02", "NF-04")
    def test_find_urls(self):
        """lib/verify.find_urls（v1.3 U-3，URL_RE §4.6）：http(s)://、www.、裸域名（.com/.cn/.net/.org/.io/.tv/.me/.co/.info/.gov/.edu）均命中；纯来源名称不命中"""
        f = self.libfn("verify", "find_urls")
        for t in ("见 https://a.com/x", "http://b.cn", "www.example.tv/a", "来源 commons.wikimedia.org/wiki/x", "unsplash.com", "foo.io"):
            self.assertTrue(f(t), t)
        for t in ("张三 · Wikimedia Commons · CC BY 4.0", "AI 生成", "据 国家统计局", "CC BY-SA 4.0", "版本 4.0.537"):
            self.assertEqual(f(t), [], t)

    # ---- v1.9 V9-2：licenses.json {version, note, allowed, no_attribution, denied}；规范化匹配 ----
    DENIED_DEFAULT = ["nc", "nd", "noncommercial", "non commercial", "noderivs", "no derivatives", "all rights reserved",
                      "editorial", "版权所有", "非商业", "禁止演绎"]   # A-27

    def _add(self, sd, lic, aid="L01"):
        """经 fetch_asset.py add（用临时复制的技能包）登记一张合规尺寸图片，返回 (进程, manifest 条目|None)"""
        d = self.tmpdir(); man = d / "assets-manifest.json"
        p = self.cli("fetch_asset.py", "add", "--manifest", man, "--id", aid, "--file", FIXTURES / "img_2000x1200.png", "--content", "c",
                     "--source-url", "https://example.com/a", "--source-name", "Example", "--author", "作者", "--license", lic,
                     "--aspect", "landscape", "--dest", d / "media", skill_dir=sd)
        if p.returncode != 0 or not man.exists(): return p, None
        es = [e for e in json.loads(man.read_text()).get("assets", []) if e["id"] == aid]
        return p, (es[0] if es else None)

    @covers("U-AS-07", "F-08")
    def test_license_nc_denied(self):
        """V9-2：CC BY-NC 4.0 / CC-BY-NC-SA / cc_by_nc 均命中 denied（nc 词元）→ usage=rejected、usable=false（不被 allowed 的 cc by 前缀误放行）"""
        sd = self.copy_skill()
        for lic in ("CC BY-NC 4.0", "CC-BY-NC-SA 4.0", "cc_by_nc"):
            p, e = self._add(sd, lic); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIsNotNone(e, lic); self.assertEqual((e["usage"], e["usable"]), ("rejected", False), lic)

    @covers("U-AS-08", "F-08", "NF-04")
    def test_license_cc_by_usable_needs_attribution(self):
        """V9-2：CC-BY 4.0（规范化为 cc by 4.0，以“cc by + 空格/数字”开头）→ 可用（fullscreen）且 needs_attribution=true"""
        sd = self.copy_skill()
        for lic in ("CC-BY 4.0", "CC BY 4.0", "cc_by 4.0"):
            p, e = self._add(sd, lic); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIsNotNone(e, lic); self.assertEqual((e["usage"], e["usable"], e["needs_attribution"]), ("fullscreen", True, True), lic)

    @covers("U-AS-09", "F-08")
    def test_license_unsplash_not_hit_by_nd(self):
        """V9-2：nc/nd 按词元匹配：Unsplash、Unsplash License 不被 nd 误伤 → 可用且无需署名；“CC BY-ND 4.0”仍被拒"""
        sd = self.copy_skill()
        for lic in ("Unsplash", "Unsplash License"):
            p, e = self._add(sd, lic); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIsNotNone(e, lic); self.assertEqual((e["usable"], e["needs_attribution"]), (True, False), lic)
        p, e = self._add(sd, "CC BY-ND 4.0"); self.assertIsNotNone(e); self.assertEqual(e["usage"], "rejected")

    @covers("U-AS-10", "F-08")
    def test_license_no_attr_not_subset_exit5(self):
        """V9-2：licenses.json 中 no_attribution 不是 allowed 的子集（或 allowed 与 denied 有相同项）→ fetch_asset.py 加载时退出 5"""
        for mut in ("not_subset", "overlap"):
            sd = self.copy_skill(); lp = sd / "assets/licenses.json"; d = json.loads(lp.read_text(encoding="utf-8"))
            if mut == "not_subset": d["no_attribution"] = list(d.get("no_attribution", [])) + ["only-in-no-attr"]
            else: d["denied"] = list(d.get("denied", ["nc"])) + [d["allowed"][0]]
            lp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            p, _ = self._add(sd, "CC0")
            self.assertEqual(p.returncode, 5, (mut, p.stdout + p.stderr))

    @covers("U-AS-11", "F-08")
    def test_licenses_json_schema(self):
        """V9-2：assets/licenses.json 通过 assets/schemas/licenses.schema.json；Schema 要求 denied 必填、additionalProperties=false、全小写；
        denied 含 A-27 默认 11 项；no_attribution ⊆ allowed；allowed ∩ denied = ∅；缺 denied 的反例校验失败"""
        v = self.libfn("schema_check", "validate")
        sch = load_json(self.require_path("assets/schemas/licenses.schema.json"))
        lic = load_json(self.require_path("assets/licenses.json"))
        self.assertEqual(v(lic, sch), [])
        self.assertEqual(set(sch.get("required", [])), {"version", "allowed", "no_attribution", "denied"})
        self.assertIs(sch.get("additionalProperties"), False)
        self.assertEqual(set(lic) - {"version", "note", "allowed", "no_attribution", "denied"}, set())
        self.assertTrue(set(self.DENIED_DEFAULT) <= set(lic["denied"]), set(self.DENIED_DEFAULT) - set(lic["denied"]))
        self.assertTrue(set(lic["no_attribution"]) <= set(lic["allowed"])); self.assertEqual(set(lic["allowed"]) & set(lic["denied"]), set())
        bad = {k: x for k, x in lic.items() if k != "denied"}; self.assertTrue(v(bad, sch), "缺 denied 应失败")
        self.assertTrue(v(dict(lic, allowed=lic["allowed"] + ["CC BY"]), sch), "含大写应失败")
        self.assertTrue(v(dict(lic, extra=1), sch), "多余字段应失败")
