"""画幅判定（F-10，v1.3 U-1）：只认“横屏/竖屏”两个词，平台名不参与；两个词都出现时取最后出现的那个（A-23）。
关键词表的唯一来源是 references/LAYOUT.md 中的机读 JSON 块。"""
import json, re
from pathlib import Path

PRESETS = {"landscape": (1920, 1080), "portrait": (1080, 1440)}   # 16:9 / 3:4（v1.3）
PLATFORM_IDS = ["douyin", "bilibili", "xiaohongshu", "channels", "youtube"]


def load_layout_keywords(skill_dir=None):
    p = Path(skill_dir or Path(__file__).resolve().parents[2]) / "references" / "LAYOUT.md"
    for m in re.finditer(r"```json\s*\n(.*?)```", p.read_text(encoding="utf-8"), re.S):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and "portrait_keywords" in d:
            return {"portrait": d["portrait_keywords"], "landscape": d.get("landscape_keywords", [])}
    raise ValueError(f"{p} 中没有含 portrait_keywords 的 JSON 块")


def resolve_aspect(topic: str, kw=None) -> str:
    """kw = {"portrait": ["竖屏"], "landscape": ["横屏"]}；未提及 → landscape。"""
    if kw is None:
        kw = load_layout_keywords()
    if isinstance(kw, dict):
        por = kw.get("portrait") or kw.get("portrait_keywords") or []
        lan = kw.get("landscape") or kw.get("landscape_keywords") or []
    else:
        por, lan = list(kw), []
    t = (topic or "").lower()
    best, pos = "landscape", -1
    for words, a in ((por, "portrait"), (lan, "landscape")):
        for w in words:
            i = t.rfind(w.lower())
            if i > pos:
                best, pos = a, i
    return best


def normalize_job(job: dict) -> dict:
    """补默认画幅（缺 aspect → landscape）并按预设写入 width/height、fps。"""
    j = dict(job)
    a = j.get("aspect") or "landscape"
    if a not in PRESETS:
        raise ValueError(f"aspect 非法：{a}")
    j["aspect"] = a
    j["width"], j["height"] = PRESETS[a]
    j["fps"] = int(j.get("fps") or 30)
    return j
