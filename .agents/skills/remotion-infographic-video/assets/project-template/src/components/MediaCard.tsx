import React from 'react';
import { Img, interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { EASE } from '../theme/motion';
import { TOKENS } from '../theme/tokens';
import { SourceBadge } from './SourceBadge';

export type MediaCardProps = { src: string; at: number; tilt?: number; attribution?: string; fit?: 'cover' | 'contain'; aspectRatio?: number };

/** 媒体卡片：perspective 1400 + rotateY/rotateX 倾斜入场；attribution（由 build_timeline 从 manifest 注入）渲染为角标 */
export const MediaCard: React.FC<MediaCardProps> = ({ src, at, tilt = 4, attribution, fit = 'cover', aspectRatio = 16 / 9 }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const p = interpolate(frame, [at, at + 18], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
  const sway = Math.sin((frame - at) / 45) * 0.5;
  const maxW = L.content.w * (L.columns === 2 ? 0.62 : 0.92);
  const maxH = L.content.h * 0.72;
  const w = Math.min(maxW, maxH * aspectRatio);
  return (
    <div style={{ perspective: 1400 * L.unit, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 * L.unit }}>
      <div
        style={{
          width: w, height: w / aspectRatio, borderRadius: TOKENS.radius.lg * L.unit, overflow: 'hidden',
          border: `${Math.max(1, 1.5 * L.unit)}px solid ${TOKENS.glass.border}`, boxShadow: TOKENS.glass.shadow,
          transform: `rotateY(${(1 - p) * -18 + tilt * (0.6 + sway)}deg) rotateX(${tilt * 0.6}deg) scale(${0.92 + p * 0.08})`, opacity: p,
        }}
      >
        <Img src={src} style={{ width: '100%', height: '100%', objectFit: fit, display: 'block' }} />
      </div>
      {attribution ? <SourceBadge text={attribution} /> : null}
    </div>
  );
};
export default MediaCard;
