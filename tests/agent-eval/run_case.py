"""对话评测回放 harness（Q-18，测试侧提供）。
为每个用例准备隔离环境（复制技能包、按 setup 设置 .env、注入故障），然后调用外部 Agent 运行器，
由 run_case.py 生成 <ID>.meta.json（R-01），运行器只写 <ID>.jsonl。

用法：AGENT_RUNNER="<命令>" python3 agent-eval/run_case.py [--out <dir>] [AE-01 ...]   （默认 out=agent-eval/transcripts）
运行器接口（R-02）：$AGENT_RUNNER <case.json> <out_dir>
  - case.json 为本脚本写出的用例副本，额外含 skill_dir、workdir 两个绝对路径；运行器按 user_turns 顺序发给 Agent
  - 运行器在 out_dir/ 写出 <ID>.jsonl（Q-18 格式）；退出码 0 仅表示对话正常结束，不代表用例通过
  - 运行器只负责驱动宿主 Agent 与导出记录，不得修改 Agent 回复
meta.json 字段固定为 {case_id, skill_dir, workdir, slug_dir|null, fake_key, started_at, finished_at, runner}，
fake_key 为本次生成的 TEST-<uuid4>；泄露检查要求它在 slug_dir、workdir 下的日志与 JSONL 中出现 0 次。
UR-1=B：L5 为人工评测，人工或运行器跑完后存档到 agent-eval/archive/（格式见其 README，发布门禁 tools/release_gate.py）。"""
import datetime, json, os, shlex, shutil, subprocess, sys, tempfile, uuid
from pathlib import Path
HERE = Path(__file__).resolve().parent; TESTS = HERE.parent
SKILL_DIR = Path(os.environ.get("SKILL_DIR", TESTS.parent / ".agents/skills/remotion-infographic-video")).resolve()
def now(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def prepare(case, FAKE_KEY):
    root = Path(tempfile.mkdtemp(prefix=f"ae-{case['id']}-")); sd = root / SKILL_DIR.name
    shutil.copytree(SKILL_DIR, sd, ignore=shutil.ignore_patterns(".env", "node_modules", ".git"))
    env = case["setup"].get("env")
    real = os.environ.get("AE_DOUBAO_KEY")  # 端到端用例需真实 Key（L5 联网）；仅写入 .env，不进入对话
    if env == "valid_key": (sd / ".env").write_text(f"DOUBAO_TTS_API_KEY={real or FAKE_KEY}\n")
    elif env == "invalid_key": (sd / ".env").write_text(f"DOUBAO_TTS_API_KEY={FAKE_KEY}\n")
    elif env in ("missing", "missing_then_filled"): pass
    work = root / "work"; work.mkdir()
    for name, rel in case["setup"].get("user_files", {}).items(): shutil.copy(TESTS / rel, work / name)
    return root, sd, work

def main(ids, out_dir):
    runner = os.environ.get("AGENT_RUNNER")
    if not runner: sys.exit("未设置 AGENT_RUNNER：L5 为人工评测（UR-1=B），见 README §5")
    out_dir = Path(out_dir).resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    for cid in ids:
        case = json.loads((HERE / "cases" / f"{cid}.json").read_text())
        fake_key = f"TEST-{uuid.uuid4()}"
        root, sd, work = prepare(case, fake_key)
        cp = root / f"{cid}.json"; cp.write_text(json.dumps(dict(case, skill_dir=str(sd), workdir=str(work)), ensure_ascii=False))
        env = dict(os.environ, AE_FILL_ENV_ON_TURN="2" if case["setup"].get("env") == "missing_then_filled" else "",
                   AE_FILL_KEY=fake_key, AE_INJECT=case["setup"].get("inject", ""))
        started = now()
        subprocess.run(shlex.split(runner) + [str(cp), str(out_dir)], env=env, check=False)
        slugs = [p.parent for p in work.rglob("job.json")]
        (out_dir / f"{cid}.meta.json").write_text(json.dumps(
            {"case_id": cid, "skill_dir": str(sd), "workdir": str(work), "slug_dir": str(slugs[0]) if slugs else None,
             "fake_key": fake_key, "started_at": started, "finished_at": now(), "runner": runner}, ensure_ascii=False, indent=2))
        print(f"{cid}: → {out_dir / (cid + '.jsonl')}")

if __name__ == "__main__":
    args = sys.argv[1:]; out = HERE / "transcripts"
    if args[:1] == ["--out"]: out, args = Path(args[1]), args[2:]
    main(args or sorted(p.stem for p in (HERE / "cases").glob("*.json")), out)
