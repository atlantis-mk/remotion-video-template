// 段/句帧区间纯函数（架构 v1.6 §7.5，R-04）。不导入 remotion。
// frame 为段内本地帧（<Sequence> 内 useCurrentFrame() 的值）；lines 中 from/to 为全局帧；返回值为段内本地帧。
export type FrameLine = { id: string; section: string; from: number; to: number };
export type Range = { from: number; to: number };

/** 段内本地帧 → 所在句。超出末句时返回末句（末帧属于末句），早于首句返回首句。 */
export function resolveLine<T extends FrameLine>(frame: number, lines: readonly T[], sectionStartFrame: number): T {
  if (lines.length === 0) throw new Error('resolveLine: lines 为空');
  const g = frame + sectionStartFrame;
  for (const l of lines) if (g >= l.from && g < l.to) return l;
  const last = lines[lines.length - 1];
  if (g >= last.to) return last;
  let best = lines[0];
  for (const l of lines) if (l.from <= g) best = l;
  return best;
}

/** 句相对段起点的本地帧区间 */
export function lineLocalRange(id: string, lines: readonly FrameLine[], sectionStartFrame: number): Range {
  const l = lines.find((x) => x.id === id);
  if (!l) throw new Error(`lineLocalRange: 找不到句 ${id}`);
  return { from: l.from - sectionStartFrame, to: l.to - sectionStartFrame };
}

/** 多句合并的本地帧区间（首句 from 到末句 to） */
export function linesLocalRange(ids: readonly string[], lines: readonly FrameLine[], sectionStartFrame: number): Range {
  const rs = ids.map((i) => lineLocalRange(i, lines, sectionStartFrame));
  return { from: Math.min(...rs.map((r) => r.from)), to: Math.max(...rs.map((r) => r.to)) };
}

/** 区间内进度 0..1（夹紧） */
export function progressIn(frame: number, r: Range): number {
  if (r.to <= r.from) return frame >= r.to ? 1 : 0;
  return Math.min(1, Math.max(0, (frame - r.from) / (r.to - r.from)));
}
