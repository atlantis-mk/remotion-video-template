"""生成工程数据文件（纯函数）：tokens.ts、timeline.ts、subtitles.ts、assets.ts、job.ts、scenes/index.ts。"""
import json, re
from .timeline import sec_to_frame

HEADER = "// 自动生成，勿手改。来源：{src}\n"


def _js(v):
    return json.dumps(v, ensure_ascii=False, indent=2)


def render_tokens_ts(tokens: dict) -> str:
    t = {k: v for k, v in tokens.items() if not k.startswith("$")}
    return (HEADER.format(src="assets/tokens.json（scripts/scaffold_project.py）") +
            f"export const TOKENS = {_js(t)} as const;\n\n"
            "export type Tokens = typeof TOKENS;\n"
            "export const COLORS = TOKENS.colors;\n"
            "export const TONES = TOKENS.tones;\n"
            "export type ToneKey = (typeof TOKENS.tones)[number];\n"
            "export const LAYOUT_TOKENS = TOKENS.layout;\n"
            "export const MOTION = TOKENS.motion;\n"
            "export default TOKENS;\n")


def render_job_ts(job: dict) -> str:
    j = {k: job[k] for k in ("topic", "slug", "aspect", "fps") if k in job}
    return (HEADER.format(src="job.json（scripts/scaffold_project.py）") +
            "import { CANVAS_PRESETS } from '../layout/presets';\n\n"
            f"export const JOB_META = {_js(j)} as const;\n"
            "export type Aspect = 'landscape' | 'portrait';\n"
            f"export const ASPECT: Aspect = {json.dumps(j['aspect'])};\n"
            "export const JOB = { ...JOB_META, aspect: ASPECT, ...CANVAS_PRESETS[ASPECT] };\n"
            "export default JOB;\n")


def frame_tables(timeline: dict, storyboard: dict, fps: int = 30):
    total = sec_to_frame(timeline["audio_seconds"], fps)
    lines = []
    tl = timeline["lines"]
    for i, l in enumerate(tl):
        f = sec_to_frame(l["start"], fps)
        t = total if i == len(tl) - 1 else sec_to_frame(l["end"], fps)
        lines.append({"id": l["id"], "section": l.get("section", ""), "from": f, "to": max(f, min(t, total))})
    if lines:
        lines[0]["from"] = 0
        for a, b in zip(lines, lines[1:]):
            b["from"] = a["to"]
    by_id = {l["id"]: l for l in lines}
    sections, shots = [], []
    for s in storyboard.get("sections", []):
        ids = [i for sh in s["shots"] for i in sh["line_ids"] if i in by_id]
        sec_lines = [l for l in lines if l["section"] == s["id"]] or [by_id[i] for i in ids]
        if not sec_lines:
            continue
        sections.append({"id": s["id"], "title": s.get("title", ""), "from": min(l["from"] for l in sec_lines),
                         "to": max(l["to"] for l in sec_lines), "transition": s["transition"], "palette": s["palette"]})
        for sh in s["shots"]:
            ls = [by_id[i] for i in sh["line_ids"] if i in by_id]
            if not ls:
                continue
            d = {k: v for k, v in sh.items() if k not in ("line_ids",)}
            d.update({"section": s["id"], "line_ids": sh["line_ids"], "from": min(l["from"] for l in ls), "to": max(l["to"] for l in ls)})
            shots.append(d)
    # 段首尾相接；末段 to == TOTAL_FRAMES
    sections.sort(key=lambda x: x["from"])
    if sections:
        sections[0]["from"] = 0
        for a, b in zip(sections, sections[1:]):
            b["from"] = a["to"]
        sections[-1]["to"] = total
    return total, lines, sections, shots


def render_timeline_ts(timeline: dict, storyboard: dict, fps: int = 30) -> str:
    total, lines, sections, shots = frame_tables(timeline, storyboard, fps)
    return (HEADER.format(src="voice/timeline.json + storyboard.json（scripts/build_timeline.py）") +
            "export type SectionTransitionType = 'wipe' | 'zoom' | 'blur' | 'slide' | 'iris';\n"
            "export type ShotEntrance = 'push' | 'rise' | 'zoom';\n"
            "export type LineData = { id: string; section: string; from: number; to: number };\n"
            "export type SectionData = { id: string; title: string; from: number; to: number; transition: SectionTransitionType; palette: { a: string; b: string } };\n"
            "export type ShotData = { shot_no: number; section: string; line_ids: string[]; description: string; component: string; entrance: ShotEntrance; from: number; to: number; props?: Record<string, unknown>; asset_ids?: string[]; display_numbers?: { text: string; source_claim_id: string }[]; illustrative?: boolean };\n\n"
            f"export const FPS = {int(fps)};\n"
            f"export const AUDIO_SECONDS = {float(timeline['audio_seconds'])};\n"
            f"export const TOTAL_FRAMES = {total};\n"
            f"export const LINES: readonly LineData[] = {_frames_js(lines)};\n"
            f"export const SECTIONS: readonly SectionData[] = {_frames_js(sections)};\n"
            f"export const SHOTS: readonly ShotData[] = {_frames_js(shots)};\n")


def _frames_js(items):
    """输出 `to: N` 形式（无引号键），便于人读与 grep。"""
    s = _js(items)
    return re.sub(r'"([A-Za-z_][A-Za-z0-9_]*)":', r"\1:", s)


def render_subtitles_ts(subtitles: dict, fps: int = 30) -> str:
    cues = [{"id": c["id"], "line_id": c["line_id"], "text": c["text"], "from": sec_to_frame(c["start"], fps),
             "to": sec_to_frame(c["end"], fps)} for c in subtitles.get("cues", [])]
    return (HEADER.format(src="voice/subtitles.json（scripts/build_timeline.py）") +
            "export type CueData = { id: string; line_id: string; text: string; from: number; to: number };\n"
            f"export const CUES: readonly CueData[] = {_frames_js(cues)};\n")


def badge_text(a):
    from .credits import badge_text as bt
    return bt(a) if a.get("needs_attribution") else ""


def render_assets_ts(manifest, shot_badges=()) -> str:
    from .credits import assets_of
    manifest = assets_of(manifest)
    items = [{"id": a["id"], "file": a.get("file", ""), "kind": a.get("kind", "image"), "usage": a.get("usage", "rejected"),
              "usable": bool(a.get("usable")), "width": a.get("width"), "height": a.get("height"),
              "attribution": badge_text(a)} for a in manifest]
    return (HEADER.format(src="assets-manifest.json（scripts/build_timeline.py）") +
            "export type AssetData = { id: string; file: string; kind: string; usage: 'fullscreen' | 'card-only' | 'rejected'; usable: boolean; width: number | null; height: number | null; attribution: string };\n"
            f"export const ASSETS: readonly AssetData[] = {_frames_js(items)};\n"
            "export const ASSET_BY_ID: Record<string, AssetData> = Object.fromEntries(ASSETS.map((a) => [a.id, a]));\n"
            "export type ShotBadge = { shot_no: number; asset_id: string; text: string };\n"
            f"export const SHOT_BADGES: readonly ShotBadge[] = {_frames_js(list(shot_badges))};\n")


def render_scenes_index_ts(scene_names) -> str:
    names = sorted(scene_names)
    imp = "".join(f"import {n} from './{n}';\n" for n in names)
    body = ", ".join(f"{n}" for n in names)
    return (HEADER.format(src="src/scenes/*.tsx（scripts/build_timeline.py）") +
            "import type React from 'react';\n" + imp +
            "\n// eslint-disable-next-line @typescript-eslint/no-explicit-any\n"
            f"export const SCENES: Record<string, React.FC<any>> = {{ {body} }};\n"
            "export default SCENES;\n")
