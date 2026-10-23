"""生成追溯矩阵 TRACEABILITY.md 并检查 F-01～F-17、NF-01～NF-08 全部被覆盖。用法：python3 tools/trace.py [--check]"""
import collections, re, sys, unittest
from pathlib import Path
TESTS = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(TESTS))
from py.support import REQ_IDS

LAYER = {"unit": "L1 单元(Py)", "contract": "L2 接口契约", "static": "L4 静态规范", "integration": "L3 离线集成", "agent_eval": "L5 Agent 对话评测", "gate": "L0 门禁工具"}

def py_cases():
    out = []
    def walk(s):
        for t in s:
            if isinstance(t, unittest.TestSuite): walk(t)
            else:
                fn = getattr(t, t._testMethodName, None)
                layer = LAYER.get(type(t).__module__.split(".")[1], "?")
                if fn is not None and hasattr(fn, "case_id"):
                    out.append((fn.case_id, layer, fn.covers, (fn.__doc__ or "").split("] ", 1)[-1].strip()))
    walk(unittest.defaultTestLoader.discover(str(TESTS / "py"), top_level_dir=str(TESTS)))
    return out

def ts_cases():
    out = []
    for f in sorted((TESTS / "ts").glob("*.test.ts")):
        for m in re.finditer(r"test\('\[(T-[A-Z0-9-]+)\]\s+((?:N?F-\d\d\s+)+)(.*?)'", f.read_text()):
            out.append((m.group(1), "L1/L2 单元(TS)", tuple(m.group(2).split()), m.group(3)))
    return out

def main():
    cases = py_cases() + ts_cases()
    ids = [c[0] for c in cases]; dup = [i for i, n in collections.Counter(ids).items() if n > 1]
    by_req = collections.defaultdict(list); by_layer = collections.Counter(c[1] for c in cases)
    for cid, layer, reqs, _ in cases:
        for r in reqs: by_req[r].append((cid, layer))
    missing = [r for r in REQ_IDS if not by_req[r]]
    lines = ["# 追溯矩阵（自动生成：`python3 tools/trace.py`，勿手改）", "",
             f"用例总数：{len(cases)}；需求条目：{len(REQ_IDS)}；未覆盖：{missing or '无'}；重复 ID：{dup or '无'}", "",
             "## 按层统计", "", "| 层 | 用例数 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(by_layer.items())] + [
             "", "## 需求 → 用例", "", "| 需求 | 用例数 | 覆盖层 | 用例 ID |", "|---|---|---|---|"]
    for r in REQ_IDS:
        lst = by_req[r]
        lines.append(f"| {r} | {len(lst)} | {', '.join(sorted({l for _, l in lst}))} | {', '.join(c for c, _ in lst)} |")
    lines += ["", "## 用例清单", "", "| 用例 ID | 层 | 覆盖需求 | 说明 |", "|---|---|---|---|"]
    lines += [f"| {c} | {l} | {' '.join(r)} | {d.replace('|', '/')} |" for c, l, r, d in sorted(cases)]
    (TESTS / "TRACEABILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"cases={len(cases)} layers={dict(by_layer)} missing={missing} dup={dup}")
    if "--check" in sys.argv and (missing or dup): sys.exit(1)

main()
