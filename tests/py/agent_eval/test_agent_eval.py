"""L5 Agent 对话评测：每个 agent-eval/cases/*.json 生成一个用例，按 transcripts/ 判定（F-03、F-10、F-11、F-13、F-16、F-17、NF-01…）"""
import importlib.util, json, os, unittest
from pathlib import Path
from py.support import covers, TESTS_DIR

AE = TESTS_DIR / "agent-eval"
spec = importlib.util.spec_from_file_location("ae_evaluate", AE / "evaluate.py"); ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)

ns = {}
for p in sorted((AE / "cases").glob("*.json")):
    c = json.loads(p.read_text())
    def t(self, _id=c["id"]):
        # UR-1=B / R-02：L5 为人工评测；未设置 AGENT_RUNNER 时在自动门禁中 SKIP（no runner），交付门禁见 run_all.sh release
        if not os.environ.get("AGENT_RUNNER"): self.skipTest("manual（UR-1=B：L5 人工评测，发布前由 release_gate.py 核对 15 份 PASS 存档）")
        errs = ev.evaluate(_id)
        if errs: self.fail("\n".join(errs))
    t.__name__ = f"test_{c['id'].replace('-', '_')}"
    ns[t.__name__] = covers(c["id"], *c["covers"])(t); ns[t.__name__].__doc__ = f"[{c['id']}] {' '.join(c['covers'])} {c['title']}"
TestAgentEval = type("TestAgentEval", (unittest.TestCase,), ns)
