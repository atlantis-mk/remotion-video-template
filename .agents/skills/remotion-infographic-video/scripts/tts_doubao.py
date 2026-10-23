#!/usr/bin/env python3
"""步骤 3：配音。script.md → <out-dir>/full.mp3 + timeline.json + subtitles.json（+ parts/、tts.log）。
用法：python3 scripts/tts_doubao.py <script.md> --out-dir <slug>/voice [--speaker ID] [--only 03,07] [--max-attempts 3] [--dry-run]
- Key 只从技能包根目录 .env 的 DOUBAO_TTS_API_KEY 读取；缺失退出 3，不产出任何文件。
- 不补尾部静音：full.mp3 = 各句音频 + 各句 silence_ms 顺序拼接。
退出码：0 成功；2 用法；3 缺 Key；4 鉴权失败；5 稿件不合格；6 重试耗尽（用 --only 只重跑失败句）；7 响度不达标。"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.envfile import load_env, DEFAULT_SPEAKER
from lib.log import Redactor  # noqa: E402
from lib.errors import SkillError, MissingKeyError  # noqa: E402
from lib.cli import summary  # noqa: E402
from lib import script_parser  # noqa: E402

SKILL = Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script"); ap.add_argument("--out-dir", required=True)
    ap.add_argument("--speaker"); ap.add_argument("--only", help="逗号分隔的句 id，只重合成这些句")
    ap.add_argument("--max-attempts", type=int, default=3, help="单句总尝试次数（首发+重试），1–3，默认 3")
    ap.add_argument("--dry-run", action="store_true", help="只解析稿件并打印请求计划，不调用接口")
    ap.add_argument("--skill-dir", default=str(SKILL))
    a = ap.parse_args(argv)
    if not 1 <= a.max_attempts <= 3:
        ap.error("--max-attempts 只能取 1–3（PRD：重试总尝试 ≤3）")
    try:
        cfg = load_env(a.skill_dir)
    except MissingKeyError as e:
        print(f"[tts] {e}", file=sys.stderr)
        return summary(False, 3, {}, [{"kind": e.kind, "env_path": e.env_path, "var": e.var, "message": str(e)}])
    red = Redactor(secrets=[cfg.key])
    speaker = a.speaker or cfg.speaker or DEFAULT_SPEAKER
    try:
        lines = script_parser.parse(Path(a.script).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:   # 稿件不合格（含空句 empty_line）：退出 5，不发起任何 TTS 请求
        err = {"kind": getattr(e, "kind", "bad_script"), "message": str(e)}
        if getattr(e, "line_id", None): err["line_id"] = e.line_id
        print(f"[tts] {e}", file=sys.stderr)
        return summary(False, 5, {}, [err], red)
    only = [x.strip() for x in a.only.split(",") if x.strip()] if a.only else None
    if a.dry_run:
        plan = {"endpoint": "doubao seed-tts (HTTP)", "auth": "X-Api-Key from .env (not shown)", "speaker": speaker,
                "lines": len(lines), "only": only, "max_attempts": a.max_attempts, "out_dir": str(Path(a.out_dir).resolve())}
        print(red.redact(json.dumps(plan, ensure_ascii=False, indent=2)), file=sys.stderr)
        return summary(True, 0, {"plan": plan}, [], red)
    from lib.tts_client import DoubaoHttpClient
    from lib.audio import FfmpegAudioTool
    from lib.tts_pipeline import run_tts
    try:
        r = run_tts(lines, client=DoubaoHttpClient(cfg.key), audio=FfmpegAudioTool(), out_dir=Path(a.out_dir), speaker=speaker,
                    only=set(only) if only else None, max_attempts=a.max_attempts, redactor=red, log=lambda m: print(m, file=sys.stderr))
    except SkillError as e:
        print(red.redact(f"[tts] {e}"), file=sys.stderr)
        return summary(False, e.code, {"log": str(Path(a.out_dir) / "tts.log")}, [{"kind": e.kind, "message": str(e)}], red)
    return summary(True, 0, {"full": str(r.full), "timeline": str(r.timeline), "subtitles": str(r.subtitles),
                             "audio_seconds": r.audio_seconds, "lufs": r.lufs, "synthesized": r.synthesized, "cached": r.cached}, [], red)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # 未预期错误：退出 1，消息仍需脱敏
        try:
            red = Redactor(secrets=[load_env(SKILL).key])
        except Exception:
            red = Redactor()
        print(red.redact(f"[tts] 未预期错误：{type(e).__name__}: {e}"), file=sys.stderr)
        sys.exit(summary(False, 1, {}, [{"kind": "unexpected", "message": red.redact(str(e))}]))
