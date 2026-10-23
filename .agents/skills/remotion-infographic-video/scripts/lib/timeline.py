"""时间轴纯函数：累计、连续性校验、钳位、秒↔帧、字幕切分（F-05、F-06）。"""
import math, re
from decimal import Decimal, ROUND_HALF_UP
from typing import List


def r3(x) -> float:
    return float(Decimal(repr(float(x))).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def sec_to_frame(s, fps=30) -> int:
    """round(s*fps)，half-up。"""
    return int((Decimal(repr(float(s))) * Decimal(int(fps))).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def build_timeline_lines(lines, durations_s) -> List[dict]:
    """句 i 的区间 = [累计起点, 起点 + 句音频时长 + 该句 silence_ms]；首句从 0 开始、首尾相接，3 位小数。
    保留输入句的 id/section/text/context/silence_ms/speech_rate 等字段。"""
    if len(lines) != len(durations_s):
        raise ValueError("lines 与 durations_s 长度不一致")
    out, t = [], 0.0
    for l, d in zip(lines, durations_s):
        sil = int(l.get("silence_ms") or 0)
        start = r3(t)
        speech_end = r3(t + float(d))
        t = t + float(d) + sil / 1000.0
        end = r3(t)
        row = {k: v for k, v in l.items() if k != "section_title"}
        row.update({"context": list(l.get("context") or []), "silence_ms": sil, "speech_rate": int(l.get("speech_rate") or 0),
                    "start": start, "end": end, "duration_s": r3(end - start), "speech_end_s": speech_end})
        out.append(row)
    return out


def validate_continuity(lines, audio_seconds=None, tol_s=0.001) -> List[str]:
    errs = []
    if not lines:
        return ["lines 为空"]
    if abs(float(lines[0]["start"])) > tol_s:
        errs.append(f"首句 start={lines[0]['start']} 不为 0")
    for i, l in enumerate(lines):
        s, e, d = float(l["start"]), float(l["end"]), float(l["duration_s"])
        if e < s:
            errs.append(f"第 {i} 句 end<start")
        if abs((e - s) - d) > tol_s:
            errs.append(f"第 {i} 句 duration_s={d} ≠ end-start={e - s:.3f}")
        if d <= 0:
            errs.append(f"第 {i} 句 duration_s={d} 应 > 0")
        # v1.9 V9-1：停顿算在本句区间内；speech_end_s 必填，start < speech_end_s ≤ end，非末句 end − speech_end_s = silence
        if l.get("speech_end_s") is None:
            errs.append(f"第 {i} 句缺 speech_end_s")
        else:
            se = float(l["speech_end_s"]); sil = int(l.get("silence_ms") or 0) / 1000.0
            if not (s < se <= e + tol_s):
                errs.append(f"第 {i} 句 speech_end_s={se} 不满足 start < speech_end_s ≤ end")
            last = i == len(lines) - 1
            if not last and abs((e - se) - sil) > tol_s:
                errs.append(f"第 {i} 句 end−speech_end_s={e - se:.3f} ≠ 停顿 {sil:.3f}")
            if last and (e - se) > sil + tol_s:
                errs.append(f"末句 end−speech_end_s={e - se:.3f} 超过停顿 {sil:.3f}")
        if i:
            pe = float(lines[i - 1]["end"])
            if s < pe - tol_s:
                errs.append(f"第 {i} 句与上一句重叠（start {s} < 上句 end {pe}）")
            elif s > pe + tol_s:
                errs.append(f"第 {i} 句与上一句有空隙（start {s} > 上句 end {pe}）")
    if audio_seconds is not None and float(lines[-1]["end"]) > float(audio_seconds) + tol_s:
        errs.append(f"末句 end={lines[-1]['end']} 超过 audio_seconds={audio_seconds}")
    return errs


def clamp_to_audio(lines, audio_seconds):
    out = [dict(l) for l in lines]
    a = r3(audio_seconds)
    if out and float(out[-1]["end"]) > a:
        out[-1]["end"] = a
        out[-1]["duration_s"] = r3(a - float(out[-1]["start"]))
        if "speech_end_s" in out[-1] and out[-1]["speech_end_s"] > a:
            out[-1]["speech_end_s"] = a
    return out


_PUNCT_SPLIT = re.compile(r"(?<=[，,。！？!?；;：:、…])")
_STRIP = re.compile(r"[\s，,。！？!?；;：:、…“”\"'‘’（）()《》—\-]")


def _weight(s):
    return max(1, len(_STRIP.sub("", s)))


def split_cues(line) -> List[dict]:
    text = line["text"].strip()
    parts = [p.strip() for p in _PUNCT_SPLIT.split(text) if p.strip()]
    # 去掉只含标点的片段（并入上一段）
    merged = []
    for p in parts:
        if merged and not _STRIP.sub("", p):
            merged[-1] += p
        else:
            merged.append(p)
    parts = merged or [text]
    start, end = float(line["start"]), float(line.get("speech_end_s") or line["end"])
    if end <= start:
        end = float(line["end"])
    total = sum(_weight(p) for p in parts)
    cues, acc, t0 = [], 0, start
    for i, p in enumerate(parts):
        acc += _weight(p)
        t1 = r3(end) if i == len(parts) - 1 else r3(start + (end - start) * acc / total)
        cues.append({"id": f"{line['id']}-{i + 1:02d}", "line_id": line["id"], "text": p, "start": r3(t0), "end": t1})
        t0 = t1
    return cues
