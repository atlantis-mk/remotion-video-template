"""配音编排：逐句合成（重试/缓存）→ 拼接 → loudnorm → timeline.json / subtitles.json（F-05、F-06、NF-07）。"""
import hashlib, json, os, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .log import Redactor
from .envfile import DEFAULT_SPEAKER
from .errors import TtsAuthError, TtsTransientError, TtsBadRequest, TtsServiceError, CheckFailed
from .timeline import build_timeline_lines, clamp_to_audio, validate_continuity, split_cues, r3
from .cli import write_json

LUFS_TARGET, LUFS_TOL = -16.0, 1.0


@dataclass
class TtsResult:
    full: Path
    timeline: Path
    subtitles: Path
    audio_seconds: float
    lufs: Optional[float] = None
    synthesized: List[str] = field(default_factory=list)
    cached: List[str] = field(default_factory=list)


def line_hash(l, speaker):
    s = json.dumps([l["text"], speaker, list(l.get("context") or []), int(l.get("speech_rate") or 0)], ensure_ascii=False)
    return hashlib.sha256(s.encode()).hexdigest()


MAX_ATTEMPTS_LIMIT = 3


def run_tts(lines, *, client, audio, out_dir, speaker=DEFAULT_SPEAKER, only=None, max_attempts=3,
            sleeper=time.sleep, redactor=None, engine="doubao", check_lufs=True, log=None):
    """每句总尝试 ≤ max_attempts（≤3，首发 + 最多 2 次重试）；only 为需强制重合成的句 id 集合。"""
    red = redactor or Redactor()
    if not isinstance(max_attempts, int) or not 1 <= max_attempts <= MAX_ATTEMPTS_LIMIT:
        raise ValueError(f"max_attempts 须为 1..{MAX_ATTEMPTS_LIMIT}，收到 {max_attempts!r}")
    attempts_max = max_attempts
    out = Path(out_dir); parts = out / "parts"; parts.mkdir(parents=True, exist_ok=True)
    logf = out / "tts.log"
    only = set(only) if only else None

    def L(msg):
        m = red.redact(msg)
        with open(logf, "a", encoding="utf-8") as f:
            f.write(m + "\n")
        if log:
            log(m)

    ids = [l["id"] for l in lines]
    if len(set(ids)) != len(ids):
        raise TtsBadRequest("句 id 重复")
    if only and not only <= set(ids):
        raise TtsBadRequest(f"--only 中的句不存在：{sorted(only - set(ids))}")

    synthesized, cached, failed, meta = [], [], {}, {}
    for l in lines:
        h = line_hash(l, speaker)
        mj = parts / f"{l['id']}.json"
        old = json.loads(mj.read_text()) if mj.exists() else {}
        prev = parts / old.get("file", f"{l['id']}.none")
        if prev.exists() and old.get("hash") == h and not (only and l["id"] in only):
            cached.append(l["id"]); meta[l["id"]] = old; continue
        for attempt in range(1, attempts_max + 1):
            try:
                r = client.synthesize(l["text"], speaker=speaker, context=list(l.get("context") or []),
                                      speech_rate=int(l.get("speech_rate") or 0))
                fmt = (getattr(r, "format", None) or "mp3").lower()
                dst = parts / f"{l['id']}.{fmt}"   # 按 SynthResult.format 落盘 parts/NN.<fmt>（R-03）
                tmp = parts / f".{l['id']}.{fmt}.tmp"; tmp.write_bytes(r.audio_bytes); os.replace(tmp, dst)
                meta[l["id"]] = {"hash": h, "logid": getattr(r, "logid", None), "file": dst.name}
                write_json(mj, meta[l["id"]])
                synthesized.append(l["id"])
                L(f"[{l['id']}] ok attempt={attempt} logid={getattr(r, 'logid', None)}")
                break
            except TtsAuthError as e:
                L(f"[{l['id']}] auth error: {e}")
                raise TtsAuthError(red.redact(str(e))) from None
            except TtsBadRequest as e:
                L(f"[{l['id']}] bad request: {e}")
                raise TtsBadRequest(red.redact(str(e))) from None
            except TtsTransientError as e:
                L(f"[{l['id']}] transient error attempt={attempt}/{attempts_max}: {e}")
                if attempt == attempts_max:
                    failed[l["id"]] = red.redact(str(e))
                else:
                    sleeper(min(8.0, 0.5 * 2 ** (attempt - 1)))
    if failed:
        raise TtsServiceError(f"以下句重试 {attempts_max} 次仍失败：{sorted(failed)}；可用 --only {','.join(sorted(failed))} 只重跑这些句")

    # 解码 + 静音 + 拼接
    import tempfile
    work_dir = Path(tempfile.mkdtemp(prefix=".work-", dir=out))   # 中间文件不放 parts/，parts/* 永不删除
    seq, durs = [], []
    sil_cache = {}
    for l in lines:
        wav = work_dir / f"{l['id']}.pcm.wav"
        audio.decode(parts / meta[l["id"]].get("file", f"{l['id']}.mp3"), wav)
        durs.append(audio.duration(wav))
        seq.append(wav)
        ms = int(l.get("silence_ms") or 0)
        if ms > 0:
            if ms not in sil_cache:
                sil_cache[ms] = audio.silence(ms, work_dir / f"silence_{ms}.wav")
            seq.append(sil_cache[ms])
    full_wav = work_dir / "_full.wav"
    audio.concat(seq, full_wav)
    full_tmp = out / ".full.mp3.tmp"
    audio.finalize(full_wav, full_tmp)
    audio_seconds = r3(audio.duration(full_tmp))
    lufs = audio.measure_lufs(full_tmp)
    os.replace(full_tmp, out / "full.mp3")
    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)   # 只清理临时工作目录（不在 parts/ 下）

    spans = build_timeline_lines(lines, durs)
    # 编码器帧对齐带来的毫秒级偏差：末句 end 对齐到实测音频时长（超出则钳位，F-06）
    if abs(spans[-1]["end"] - audio_seconds) <= 0.1:
        spans[-1]["end"] = audio_seconds
        spans[-1]["duration_s"] = r3(audio_seconds - spans[-1]["start"])
        # 编码延长末尾时保持 end − speech_end_s ≤ 停顿（V9-1）
        sil_last = int(lines[-1].get("silence_ms") or 0) / 1000.0
        spans[-1]["speech_end_s"] = r3(min(audio_seconds, max(spans[-1]["speech_end_s"], audio_seconds - sil_last)))
    spans = clamp_to_audio(spans, audio_seconds)
    tl_lines = []
    for l, s in zip(lines, spans):
        tl_lines.append({"id": l["id"], "section": l["section"], "text": l["text"], "context": s["context"],
                         "silence_ms": s["silence_ms"], "speech_rate": s["speech_rate"],
                         "start": s["start"], "end": s["end"], "duration_s": s["duration_s"], "speech_end_s": s["speech_end_s"],
                         "file": f"parts/{meta[l['id']].get('file', l['id'] + '.mp3')}", "logid": meta.get(l["id"], {}).get("logid"), "error": None})
    errs = validate_continuity(tl_lines, audio_seconds)
    if errs:
        raise CheckFailed("时间轴不连续：" + "；".join(errs))
    tl = {"engine": engine, "speaker": speaker, "full_file": "full.mp3", "audio_seconds": audio_seconds,
          "lines": tl_lines}
    if lufs is not None:
        tl["lufs"] = round(lufs, 1)
    write_json(out / "timeline.json", tl)
    cues = [c for l in tl_lines for c in split_cues(l)]
    write_json(out / "subtitles.json", {"engine": engine, "speaker": speaker, "cues": cues})
    L(f"done audio_seconds={audio_seconds} lufs={lufs} synthesized={synthesized} cached={cached}")
    res = TtsResult(out / "full.mp3", out / "timeline.json", out / "subtitles.json", audio_seconds, lufs, synthesized, cached)
    if check_lufs and lufs is not None and abs(lufs - LUFS_TARGET) > LUFS_TOL:
        raise CheckFailed(f"响度 {lufs} LUFS 不在 {LUFS_TARGET}±{LUFS_TOL}")
    return res
