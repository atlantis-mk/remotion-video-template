"""最小 JSON Schema（2020-12 子集）校验器，仅标准库（架构 A-2）。
支持：type、required、properties、additionalProperties、items、prefixItems、enum、const、pattern、
minLength/maxLength、minimum/maximum/exclusive*、minItems/maxItems、uniqueItems、$ref(#/$defs/...)、allOf/anyOf/oneOf/not。"""
import json, re
from pathlib import Path

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: (isinstance(v, int) and not isinstance(v, bool)) or (isinstance(v, float) and v.is_integer()),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _resolve(root, ref):
    if not ref.startswith("#"):
        raise ValueError(f"不支持外部 $ref：{ref}")
    node = root
    for part in [p for p in ref[1:].split("/") if p]:
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def _v(doc, sch, root, path, errs):
    if sch is True or sch is None:
        return
    if sch is False:
        errs.append(f"{path}: 不允许出现"); return
    if "$ref" in sch:
        _v(doc, _resolve(root, sch["$ref"]), root, path, errs)
    t = sch.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_TYPES[x](doc) for x in ts):
            errs.append(f"{path}: 类型应为 {t}"); return
    if "const" in sch and doc != sch["const"]:
        errs.append(f"{path}: 应为 {sch['const']!r}")
    if "enum" in sch and doc not in sch["enum"]:
        errs.append(f"{path}: {doc!r} 不在 {sch['enum']}")
    if isinstance(doc, str):
        if "pattern" in sch and not re.search(sch["pattern"], doc):
            errs.append(f"{path}: {doc!r} 不匹配 {sch['pattern']}")
        if "minLength" in sch and len(doc) < sch["minLength"]:
            errs.append(f"{path}: 长度 < {sch['minLength']}")
        if "maxLength" in sch and len(doc) > sch["maxLength"]:
            errs.append(f"{path}: 长度 > {sch['maxLength']}")
    if _TYPES["number"](doc):
        if "minimum" in sch and doc < sch["minimum"]: errs.append(f"{path}: < {sch['minimum']}")
        if "maximum" in sch and doc > sch["maximum"]: errs.append(f"{path}: > {sch['maximum']}")
        if "exclusiveMinimum" in sch and doc <= sch["exclusiveMinimum"]: errs.append(f"{path}: ≤ {sch['exclusiveMinimum']}")
        if "exclusiveMaximum" in sch and doc >= sch["exclusiveMaximum"]: errs.append(f"{path}: ≥ {sch['exclusiveMaximum']}")
    if isinstance(doc, list):
        if "minItems" in sch and len(doc) < sch["minItems"]: errs.append(f"{path}: 元素数 < {sch['minItems']}")
        if "maxItems" in sch and len(doc) > sch["maxItems"]: errs.append(f"{path}: 元素数 > {sch['maxItems']}")
        if sch.get("uniqueItems"):
            seen = [json.dumps(x, sort_keys=True) for x in doc]
            if len(set(seen)) != len(seen): errs.append(f"{path}: 元素重复")
        pre = sch.get("prefixItems", [])
        for i, x in enumerate(doc):
            if i < len(pre):
                _v(x, pre[i], root, f"{path}[{i}]", errs)
            elif "items" in sch:
                _v(x, sch["items"], root, f"{path}[{i}]", errs)
    if isinstance(doc, dict):
        for k in sch.get("required", []):
            if k not in doc: errs.append(f"{path}: 缺少必需字段 {k}")
        props = sch.get("properties", {})
        for k, x in doc.items():
            if k in props:
                _v(x, props[k], root, f"{path}.{k}", errs)
            elif "additionalProperties" in sch:
                _v(x, sch["additionalProperties"], root, f"{path}.{k}", errs)
    for s in sch.get("allOf", []):
        _v(doc, s, root, path, errs)
    if "anyOf" in sch and not any(not _collect(doc, s, root, path) for s in sch["anyOf"]):
        errs.append(f"{path}: 不满足 anyOf")
    if "oneOf" in sch and sum(1 for s in sch["oneOf"] if not _collect(doc, s, root, path)) != 1:
        errs.append(f"{path}: 不满足 oneOf")
    if "not" in sch and not _collect(doc, sch["not"], root, path):
        errs.append(f"{path}: 命中 not")


def _collect(doc, sch, root, path):
    e = []; _v(doc, sch, root, path, e); return e


def validate(doc, schema) -> list:
    """返回错误列表，空 = 通过。"""
    return _collect(doc, schema, schema, "$")


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "assets" / "schemas"


def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
