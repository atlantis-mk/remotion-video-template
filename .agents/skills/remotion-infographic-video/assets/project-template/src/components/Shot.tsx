import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { EASE, SHOT_BLUR, SHOT_IN } from '../theme/motion';

export type ShotEntranceType = 'push' | 'rise' | 'zoom';
export type ShotProps = { entrance: ShotEntranceType; at: number; children: React.ReactNode; style?: React.CSSProperties };

/** 镜头入场：push（横推）/ rise（上升）/ zoom（缩放），SHOT_IN 帧内模糊→清晰 */
export const Shot: React.FC<ShotProps> = ({ entrance, at, children, style }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const p = interpolate(frame, [at, at + SHOT_IN], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
  const d = (1 - p) * 0.06;
  const transform =
    entrance === 'push' ? `translateX(${d * L.width}px)` : entrance === 'rise' ? `translateY(${d * L.height}px)` : `scale(${1 + d * 2})`;
  return (
    <div style={{ position: 'absolute', inset: 0, opacity: p, transform, filter: p < 1 ? `blur(${(1 - p) * SHOT_BLUR * L.unit}px)` : undefined, ...style }}>
      {children}
    </div>
  );
};
export default Shot;
