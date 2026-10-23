"""storyboard 校验（F-07）：Schema + 句覆盖 + 段顺序 + 组件清单 + 素材可用。"""
from . import schema_check

COMPONENTS = ["GlassPanel", "Split", "Shot", "SectionTransition", "SlamTitle", "ImpactShake", "KeywordPulse", "StepList",
              "NumberRoll", "CompareBars", "SourceBadge", "IllustrativeTag", "MediaCard", "FollowCTA", "HoldFade"]


def check_storyboard(sb, timeline=None, manifest=None, sources=None, components=COMPONENTS):
    errs = schema_check.validate(sb, schema_check.load_schema("storyboard.schema.json"))
    if errs:
        return errs
    shots = [sh for s in sb["sections"] for sh in s["shots"]]
    nos = [sh["shot_no"] for sh in shots]
    if nos != sorted(nos) or len(set(nos)) != len(nos):
        errs.append("shot_no 必须全局递增且唯一")
    for sh in shots:
        if components and sh["component"] not in components:
            errs.append(f"镜 {sh['shot_no']} 组件 {sh['component']} 不在组件清单中")
    if timeline is not None:
        tl_ids = [l["id"] for l in timeline.get("lines", [])]
        covered = {i for sh in shots for i in sh["line_ids"]}
        for i in tl_ids:
            if i not in covered:
                errs.append(f"句 {i} 未被任何镜覆盖")
        for i in covered - set(tl_ids):
            errs.append(f"镜引用了不存在的句 {i}")
        sec_of = {l["id"]: l.get("section") for l in timeline.get("lines", [])}
        order = [s["id"] for s in sb["sections"]]
        tl_order = list(dict.fromkeys(sec_of[i] for i in tl_ids))
        if [x for x in order if x in tl_order] != tl_order:
            errs.append(f"段顺序 {order} 与稿件段顺序 {tl_order} 不一致")
        for s in sb["sections"]:
            for sh in s["shots"]:
                for i in sh["line_ids"]:
                    if i in sec_of and sec_of[i] != s["id"]:
                        errs.append(f"镜 {sh['shot_no']} 的句 {i} 属于 {sec_of[i]}，不在段 {s['id']}")
    if manifest is not None:
        ok = {a["id"] for a in manifest if a.get("usable")}
        for sh in shots:
            for aid in sh.get("asset_ids") or []:
                if aid not in ok:
                    errs.append(f"镜 {sh['shot_no']} 引用素材 {aid} 不在 manifest 或不可用")
    if sources is not None:
        cids = {s.get("claim_id") for s in sources}
        for sh in shots:
            for d in sh.get("display_numbers") or []:
                if d["source_claim_id"] not in cids:
                    errs.append(f"镜 {sh['shot_no']} 上屏数字 {d['text']} 的来源 {d['source_claim_id']} 不存在")
    return errs
