#!/usr/bin/env python3
"""步骤 0：前置检查。只读技能包根目录的 .env（不读进程环境变量），并检查 node / python3 / ffmpeg / ffprobe。
用法：python3 scripts/check_env.py [--skill-dir DIR]
退出码：0 通过；3 配置缺失（.env 无 Key 或缺命令）。stdout 最后一行为 JSON 摘要，不输出 Key 及其长度/前缀。"""
import argparse, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.envfile import load_env, env_path_of, DEFAULT_SPEAKER, KEY_VAR  # noqa: E402
from lib.errors import MissingKeyError  # noqa: E402
from lib.cli import summary  # noqa: E402

REQUIRED_CMDS = ("node", "python3", "ffmpeg", "ffprobe")


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parents[1]), help="技能包根目录（默认：脚本所在目录的上一级）")
    ap.add_argument("--no-cmd-check", action="store_true", help="跳过外部命令检查")
    a = ap.parse_args(argv)
    sd = Path(a.skill_dir).resolve()
    errors, outputs = [], {"env_path": str(env_path_of(sd))}
    try:
        cfg = load_env(sd)
        outputs["speaker"] = cfg.speaker or DEFAULT_SPEAKER
    except MissingKeyError as e:
        errors.append({"kind": e.kind, "env_path": e.env_path, "var": e.var, "message": str(e)})
        print(f"[check_env] {e}", file=sys.stderr)
    if not a.no_cmd_check:
        missing = [c for c in REQUIRED_CMDS if not shutil.which(c)]
        if missing:
            errors.append({"kind": "missing_command", "commands": missing,
                           "message": f"缺少命令：{', '.join(missing)}（请自行安装，脚本不会自动安装）"})
            print(f"[check_env] 缺少命令：{missing}", file=sys.stderr)
    if errors:
        return summary(False, 3, outputs, errors)
    print(f"[check_env] {KEY_VAR} 已配置（值不显示）", file=sys.stderr)
    return summary(True, 0, outputs)


if __name__ == "__main__":
    sys.exit(main())
