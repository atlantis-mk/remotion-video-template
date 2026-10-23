"""数字归一化与 sources.md 出处比对（F-04、NF-03）。"""
import json, re
from decimal import Decimal, InvalidOperation
from typing import List, Optional

# ---------------- 数字归一化 ----------------
CN_DIGIT = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNIT = {"十": 10, "百": 100, "千": 1000}
BIG = [("亿", Decimal(10) ** 8), ("万", Decimal(10) ** 4)]
CN_CHARS = "零〇一二两三四五六七八九十百千万亿点"


def _cn_small(s: str) -> Decimal:
    """解析 < 1 万的汉字整数（可含阿拉伯数字段）。"""
    if not s:
        return Decimal(0)
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return Decimal(s)
    total, cur = Decimal(0), None
    for ch in s:
        if ch in CN_DIGIT:
            cur = CN_DIGIT[ch]
        elif ch in CN_UNIT:
            total += Decimal(1 if cur is None else cur) * CN_UNIT[ch]
            cur = None
        elif ch.isdigit():
            cur = (cur or 0) * 10 + int(ch)
        else:
            raise ValueError(s)
    if cur is not None:
        total += cur
    return total


def _cn_int(s: str) -> Decimal:
    for ch, mul in BIG:
        if ch in s:
            hi, lo = s.split(ch, 1)
            return (_cn_int(hi) if hi else Decimal(1)) * mul + (_cn_int(lo) if lo else 0)
    return _cn_small(s)


def _cn_number(s: str) -> Decimal:
    if "点" in s:
        ip, fp = s.split("点", 1)
        # 小数部分逐位读
        frac = "".join(str(CN_DIGIT[c]) if c in CN_DIGIT else c for c in fp)
        # 末尾可能带单位（二点五亿）
        unit = Decimal(1)
        for ch, mul in BIG:
            if frac.endswith(ch):
                frac, unit = frac[: -len(ch)], mul
        if not re.fullmatch(r"\d+", frac):
            raise ValueError(s)
        return (_cn_int(ip) + Decimal("0." + frac)) * unit
    return _cn_int(s)


def normalize_number(s: str) -> Optional[Decimal]:
    """归一为 Decimal（百分数按比例值，30% → 0.3）；无法识别返回 None。"一千五百亿"、"1500亿"、"1,500 亿元" 相等。"""
    if s is None:
        return None
    t = re.sub(r"[\s,，_]", "", str(s))
    pct = False
    if t.startswith("百分之"):
        pct, t = True, t[3:]
    if t.endswith("%") or t.endswith("％"):
        pct, t = True, t[:-1]
    t = re.sub(r"(元|美元|人民币|块|个|倍|种|次|秒|分钟|年|月|日|天|步|家|名|条|段|句|帧|像素)$", "", t)
    if not t:
        return None
    try:
        m = re.fullmatch(r"(\d+(?:\.\d+)?)(万亿|亿|万|千|百)?", t)
        if m:
            v = Decimal(m.group(1))
            mul = {"万亿": Decimal(10) ** 12, "亿": Decimal(10) ** 8, "万": Decimal(10) ** 4,
                   "千": Decimal(1000), "百": Decimal(100), None: Decimal(1)}[m.group(2)]
            v = v * mul
        elif all(c in CN_CHARS or c.isdigit() or c == "." for c in t):
            v = _cn_number(t.replace(".", "点"))
        else:
            return None
    except (ValueError, InvalidOperation, KeyError):
        return None
    if pct:
        v = v / 100
    return v.normalize()


# 句中数字抽取（validate sources 使用）
_NUM_TOKEN = re.compile(r"(百分之[零〇一二两三四五六七八九十百千点]+|[0-9][0-9,，.]*\s*(?:万亿|亿|万)?\s*%?|[零〇一二两三四五六七八九十百千万亿点]+%?)")
# 非数量的常用词（含数字汉字但不是数据）
NON_NUMERIC = ("一点都", "一点也", "一起", "一下", "一直", "一定", "一样", "统一", "唯一", "一切", "万一", "一些", "一旦",
               "一般", "一边", "一面", "一致", "一口气", "一句", "一眼", "第一", "之一", "一条龙", "千万别", "一千零一", "一键",
               "一遍", "一次性", "逐一", "一步步", "一个个", "一张", "第三方", "同一", "一声")


def extract_numbers(text: str) -> List[str]:
    t = text
    for w in NON_NUMERIC:
        t = t.replace(w, " " * len(w))
    out = []
    for m in _NUM_TOKEN.finditer(t):
        tok = m.group(0).strip()
        if not tok or tok == "点" or set(tok) <= set("点.,，"):
            continue
        tok = tok.strip("点.,，")
        if normalize_number(tok) is not None:
            out.append(tok)
    return out



def parse_sources_md(text: str):
    blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.S)
    if not blocks:
        raise ValueError("sources.md 末尾缺少 ```json 结构化来源块")
    data = json.loads(blocks[-1])
    if isinstance(data, dict):
        data = data.get("sources", [])
    if not isinstance(data, list):
        raise ValueError("sources json 必须是数组")
    return data


def check_sources(lines, sources):
    """返回错误列表：稿中每个数字都须在同句（line_id）或全局的来源条目中找到。"""
    errs = []
    by_line = {}
    for s in sources:
        vals = {normalize_number(s.get("value_spoken", "")), normalize_number(s.get("value_display", ""))} - {None}
        if not s.get("url"):
            errs.append(f"来源 {s.get('claim_id')} 缺 url")
        by_line.setdefault(s.get("line_id"), set()).update(vals)
    for l in lines:
        for tok in extract_numbers(l["text"]):
            v = normalize_number(tok)
            if v not in by_line.get(l["id"], set()):
                errs.append(f"句 [{l['id']}] 的数字「{tok}」在 sources 中没有对应来源")
    return errs
