#!/usr/bin/env python3
"""步骤 6：由 timeline.json + storyboard.json (+ subtitles.json、assets-manifest.json) 生成工程数据文件：
src/data/timeline.ts、subtitles.ts、assets.ts，src/scenes/index.ts（场景注册表），并复制 full.mp3 到 public/audio/。
用法：python3 scripts/build_timeline.py --timeline voice/timeline.json --storyboard storyboard.json
        --subtitles voice/subtitles.json --manifest assets-manifest.json --project project/ [--fps 30]
TOTAL_FRAMES = round(audio_seconds × fps)，不加任何额外帧（无片尾署名页）。输入不合 Schema → 退出 5。"""
import argparse, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.cli import summary, atomic_write, read_json  # noqa: E402
from lib import render_ts, schema_check, assets as A, credits as C  # noqa: E402
from lib.cli import write_json  # noqa: E402
from lib.timeline import validate_continuity  # noqa: E402
from lib.storyboard import check_storyboard  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--timeline", required=True); ap.add_argument("--storyboard", required=True)
    ap.add_argument("--subtitles"); ap.add_argument("--manifest"); ap.add_argument("--project", required=True)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args(argv)
    try:
        tl, sb = read_json(a.timeline), read_json(a.storyboard)
        subs = read_json(a.subtitles) if a.subtitles and Path(a.subtitles).exists() else {"cues": []}
        man = A.load_manifest(a.manifest) if a.manifest else []
    except (OSError, ValueError) as e:
        return summary(False, 5, {}, [{"kind": "bad_input", "message": str(e)}])
    errs = schema_check.validate(tl, schema_check.load_schema("timeline.schema.json"))
    errs += validate_continuity(tl.get("lines", []), tl.get("audio_seconds")) if not errs else []
    errs += check_storyboard(sb, tl, man)
    if subs.get("cues"):
        errs += schema_check.validate(subs, schema_check.load_schema("subtitles.schema.json"))
    errs += schema_check.validate(A.manifest_doc(man), schema_check.load_schema("assets-manifest.schema.json"))
    if errs:
        for e in errs: print(f"[build_timeline] {e}", file=sys.stderr)
        return summary(False, 5, {}, [{"kind": "schema", "message": e} for e in errs])
    proj = Path(a.project)
    atomic_write(proj / "src/data/timeline.ts", render_ts.render_timeline_ts(tl, sb, a.fps))
    atomic_write(proj / "src/data/subtitles.ts", render_ts.render_subtitles_ts(subs, a.fps))
    badges = C.shot_badges(sb, man)
    write_json(proj / "src/data/shot-badges.json", badges)
    atomic_write(proj / "src/data/assets.ts", render_ts.render_assets_ts(man, badges))
    scenes = proj / "src/scenes"; scenes.mkdir(parents=True, exist_ok=True)
    names = [p.stem for p in scenes.glob("S[0-9][0-9].tsx")]
    atomic_write(scenes / "index.ts", render_ts.render_scenes_index_ts(names))
    full = Path(a.timeline).resolve().parent / tl.get("full_file", "full.mp3")
    if full.is_file():
        (proj / "public/audio").mkdir(parents=True, exist_ok=True)
        shutil.copy2(full, proj / "public/audio/full.mp3")
    total = render_ts.frame_tables(tl, sb, a.fps)[0]
    return summary(True, 0, {"total_frames": total, "fps": a.fps, "scenes": sorted(names),
                             "files": ["src/data/timeline.ts", "src/data/subtitles.ts", "src/data/assets.ts", "src/data/shot-badges.json", "src/scenes/index.ts"]})


if __name__ == "__main__":
    sys.exit(main())
