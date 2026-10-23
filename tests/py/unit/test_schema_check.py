"""L1 单元：最小 JSON Schema 校验器 + Schema 正反例（F-05、F-07、F-08、F-15）"""
import copy
from py.support import SkillTestCase, covers, load_json

TL = {"engine": "doubao", "speaker": "s", "full_file": "full.mp3", "audio_seconds": 3.0,
      "lines": [{"id": "01", "section": "S01", "text": "一", "context": [], "silence_ms": 300, "speech_rate": 0,
                 "start": 0, "speech_end_s": 2.7, "end": 3.0, "duration_s": 3.0}]}   # v1.9：speech_end_s 必填
SB = {"version": 1, "aspect": "landscape", "sections": [{"id": "S01", "title": "t", "palette": {"a": "gold", "b": "blue"},
      "transition": "wipe", "shots": [{"shot_no": 1, "line_ids": ["01"], "description": "d", "component": "SlamTitle", "entrance": "push"}]}]}
AM = {"version": 1, "assets": [{"id": "A01", "file": "media/a.png", "kind": "image", "content": "c", "source": "AI 生成", "license": "AI 生成",
       "needs_attribution": False, "opens": True, "usage": "card-only", "usable": True, "width": 800, "height": 600}]}

class TestSchemas(SkillTestCase):
    def v(self, schema_name, doc):
        validate = self.attr(self.lib("schema_check"), "validate")
        schema = load_json(self.require_path(f"assets/schemas/{schema_name}"))
        return validate(doc, schema)  # 返回错误列表

    @covers("U-SC-01", "F-05", "F-15")
    def test_timeline_schema(self):
        """timeline 正例通过；缺 9 个必需字段任一（v1.9 含 speech_end_s）/ id 格式错 / lines 为空均失败"""
        self.assertFalse(self.v("timeline.schema.json", TL))
        for k in ("id", "text", "context", "silence_ms", "speech_rate", "start", "speech_end_s", "end", "duration_s"):
            d = copy.deepcopy(TL); del d["lines"][0][k]
            self.assertTrue(self.v("timeline.schema.json", d), k)
        d = copy.deepcopy(TL); d["lines"][0]["id"] = "1"; self.assertTrue(self.v("timeline.schema.json", d))
        d = copy.deepcopy(TL); d["lines"] = []; self.assertTrue(self.v("timeline.schema.json", d))

    @covers("U-SC-02", "F-07")
    def test_storyboard_schema(self):
        """storyboard 正例通过；非法转场/入场、缺镜号/句 id/画面描述/组件均失败"""
        self.assertFalse(self.v("storyboard.schema.json", SB))
        d = copy.deepcopy(SB); d["sections"][0]["transition"] = "fade"; self.assertTrue(self.v("storyboard.schema.json", d))
        d = copy.deepcopy(SB); d["sections"][0]["shots"][0]["entrance"] = "slide"; self.assertTrue(self.v("storyboard.schema.json", d))
        for k in ("shot_no", "line_ids", "description", "component", "entrance"):
            d = copy.deepcopy(SB); del d["sections"][0]["shots"][0][k]; self.assertTrue(self.v("storyboard.schema.json", d), k)
        d = copy.deepcopy(SB); d["sections"][0]["shots"][0]["line_ids"] = []; self.assertTrue(self.v("storyboard.schema.json", d))
        for t in ("wipe", "zoom", "blur", "slide", "iris"):
            d = copy.deepcopy(SB); d["sections"][0]["transition"] = t; self.assertFalse(self.v("storyboard.schema.json", d), t)

    @covers("U-SC-03", "F-08")
    def test_assets_manifest_schema(self):
        """manifest 顶层为对象 {version:1, assets:[...]}（Q-03）：正例通过；顶层数组失败；缺 文件/内容/来源/许可/是否需署名 任一失败"""
        self.assertFalse(self.v("assets-manifest.schema.json", AM))
        self.assertTrue(self.v("assets-manifest.schema.json", AM["assets"]), "顶层数组应失败")
        d = copy.deepcopy(AM); del d["version"]; self.assertTrue(self.v("assets-manifest.schema.json", d))
        for k in ("file", "content", "source", "license", "needs_attribution"):
            d = copy.deepcopy(AM); del d["assets"][0][k]; self.assertTrue(self.v("assets-manifest.schema.json", d), k)

    @covers("U-SC-04", "F-11")
    def test_check_report_schema(self):
        """check-report.schema.json（Q-10）：ok/attempt/aspect/failed_step/steps/log_path；failed_step 枚举外取值失败"""
        ok = {"ok": False, "attempt": 1, "aspect": "landscape", "failed_step": "tsc", "log_path": "/abs/check/tsc.log",
              "steps": [{"name": "tsc", "ok": False, "log_path": "/abs/check/tsc.log", "duration_ms": 1200, "message": "TS2322"}]}
        self.assertFalse(self.v("check-report.schema.json", ok))
        good = {"ok": True, "attempt": 2, "aspect": "portrait", "failed_step": None, "log_path": None, "steps": []}
        self.assertFalse(self.v("check-report.schema.json", good))
        for k in ("ok", "attempt", "aspect", "failed_step", "steps", "log_path"):
            d = copy.deepcopy(ok); del d[k]; self.assertTrue(self.v("check-report.schema.json", d), k)
        d = copy.deepcopy(ok); d["failed_step"] = "lint"; self.assertTrue(self.v("check-report.schema.json", d))
