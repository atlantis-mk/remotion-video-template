import React from 'react';
import { Sequence } from 'remotion';
import { Shot } from '../components/Shot';
import { ContentArea } from '../layout/ContentArea';
import type { SectionData, ShotData } from './types';
import { shotRange } from './useLines';

/** 场景写法辅助：把一个镜头放进它自己的时间区间（段内本地帧），套上镜头入场，并限定在内容区内 */
export const ShotSequence: React.FC<{ shot: ShotData | undefined; section: SectionData; children: React.ReactNode; gap?: number }> = ({ shot, section, children, gap = 0 }) => {
  if (!shot) return null;
  const r = shotRange(shot, section);
  return (
    <Sequence from={r.from} durationInFrames={Math.max(1, r.to - r.from)} name={`镜 ${shot.shot_no} ${shot.component}`}>
      <Shot entrance={shot.entrance} at={0}>
        <ContentArea style={{ gap }}>{children}</ContentArea>
      </Shot>
    </Sequence>
  );
};
export default ShotSequence;
