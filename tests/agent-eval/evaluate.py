"""Agent 对话评测判定器（格式按架构 QA Q-18）。
输入：cases/<ID>.json（用例）+ transcripts/<ID>.jsonl（对话记录）+ transcripts/<ID>.meta.json（运行元信息）。
JSONL 每行：{"turn": int, "role": "user"|"assistant"|"tool", "content": str, "tool_name"?: str, "ts": ISO8601}
  - role=tool 的 content 为工具调用的命令/参数及输出摘要（用于“是否调用了 TTS/渲染/上传”等判定）
  - 文案类判定只看 role=assistant 的 content
meta.json（R-01，由 run_case.py 生成）：{case_id, skill_dir, workdir, slug_dir|null, fake_key: "TEST-<uuid4>", started_at, finished_at, runner}
每个 check 返回错误字符串列表；空列表=通过。"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUESTION = re.compile(r"[?？]")
ASK_MATERIAL = re.compile(r"(提供|发|给|上传|准备).{0,8}(口播稿|稿子|稿件|配音|音频|图片|视频|素材)")

def _assist(t, turn=None):
    return [dict(e, text=e["content"]) for e in t["events"] if e["role"] == "assistant" and (turn is None or e["turn"] == turn)]
def _tools(t, from_turn=None):
    return [e for e in t["events"] if e["role"] == "tool" and (from_turn is None or e["turn"] >= from_turn)]
def _cmd(e): return f"{e.get('tool_name', '')} {e.get('content', '')}"
def _fmt(s, t): return s.replace("{SKILL_DIR}", t.get("skill_dir") or "").replace("{SLUG}", t.get("slug_dir") or "")

def check(c, t):
    k = c["type"]; A = _assist(t); first = A[0]["text"] if A else ""; last = A[-1]["text"] if A else ""
    if k == "first_reply_question_count":
        n = len(QUESTION.findall(first))
        if "eq" in c and n != c["eq"]: return [f"首条回复问句数={n}，应为 {c['eq']}"]
        if "lte" in c and n > c["lte"]: return [f"首条回复问句数={n}>{c['lte']}"]
        return []
    if k == "question_is_topic":
        qs = [x for x in re.split(r"(?<=[。！？?!\n])", first) if QUESTION.search(x)]
        return [] if qs and all("选题" in q for q in qs) else ["问句不是在问选题"]
    if k == "key_prompt_is_statement":
        segs = [x for x in re.split(r"(?<=[。！？?!\n])", first) if "DOUBAO_TTS_API_KEY" in x or ".env" in x]
        return ["缺 Key 提示"] if not segs else [f"Key 提示带问号：{x[:60]}" for x in segs if QUESTION.search(x)]
    if k == "first_reply_contains_any": return [] if any(v in first for v in c["values"]) else [f"首条回复缺 {c['values']}"]
    if k == "first_reply_contains_all": return [f"首条回复缺 {v}" for v in c["values"] if _fmt(v, t) not in first]
    if k == "first_reply_not_asks_materials": return [f"首条回复索要素材：{m.group(0)}" for m in ASK_MATERIAL.finditer(first)]
    if k == "last_reply_contains_all": return [f"交付消息缺 {v}" for v in c["values"] if _fmt(v, t) not in last]
    if k == "last_reply_contains_any": return [] if any(v in last for v in c["values"]) else [f"交付消息缺 {c['values']}"]
    if k == "reply_not_matching": return [f"回复命中禁止模式：{a['text'][:80]}" for a in A if re.search(c["pattern"], a["text"])]
    if k == "no_tool_call_matching": return [f"出现禁止的调用：{_cmd(e)[:120]}" for e in _tools(t) if re.search(c["pattern"], _cmd(e))]
    if k == "tool_call_matching": return [] if any(re.search(c["pattern"], _cmd(e)) for e in _tools(t)) else [f"未调用 {c['pattern']}"]
    if k == "tool_call_after_turn": return [] if any(re.search(c["pattern"], _cmd(e)) for e in _tools(t, c["turn"])) else [f"第 {c['turn']} 轮后未调用 {c['pattern']}"]
    if k == "tool_call_count":
        n = sum(1 for e in _tools(t) if re.search(c["pattern"], _cmd(e))); errs = []
        if "lte" in c and n > c["lte"]: errs.append(f"{c['pattern']} 调用 {n} 次 > {c['lte']}")
        if "gte" in c and n < c["gte"]: errs.append(f"{c['pattern']} 调用 {n} 次 < {c['gte']}")
        return errs
    if k == "turn_count_assistant_before_user_reply": return [] if len(_assist(t, 1)) == c["eq"] else [f"第 1 轮 assistant 消息数={len(_assist(t, 1))}"]
    if k == "no_question_until_delivery":
        # 从 from_turn（默认 1）起，所有 assistant 消息（含最终交付/停止报告）都不得含问号；用例给定的用户轮次之外不得再有用户输入
        frm = c.get("from_turn", 1); n_user = t.get("n_user_turns", 1)
        errs = [f"中途提问：{a['text'][:80]}" for a in A if a["turn"] >= frm and QUESTION.search(a["text"])]
        extra = [e for e in t["events"] if e["role"] == "user" and e["turn"] > n_user]
        return errs + ([f"出现用例之外的用户输入 {len(extra)} 条"] if extra else []) + ([] if A else ["没有任何 assistant 回复"])
    if k == "replies_after_turn_not_contains": return [f"第 {c['turn']} 轮后重复提示：{v}" for a in A if a["turn"] >= c["turn"] for v in c["values"] if v in a["text"]]
    if k == "no_key_in_transcript":
        # R-01：fake_key 在对话记录 JSONL 以及 slug_dir、workdir 下所有日志（*.log、*.jsonl、*.txt）中字面出现 0 次
        key = t.get("fake_key")
        if not key or not re.fullmatch(r"TEST-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", key):
            return [f"meta.fake_key 缺失或不是 TEST-<uuid4>：{key!r}"]
        hits = [t["transcript_path"]] if key in t.get("transcript_raw", "") else []
        for d in {t.get("slug_dir"), t.get("workdir")} - {None}:
            for f in Path(d).rglob("*"):
                if f.is_file() and f.suffix in (".log", ".jsonl", ".txt") and key in f.read_text(errors="ignore"): hits.append(str(f))
        return [f"Key 泄露（出现在 {h}）" for h in hits]
    if k == "job_field":
        p = Path(t.get("slug_dir") or "/nonexistent") / "job.json"
        if not p.exists(): return [f"缺 {p}"]
        v = json.loads(p.read_text()).get(c["field"]); return [] if v == c["eq"] else [f"job.{c['field']}={v}，应为 {c['eq']}"]
    if k == "artifacts_exist": return [f"缺产物 {p}" for p in c["paths"] if not (Path(t.get("slug_dir") or "/nonexistent") / p).exists()]
    if k == "artifacts_absent": return [f"不应存在 {p}" for p in c["paths"] if (Path(t.get("slug_dir") or "/nonexistent") / p).exists()]
    if k == "artifact_equals_user_file":
        a = Path(t.get("slug_dir") or "/nonexistent") / c["path"]; u = HERE.parent / json.loads((HERE / "cases" / f"{t['case']}.json").read_text())["setup"]["user_files"][c["user_file"]]
        return [] if a.exists() and a.read_text() == u.read_text() else ["用户提供的稿件被改写或未使用"]
    if k == "artifact_cli_ok":
        parts = _fmt(c["cmd"], t).split(); script = Path(t["skill_dir"]) / "scripts" / parts[0]
        p = subprocess.run([sys.executable, str(script), *parts[1:]], capture_output=True, text=True)
        return [] if p.returncode == 0 else [f"{c['cmd']} 退出 {p.returncode}"]
    return [f"未知 check 类型 {k}"]

META_KEYS = {"case_id", "skill_dir", "workdir", "slug_dir", "fake_key", "started_at", "finished_at", "runner"}

def evaluate(case_id, tdir=None):
    case = json.loads((HERE / "cases" / f"{case_id}.json").read_text())
    tdir = Path(tdir) if tdir else HERE / "transcripts"
    tp = tdir / f"{case_id}.jsonl"; mp = tdir / f"{case_id}.meta.json"
    if not tp.exists() or not mp.exists():
        return [f"缺少对话记录 {tp} 或 {mp.name}（需用实现后的技能包经 run_case.py 回放导出）"]
    events = []
    for i, line in enumerate(tp.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        e = json.loads(line)
        for k in ("turn", "role", "content", "ts"):
            if k not in e: return [f"{tp.name} 第 {i} 行缺字段 {k}"]
        if e["role"] not in ("user", "assistant", "tool"): return [f"{tp.name} 第 {i} 行 role 非法"]
        events.append(e)
    meta = json.loads(mp.read_text())
    if set(meta) != META_KEYS: return [f"{mp.name} 字段应恰为 {sorted(META_KEYS)}，实际 {sorted(meta)}"]
    if meta["case_id"] != case_id: return [f"{mp.name} case_id 不符"]
    t = {**meta, "case": case_id, "events": events, "n_user_turns": len(case["user_turns"]),
         "transcript_path": str(tp), "transcript_raw": tp.read_text(encoding="utf-8")}
    return [f"{c['type']}: {e}" for c in case["checks"] for e in check(c, t)]

if __name__ == "__main__":
    args = sys.argv[1:]; tdir = None
    if args[:1] == ["--dir"]: tdir, args = args[1], args[2:]
    ids = args or sorted(p.stem for p in (HERE / "cases").glob("*.json"))
    bad = 0
    for i in ids:
        errs = evaluate(i, tdir); bad += bool(errs)
        print(("PASS " if not errs else "FAIL ") + i + ("" if not errs else "\n  - " + "\n  - ".join(errs)))
    sys.exit(1 if bad else 0)
