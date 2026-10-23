"""发布门禁（架构 v1.7 §7.3.1 / QA RV-1）。
检查：
  1. （默认）先跑自动门禁 `run_all.sh all`：L1–L4、TS 中任何 FAIL/ERROR/SKIP → 不通过（SKIP 按 FAIL 计，只有 L5 可 SKIP）；
  2. tests/agent-eval/archive/ 中 cases/ 下每个 AE 用例（当前 AE-01～AE-15 共 15 个）各至少 1 份 PASS 存档；
  3. 每份 PASS 存档的 skill_md_sha256 等于当前 SKILL.md 文件字节的 sha256，不一致视为缺失；
  4. 并用 evaluate.py 对存档的 jsonl + meta.json 复判，复判不通过视为失效（人工结论与自动判定不一致也算失效）。
存档布局：archive/ 下任意子目录（建议 archive/<ID>/<YYYYMMDD-HHMMSS>/）中同时有
  <ID>.jsonl、<ID>.meta.json、<ID>.verdict.json；
  verdict.json 字段恰为 {case_id, result:"PASS"|"FAIL", skill_md_sha256, judged_by:"auto"|"human", judged_at(ISO8601)}。
用法：python3 tools/release_gate.py [--skill-dir DIR] [--archive DIR] [--archive-only]
输出：逐个 case_id 的 OK / MISSING / INVALID 及原因；任一缺失或失效 → 退出 1；全部有效 → 0。"""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1]; AE = TESTS / "agent-eval"
VERDICT_KEYS = {"case_id", "result", "skill_md_sha256", "judged_by", "judged_at"}
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d(:\d\d(\.\d+)?)?(Z|[+-]\d\d:\d\d)$")

def _ev():
    spec = importlib.util.spec_from_file_location("ae_evaluate", AE / "evaluate.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def check_one(vp: Path, cid: str, sha: str, ev):
    """返回该份存档的失效原因列表；空 = 有效 PASS。"""
    try: v = json.loads(vp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e: return [f"{vp.name} 无法解析：{e}"]
    if not isinstance(v, dict) or set(v) != VERDICT_KEYS: return [f"{vp.name} 字段应恰为 {sorted(VERDICT_KEYS)}"]
    errs = []
    if v["case_id"] != cid: errs.append("case_id 与文件名不符")
    if v["result"] != "PASS": errs.append(f"result={v['result']!r}")
    if v["judged_by"] not in ("auto", "human"): errs.append("judged_by 须为 auto|human")
    if not isinstance(v["judged_at"], str) or not ISO.match(v["judged_at"]): errs.append("judged_at 不是带时区的 ISO8601")
    if v["skill_md_sha256"] != sha: errs.append("skill_md_sha256 与当前 SKILL.md 不一致（存档已失效）")
    for suf in (".jsonl", ".meta.json"):
        if not (vp.parent / f"{cid}{suf}").exists(): errs.append(f"缺 {cid}{suf}")
    if not errs: errs += [f"evaluate 复判：{e}" for e in ev.evaluate(cid, vp.parent)]
    return errs

def check_archive(skill_dir: Path, archive: Path, ev=None):
    """返回 (ok_ids, problems: {case_id: [原因]})"""
    sk = Path(skill_dir) / "SKILL.md"
    ids = sorted(p.stem for p in (AE / "cases").glob("AE-*.json"))
    if not sk.exists(): return [], {i: [f"找不到 {sk}"] for i in ids}
    sha = hashlib.sha256(sk.read_bytes()).hexdigest(); ev = ev or _ev()
    ok, bad = [], {}
    for cid in ids:
        vps = sorted(Path(archive).rglob(f"{cid}.verdict.json")) if Path(archive).exists() else []
        if not vps: bad[cid] = ["MISSING：无存档"]; continue
        reasons = []
        for vp in vps:
            r = check_one(vp, cid, sha, ev)
            if not r: ok.append(cid); break
            reasons.append(f"{vp.relative_to(archive)}：" + "；".join(r))
        else: bad[cid] = ["INVALID：" + x for x in reasons]
    return ok, bad

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-dir", default=os.environ.get("SKILL_DIR", TESTS.parent / ".agents/skills/remotion-infographic-video"))
    ap.add_argument("--archive", default=AE / "archive")
    ap.add_argument("--archive-only", action="store_true", help="只检查存档（不跑自动门禁）")
    a = ap.parse_args(argv); rc = 0
    if not a.archive_only:
        env = dict(os.environ, SKILL_DIR=str(Path(a.skill_dir).resolve()))
        if subprocess.run(["bash", str(TESTS / "run_all.sh"), "all"], env=env).returncode != 0:
            print("== 自动门禁未通过（L1–L4/TS 的 FAIL、ERROR、SKIP 均计为失败）"); rc = 1
    ok, bad = check_archive(Path(a.skill_dir).resolve(), Path(a.archive))
    for cid in ok: print(f"OK      {cid}")
    for cid, rs in bad.items(): print(f"{rs[0].split('：')[0]:7} {cid}\n  - " + "\n  - ".join(rs))
    n = len(ok) + len(bad); print(f"== 发布门禁（L5 存档）：{len(ok)}/{n} 有效 PASS；缺失或失效：{', '.join(bad) or '无'}")
    return 1 if (bad or rc) else 0

if __name__ == "__main__": sys.exit(main())
