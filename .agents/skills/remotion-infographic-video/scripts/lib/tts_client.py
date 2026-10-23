"""TtsClient 协议 + 豆包 HTTP 实现 + 测试替身 FakeTtsClient（架构 §4.4、§7.1）。"""
import base64, json, re, shutil, subprocess, tempfile, urllib.error, urllib.request, uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .errors import TtsAuthError, TtsTransientError, TtsBadRequest, TtsServiceError  # noqa: F401

DOUBAO_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
DOUBAO_RESOURCE_ID = "seed-tts-2.0"


@dataclass
class SynthResult:
    audio_bytes: bytes
    format: str = "mp3"
    logid: Optional[str] = None
    usage: dict = field(default_factory=dict)
    words: Optional[List[dict]] = None

    @property
    def audio(self) -> bytes:
        return self.audio_bytes


class UrllibTransport:
    def post(self, url, headers, body: bytes, timeout=120):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read() if hasattr(e, "read") else b""
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            raise TtsTransientError(f"网络错误：{type(e).__name__}")


class DoubaoHttpClient:
    """豆包语音合成 2.0（HTTP 单向流式）。Key 只在构造请求头时 reveal()。"""

    def __init__(self, key, *, transport=None, url=DOUBAO_URL, resource_id=DOUBAO_RESOURCE_ID, sample_rate=24000):
        self._key, self.transport = key, transport or UrllibTransport()
        self.url, self.resource_id, self.sample_rate = url, resource_id, sample_rate

    def headers(self):
        k = self._key.reveal() if hasattr(self._key, "reveal") else str(self._key)
        return {"Content-Type": "application/json", "X-Api-Key": k, "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": str(uuid.uuid4())}

    def request_body(self, text, *, speaker, context, speech_rate):
        additions = {"disable_markdown_filter": True}
        if context:
            additions["context_texts"] = list(context)
        return {"user": {"uid": "remotion-infographic-video"},
                "req_params": {"text": text, "speaker": speaker,
                               "audio_params": {"format": "mp3", "sample_rate": self.sample_rate, "speech_rate": int(speech_rate)},
                               "additions": json.dumps(additions, ensure_ascii=False)}}

    def synthesize(self, text, *, speaker, context=(), speech_rate=0):
        body = json.dumps(self.request_body(text, speaker=speaker, context=context, speech_rate=speech_rate)).encode()
        status, hdrs, raw = self.transport.post(self.url, self.headers(), body)
        logid = hdrs.get("X-Tt-Logid") or hdrs.get("x-tt-logid")
        if status in (401, 403):
            raise TtsAuthError(f"鉴权失败 HTTP {status} logid={logid}（请检查 .env 中的 DOUBAO_TTS_API_KEY）")
        if status == 429 or status >= 500:
            raise TtsTransientError(f"HTTP {status} logid={logid}")
        if status >= 400:
            raise TtsBadRequest(f"HTTP {status} logid={logid} {raw[:200].decode('utf-8', 'replace')}")
        audio, usage = bytearray(), {}
        for chunk in re.split(rb"\r?\n", raw):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                msg = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            code = msg.get("code", 0)
            if code in (0, 20000000):
                if msg.get("data"):
                    audio += base64.b64decode(msg["data"])
                usage = msg.get("usage") or usage
                continue
            m = str(msg.get("message", ""))[:200]
            if code in (45000010, 45000030) or "auth" in m.lower() or ("key" in m.lower() and "invalid" in m.lower()):
                raise TtsAuthError(f"鉴权失败 code={code} logid={logid}")
            if 40000000 <= int(code) < 50000000:
                raise TtsBadRequest(f"请求错误 code={code} logid={logid} {m}")
            raise TtsTransientError(f"服务错误 code={code} logid={logid} {m}")
        if not audio:
            raise TtsTransientError(f"未返回音频 logid={logid}")
        return SynthResult(bytes(audio), "mp3", logid, usage, None)


_STRIP = re.compile(r"[\s，,。！？!?；;：:、…“”\"'‘’（）()《》—\-·]")


class FakeTtsClient:
    """确定性替身：时长 = ms_per_char × 有效字数 / 1000（去空白与标点），产出同时长的 PCM WAV（R-03）。
    为使响度归一化（LUFS −16±1）可测，音频为低电平正弦音而非纯静音（PRD 未规定内容，见回报疑问点）。
    fail_plan: {text: [Exception, ...]}，按次序在对应调用时抛出。"""

    _cache = {}

    def __init__(self, ms_per_char: int = 220, fail_plan=None):
        self.ms_per_char = ms_per_char
        self.fail_plan = {k: list(v) for k, v in (fail_plan or {}).items()}
        self.calls = []

    def duration_for(self, text) -> float:
        # max(1, …) 是防御性兜底（架构 v1.7）：空句已由 script_parser 拒绝（empty_line，退出 5），正常流程走不到 0 字。
        return self.ms_per_char * max(1, len(_STRIP.sub("", text))) / 1000.0

    SR = 24000

    def synthesize(self, text, *, speaker="fake", context=(), speech_rate=0):
        self.calls.append(text)
        plan = self.fail_plan.get(text)
        if plan:
            raise plan.pop(0)
        dur = self.duration_for(text)
        return SynthResult(self._wav(dur), "wav", f"fake-{len(self.calls)}", {"text_words": len(text)}, None)

    @classmethod
    def _wav(cls, dur):
        """PCM WAV：24 kHz、单声道、16-bit，样本数 = round(时长×24000)；内容为低电平 220 Hz 正弦音（确定性，R-03）。"""
        n = round(dur * cls.SR)
        if n not in cls._cache:
            import io, math, struct, wave
            amp = int(32767 * 0.25)
            frames = b"".join(struct.pack("<h", int(round(amp * math.sin(2 * math.pi * 220 * i / cls.SR)))) for i in range(n))
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(cls.SR); w.writeframes(frames)
            cls._cache[n] = buf.getvalue()
        return cls._cache[n]
