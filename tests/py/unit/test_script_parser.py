"""L1 单元：lib/script_parser.parse、lib/sources.normalize_number（F-04、NF-03）；签名按架构 v1.2 §7.5"""
from py.support import SkillTestCase, covers

SCRIPT = """# 标题
## S01 钩子
- [01] 半年融资一千五百亿，估值五千亿。 {context: 惊讶 | rate: 0 | pause: 350}
- [02] 我的结论是：一点都不贵。
## S02 公司
- [03] 第三句。 {rate: -8}
"""

class TestScriptParser(SkillTestCase):
    @covers("U-SP-01", "F-04", "F-05")
    def test_parse_sections_lines_defaults(self):
        """段数由稿件决定；句含 id/section/text/context/speech_rate/silence_ms，缺省 rate 0、pause 300"""
        parse = self.attr(self.lib("script_parser"), "parse")
        lines = parse(SCRIPT)
        self.assertEqual([l["id"] for l in lines], ["01", "02", "03"])
        self.assertEqual([l["section"] for l in lines], ["S01", "S01", "S02"])
        self.assertEqual(lines[0]["text"], "半年融资一千五百亿，估值五千亿。")
        self.assertEqual(lines[0]["silence_ms"], 350)
        self.assertEqual(lines[0]["context"], ["惊讶"])
        self.assertEqual((lines[1]["speech_rate"], lines[1]["silence_ms"]), (0, 300))
        self.assertEqual(lines[2]["speech_rate"], -8)

    @covers("U-SP-04", "F-04", "F-05")
    def test_parse_rejects_empty_line(self):
        """RV-2(a)：去空白与标点后有效字数为 0 的句子（如 [05] ……、[06] ？）→ ScriptError(kind="empty_line", line_id)"""
        m = self.lib("script_parser")
        for body, lid in (("- [05] ……", "05"), ("- [06] ？", "06"), ("- [07]   。 ", "07")):
            with self.assertRaises(Exception, msg=body) as cm:
                m.parse(f"## S01 a\n- [01] 正常一句。\n{body}\n")
            self.assertEqual(getattr(cm.exception, "kind", None), "empty_line", body)
            self.assertEqual(getattr(cm.exception, "line_id", None), lid, body)

    @covers("U-SP-02", "F-04")
    def test_parse_rejects_duplicate_ids(self):
        """重复句 id 报错"""
        m = self.lib("script_parser")
        with self.assertRaises(Exception):
            m.parse("## S01 a\n- [01] x。\n- [01] y。\n")

    @covers("U-SP-03", "F-04", "NF-03")
    def test_normalize_number_equivalence(self):
        """lib/sources.normalize_number：汉字写法与阿拉伯写法归一为相等的 Decimal；非数字返回 None"""
        from decimal import Decimal
        n = self.libfn("sources", "normalize_number")
        self.assertIsInstance(n("1500亿"), Decimal); self.assertIsNone(n("没有数字"))
        for a, b in [("一千五百亿", "1500亿"), ("五千亿", "5000亿"), ("一千五百亿", "1,500 亿元"),
                     ("百分之三十", "30%"), ("九", "9"), ("二点五", "2.5")]:
            self.assertEqual(n(a), n(b), (a, b))
        self.assertNotEqual(n("一千五百亿"), n("1500万"))
