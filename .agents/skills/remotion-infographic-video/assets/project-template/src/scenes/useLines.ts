// 场景内取句/镜区间的 hook 包装；纯函数在 ../timing/lines.ts。返回的帧均为段内本地帧。
import { useCurrentFrame } from 'remotion';
import { LINES, type SectionData, type ShotData } from '../data/timeline';
import { lineLocalRange, linesLocalRange, resolveLine, type Range } from '../timing/lines';

export const useLines = (section: Pick<SectionData, 'id' | 'from'>, ids?: readonly string[]) => {
  const frame = useCurrentFrame();
  const own = LINES.filter((l) => l.section === section.id);
  const pool = own.length ? own : LINES;
  const want = ids ?? pool.map((l) => l.id);
  const ranges: Record<string, Range> = {};
  for (const id of want) if (LINES.some((l) => l.id === id)) ranges[id] = lineLocalRange(id, LINES, section.from);
  return {
    frame,
    current: pool.length ? resolveLine(frame, pool, section.from) : undefined,
    ranges,
    range: (id: string): Range => ranges[id] ?? lineLocalRange(id, LINES, section.from),
  };
};

/** 镜头相对段起点的本地帧区间 */
export const shotRange = (shot: Pick<ShotData, 'from' | 'to'>, section: Pick<SectionData, 'from'>): Range => ({ from: shot.from - section.from, to: shot.to - section.from });

/** 多句的本地帧区间 */
export const rangeOf = (ids: readonly string[], section: Pick<SectionData, 'from'>): Range => linesLocalRange(ids, LINES, section.from);

/** 按 shot_no 取镜头 */
export const shotByNo = (shots: readonly ShotData[], no: number): ShotData | undefined => shots.find((s) => s.shot_no === no);
