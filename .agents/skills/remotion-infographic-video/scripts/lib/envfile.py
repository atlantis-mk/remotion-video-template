""".env 解析、Key 校验、Secret 包装与脱敏（架构 §6）。只从技能包根的 .env 读取 Key，不读进程环境变量。"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Optional

from .errors import MissingKeyError

KEY_VAR = "DOUBAO_TTS_API_KEY"
SPEAKER_VAR = "DOUBAO_SPEAKER"
DEFAULT_SPEAKER = "zh_male_m191_uranus_bigtts"


def parse_env(text: str) -> Dict[str, str]:
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        elif " #" in v:
            v = v.split(" #", 1)[0].rstrip()
        if k:
            out[k] = v
    return out


class Secret:
    __slots__ = ("_v",)

    def __init__(self, value: str):
        self._v = value

    def reveal(self) -> str:
        return self._v

    def __repr__(self):
        return "***"

    __str__ = __repr__


@dataclass
class EnvConfig:
    env_path: Path
    key: Secret
    speaker: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict, repr=False)

    def __repr__(self):
        return f"EnvConfig(env_path={str(self.env_path)!r}, key=***, speaker={self.speaker!r})"

    __str__ = __repr__


def env_path_of(skill_dir) -> Path:
    return (Path(skill_dir) / ".env").resolve()


def load_env(skill_dir) -> EnvConfig:
    p = env_path_of(skill_dir)
    if not p.is_file():
        raise MissingKeyError(f"缺少 {p}：请把 .env.example 复制为 .env 并填写 {KEY_VAR}",
                              kind="missing_env", env_path=str(p), var=KEY_VAR)
    vals = parse_env(p.read_text(encoding="utf-8"))
    key = (vals.get(KEY_VAR) or "").strip()
    if not key:
        raise MissingKeyError(f"{p} 中 {KEY_VAR} 为空：请填写后重试",
                              kind="empty_key", env_path=str(p), var=KEY_VAR)
    spk = (vals.get(SPEAKER_VAR) or "").strip() or None
    extra = {k: v for k, v in vals.items() if k not in (KEY_VAR,)}
    return EnvConfig(env_path=p, key=Secret(key), speaker=spk, extra=extra)


from .log import Redactor  # noqa: E402,F401  （兼容旧导入路径）
