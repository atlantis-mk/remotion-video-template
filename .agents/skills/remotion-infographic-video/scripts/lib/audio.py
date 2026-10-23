"""AudioTool：ffmpeg 实现与内存替身（架构 §7.1）。流水线内部统一用 PCM WAV（采样级精确拼接），最后一次性 loudnorm + 编码 mp3。"""
import json, re, shutil, subprocess, wave
from pathlib import Path

SR = 44100
LOUDNORM = {"I": -16.0, "TP": -1.5, "LRA": 11.0}


class FfmpegAudioTool:
    def __init__(self, ffmpeg=None, ffprobe=None, runner=subprocess.run):
        self.ffmpeg = ffmpeg or shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe = ffprobe or shutil.which("ffprobe") or "ffprobe"
        self.run = runner

    def _ff(self, *args):
        p = self.run([self.ffmpeg, "-hide_banner", "-nostats", "-y", *map(str, args)], capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"ffmpeg 失败：{p.stderr[-400:]}")
        return p

    def duration(self, path) -> float:
        path = Path(path)
        if path.suffix == ".wav":
            with wave.open(str(path)) as w:
                return w.getnframes() / float(w.getframerate())
        p = self.run([self.ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                     capture_output=True, text=True)
        return float(json.loads(p.stdout)["format"]["duration"])

    def decode(self, src, dst):
        self._ff("-i", src, "-ac", "1", "-ar", SR, "-c:a", "pcm_s16le", "-map_metadata", "-1", dst)
        return dst

    def silence(self, ms, dst):
        n = int(round(SR * ms / 1000.0))
        with wave.open(str(dst), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(b"\x00\x00" * n)
        return dst

    def concat(self, paths, dst):
        with wave.open(str(dst), "wb") as out:
            out.setnchannels(1); out.setsampwidth(2); out.setframerate(SR)
            for p in paths:
                with wave.open(str(p)) as w:
                    out.writeframes(w.readframes(w.getnframes()))
        return dst

    def finalize(self, src_wav, dst_mp3):
        """两遍 loudnorm（I=-16, TP=-1.5, LRA=11）后编码 mp3。"""
        ln = "loudnorm=I={I}:TP={TP}:LRA={LRA}".format(**LOUDNORM)
        p = self._ff("-i", src_wav, "-af", ln + ":print_format=json", "-f", "null", "-")
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
        af = ln
        if m:
            st = json.loads(m.group(0))
            af = (ln + ":measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
                  "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**st)
        self._ff("-i", src_wav, "-af", af, "-ar", SR, "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k",
                 "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", "-f", "mp3", dst_mp3)
        return dst_mp3

    def measure_lufs(self, path):
        p = self.run([self.ffmpeg, "-nostats", "-i", str(path), "-filter_complex", "ebur128", "-f", "null", "-"],
                     capture_output=True, text=True)
        m = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", p.stderr)
        return float(m[-1]) if m else None


def mp3_duration(data: bytes):
    """纯函数：按 MPEG 帧头累计 mp3 时长（CBR/VBR 皆可）。无法识别返回 None。"""
    br = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
          2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
    srs = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
    i, total, n = 0, 0.0, 0
    if data[:3] == b"ID3" and len(data) > 10:
        i = 10 + ((data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14 | (data[8] & 0x7F) << 7 | (data[9] & 0x7F))
    while i + 4 <= len(data):
        h = data[i:i + 4]
        if h[0] == 0xFF and (h[1] & 0xE0) == 0xE0:
            ver, layer = (h[1] >> 3) & 3, (h[1] >> 1) & 3
            bi, si, pad = h[2] >> 4, (h[2] >> 2) & 3, (h[2] >> 1) & 1
            if ver != 1 and layer == 1 and 0 < bi < 15 and si < 3:
                sr = srs[ver][si]
                kbps = br[1 if ver == 3 else 2][bi]
                spf = 1152 if ver == 3 else 576
                size = (144 if ver == 3 else 72) * kbps * 1000 // sr + pad
                total += spf / sr; n += 1; i += size
                continue
        i += 1
    return total if n else None


class FakeAudioTool:
    """内存替身：不做真实解码/响度处理，时长按帧头或登记值计算。"""

    def __init__(self):
        self.durations = {}

    def duration(self, path) -> float:
        k = str(Path(path))
        if k in self.durations:
            return self.durations[k]
        data = Path(path).read_bytes()
        if data[:4] == b"RIFF":   # 时长一律从音频本身实测
            import io
            with wave.open(io.BytesIO(data)) as w:
                return w.getnframes() / float(w.getframerate())
        d = mp3_duration(data)
        return d if d is not None else 0.0

    def decode(self, src, dst):
        Path(dst).write_bytes(Path(src).read_bytes())
        self.durations[str(Path(dst))] = self.duration(src)
        return dst

    def silence(self, ms, dst):
        Path(dst).write_bytes(b"")
        self.durations[str(Path(dst))] = ms / 1000.0
        return dst

    def concat(self, paths, dst):
        Path(dst).write_bytes(b"".join(Path(p).read_bytes() for p in paths))
        self.durations[str(Path(dst))] = sum(self.duration(p) for p in paths)
        return dst

    def finalize(self, src, dst):
        Path(dst).write_bytes(Path(src).read_bytes())
        self.durations[str(Path(dst))] = self.duration(src)
        return dst

    def measure_lufs(self, path):
        return -16.0
