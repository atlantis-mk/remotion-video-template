import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { seeded } from '../layers/particles';

export type ImpactShakeProps = { at: number; intensity?: number; children: React.ReactNode };

/** 落地震动：at 起 10 帧内衰减抖动（确定性伪随机） */
export const ImpactShake: React.FC<ImpactShakeProps> = ({ at, intensity = 1, children }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const t = frame - at;
  const amp = t >= 0 && t < 10 ? interpolate(t, [0, 10], [14, 0]) * intensity * L.unit : 0;
  const dx = amp ? (seeded(`shake-x-${t}`) - 0.5) * 2 * amp : 0;
  const dy = amp ? (seeded(`shake-y-${t}`) - 0.5) * 2 * amp : 0;
  return <div style={{ transform: amp ? `translate(${dx}px, ${dy}px)` : undefined, width: '100%' }}>{children}</div>;
};
export default ImpactShake;
